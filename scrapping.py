import os
import mimetypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Función para recorrer la estructura de carpetas y archivos
def get_directory_structure(rootdir):
    """
    Recoge la estructura de directorios y archivos.
    Devuelve un diccionario con carpetas como claves y listas de archivos como valores.
    """
    directory_structure = {}
    for root, dirs, files in os.walk(rootdir):
        relative_path = os.path.relpath(root, rootdir)
        directory_structure[relative_path] = files
    return directory_structure

# Configuración del WebDriver
service = Service("C:/Users/JOSE/Desktop/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    # Paso 1: Abrir la página de inicio de sesión
    driver.get("https://repositoriot.inah.gob.mx/arrastrar/index.php")

    # Paso 2: Iniciar sesión
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "correo"))
    )
    driver.find_element(By.NAME, "correo").send_keys("al049738@uacam.mx")
    driver.find_element(By.NAME, "contrasenia").send_keys("DSA22093")
    driver.find_element(By.NAME, "iniciar").click()

    # Paso 3: Esperar a que cargue la página principal
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "file_upload"))
    )
    print("Inicio de sesión exitoso")
    
    
    procesamiento_folder = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "ARQUITECTURA"))
    )
    procesamiento_folder.click()

    prc02_folder = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "ARQ-01"))
    )
    prc02_folder.click()

    # Paso 4: Recorrer la estructura local de carpetas
    local_root = "D:/Documentos/Wondershare"  # Ruta local
    directory_structure = get_directory_structure(local_root)
    print("Estructura de carpetas detectada:", directory_structure)

    # Paso 5: Crear carpetas y subir archivos
    for folder, files in directory_structure.items():
        # Crear carpeta en el servidor
        if folder != ".":
            folder_name = os.path.basename(folder)
            print(f"Creando carpeta en el servidor: {folder_name}")
            driver.execute_script(
                """
                var folderName = arguments[0];
                var action = document.getElementById('accion').value;
                $.ajax({
                    type: "POST",
                    url: "file_upload.php",
                    data: { accion: action, nombre_carpeta: folderName },
                    success: function(response) {
                        console.log("Carpeta creada:", folderName);
                    }
                });
                """,
                folder_name
            )
            WebDriverWait(driver, 5).until(lambda d: True)  # Pausa breve para la creación

        # Subir archivos en la carpeta
        for file in files:
            file_path = os.path.join(local_root, folder, file)
            mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            print(f"Subiendo archivo: {file} a la carpeta: {folder}")

            # Simular la carga de archivos en Dropzone.js
            dropzone_script = """
            const dropzone = Dropzone.instances[0];
            const fileName = arguments[0];
            const filePath = arguments[1];
            const mimeType = arguments[2];
            const fileObject = new File([''], fileName, { type: mimeType });
            dropzone.addFile(fileObject);
            console.log(`Archivo cargado: ${fileName}`);
            """
            driver.execute_script(dropzone_script, file, file_path, mime_type)
            WebDriverWait(driver, 2).until(lambda d: True)  # Pausa breve para la carga

    print("Carga de carpetas y archivos completada")

finally:
    # Paso final: Cerrar el navegador
    driver.quit()
