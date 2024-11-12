import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Función para esperar confirmación automática
def handle_confirmation(driver):
    try:
        alert = WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert.accept()  # Automáticamente selecciona "Sí"
        print("Confirmación aceptada automáticamente.")
    except:
        pass  # Si no hay confirmación, continuar normalmente


# Función para crear una carpeta remota
def create_remote_folder(driver, folder_name):
    try:
        print(f"Creando carpeta: {folder_name}")
        folder_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nombre_carpeta"))
        )
        folder_input.clear()
        folder_input.send_keys(folder_name)

        create_button = driver.find_element(By.CSS_SELECTOR, "a.btn-success")
        create_button.click()

        handle_confirmation(driver)

        # Esperar a que la carpeta sea creada
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, folder_name))
        )
        print(f"Carpeta '{folder_name}' creada exitosamente.")
    except Exception as e:
        print(f"Error al crear la carpeta '{folder_name}': {e}")


# Función para subir un archivo a la carpeta actual
def upload_file(driver, file_path):
    try:
        print(f"Subiendo archivo: {file_path}")
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(file_path)

        # Esperar a que la subida se complete
        wait_for_all_uploads(driver)
        print(f"Archivo '{file_path}' subido exitosamente.")
    except Exception as e:
        print(f"Error al subir el archivo '{file_path}': {e}")


# Función para esperar a que todas las subidas se completen
def wait_for_all_uploads(driver, max_wait=3600):
    print("Esperando a que se completen todas las subidas...")
    start_time = time.time()

    while True:
        pending_uploads = driver.find_elements(By.CSS_SELECTOR, ".dz-preview:not(.dz-success)")
        if not pending_uploads:
            print("Todas las subidas se han completado.")
            return True

        for pending in pending_uploads:
            file_name = pending.find_element(By.CSS_SELECTOR, ".dz-filename span").text
            progress = pending.find_element(By.CSS_SELECTOR, ".dz-progress span").get_attribute("style")
            print(f"Archivo pendiente: {file_name}, progreso: {progress}")

        if time.time() - start_time > max_wait:
            print("Archivos que no se subieron:")
            for pending in pending_uploads:
                file_name = pending.find_element(By.CSS_SELECTOR, ".dz-filename span").text
                print(f"  - {file_name}")
            raise TimeoutError("Se agotó el tiempo de espera. Algunos archivos no se subieron correctamente.")

        time.sleep(5)


# Función principal para replicar estructura
def replicate_structure(driver, local_path):
    for root, dirs, files in os.walk(local_path):
        relative_path = os.path.relpath(root, local_path)
        if relative_path == ".":
            continue  # Saltar la raíz (carpeta base)

        # Crear carpeta remota
        create_remote_folder(driver, relative_path)

        # Acceder a la carpeta creada
        folder_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, relative_path))
        )
        folder_link.click()

        # Subir archivos en la carpeta
        for file in files:
            file_path = os.path.join(root, file)
            upload_file(driver, file_path)

        # Volver al nivel anterior
        driver.back()


# Configuración del WebDriver
service = Service("C:/Users/josev/Escritorio/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    # Inicio de sesión
    driver.get("https://repositoriot.inah.gob.mx/arrastrar/index.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "correo")))
    driver.find_element(By.NAME, "correo").send_keys("al049738@uacam.mx")
    driver.find_element(By.NAME, "contrasenia").send_keys("DSA22093")
    driver.find_element(By.NAME, "iniciar").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file_upload")))
    print("Inicio de sesión exitoso")

    # Navegar a la carpeta de destino
    folder_root = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "ARQUITECTURA")))
    folder_root.click()

    folio_hdd = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "ARQ-01")))
    folio_hdd.click()

    # Replicar estructura local
    local_path = "C:/Users/josev/Documentos/PRC-02/Tramo 7/Prospección/2024"
    replicate_structure(driver, local_path)

    print("Estructura replicada exitosamente")

finally:
    driver.quit()
