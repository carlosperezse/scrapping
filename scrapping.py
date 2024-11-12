import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Función para recorrer la estructura de carpetas y archivos
def get_directory_structure(rootdir):
    directory_structure = {}
    for root, dirs, files in os.walk(rootdir):
        relative_path = os.path.relpath(root, rootdir)
        directory_structure[relative_path] = files
    return directory_structure


# Función para esperar a que todas las subidas se completen
def wait_for_all_uploads(driver, max_wait=3600):
    print("Esperando a que se completen todas las subidas...")
    start_time = time.time()

    while True:
        # Verificar si todavía hay archivos pendientes
        pending_uploads = driver.find_elements(By.CSS_SELECTOR, ".dz-preview:not(.dz-success)")
        if not pending_uploads:
            print("Todas las subidas se han completado.")
            return True

        # Mostrar los archivos que siguen pendientes
        for pending in pending_uploads:
            file_name = pending.find_element(By.CSS_SELECTOR, ".dz-filename span").text
            progress = pending.find_element(By.CSS_SELECTOR, ".dz-progress span").get_attribute("style")
            print(f"Archivo pendiente: {file_name}, progreso: {progress}")

        # Salir si el tiempo excede el límite
        if time.time() - start_time > max_wait:
            print("Archivos que no se subieron:")
            for pending in pending_uploads:
                file_name = pending.find_element(By.CSS_SELECTOR, ".dz-filename span").text
                print(f"  - {file_name}")
            raise TimeoutError("Se agotó el tiempo de espera. Algunos archivos no se subieron correctamente.")

        time.sleep(5)  # Espera breve antes de volver a verificar


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

    # Subida de archivos
    local_root = "C:/Users/josev/Documentos/PRC-02/Tramo 7/Prospección/2024"
    directory_structure = get_directory_structure(local_root)
    print("Estructura de carpetas detectada:", directory_structure)

    for folder, files in directory_structure.items():
        for file in files:
            file_path = os.path.join(local_root, folder, file)
            print(f"Subiendo archivo: {file} a la carpeta: {folder}")

            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(file_path)

    # Esperar a que todas las subidas se completen
    wait_for_all_uploads(driver)

    print("Carga de carpetas y archivos completada")

finally:
    driver.quit()
