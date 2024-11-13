import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Función para manejar confirmaciones automáticas
def handle_confirmation(driver):
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert.accept()
        print("Confirmación aceptada automáticamente.")
    except:
        pass  # Continuar normalmente si no hay confirmación

# Función para crear una carpeta remota
def create_remote_folder(driver, folder_name):
    try:
        # Verificar si la carpeta ya existe
        existing_folder = driver.find_elements(By.LINK_TEXT, folder_name)
        if existing_folder:
            print(f"Carpeta '{folder_name}' ya existe. Saltando creación.")
            return

        print(f"Creando carpeta: {folder_name}")
        folder_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "nombre_carpeta"))
        )
        folder_input.clear()
        folder_input.send_keys(folder_name)

        create_button = driver.find_element(By.CSS_SELECTOR, "a.btn-success")
        create_button.click()
        handle_confirmation(driver)

        # Esperar a que la carpeta sea creada
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.LINK_TEXT, folder_name))
        )
        print(f"Carpeta '{folder_name}' creada exitosamente.")
    except Exception as e:
        print(f"Error al crear la carpeta '{folder_name}': {e}")

# Función para subir un archivo con reintentos
def retry_upload(driver, file_path, retries=5):
    for attempt in range(retries):
        print(f"Intentando subir {file_path} (Intento {attempt + 1}/{retries})")
        result = upload_file(driver, file_path)
        if not result["error"]:
            return result
    print(f"Error: No se pudo subir el archivo {file_path} después de {retries} intentos.")
    return {"file_name": os.path.basename(file_path), "path": file_path, "error": True}

# Función para subir un archivo
def upload_file(driver, file_path):
    try:
        print(f"Subiendo archivo: {file_path}")
        file_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(file_path)

        # Esperar a que se complete la subida
        error_files = wait_for_all_uploads(driver)
        file_name = os.path.basename(file_path)
        if file_name in error_files:
            print(f"Archivo '{file_name}' no se pudo subir correctamente.")
            return {"file_name": file_name, "path": file_path, "error": True}

        print(f"Archivo '{file_name}' subido exitosamente.")
        return {"file_name": file_name, "path": file_path, "error": False}
    except Exception as e:
        print(f"Error al subir el archivo '{file_path}': {e}")
        return {"file_name": os.path.basename(file_path), "path": file_path, "error": True}

# Función para esperar a que se completen todas las subidas
def wait_for_all_uploads(driver, max_wait=600):
    print("Esperando a que se completen todas las subidas...")
    start_time = time.time()
    error_files = []

    while True:
        pending_uploads = driver.find_elements(By.CSS_SELECTOR, ".dz-preview:not(.dz-success):not(.dz-error)")
        error_uploads = driver.find_elements(By.CSS_SELECTOR, ".dz-error")

        # Registrar errores
        for error in error_uploads:
            try:
                file_name = error.find_element(By.CSS_SELECTOR, ".dz-filename span").text
                if file_name not in error_files:
                    print(f"Error al subir archivo: {file_name}")
                    error_files.append(file_name)
            except Exception as e:
                print(f"Error al obtener el nombre del archivo fallido: {e}")

        if not pending_uploads:
            print("Todas las subidas se han completado (o han fallado).")
            return error_files

        if time.time() - start_time > max_wait:
            print("Tiempo de espera agotado.")
            break

        time.sleep(5)

    return error_files

# Función para replicar la estructura de carpetas local
def replicate_structure(driver, local_path):
    def add_to_tree(tree, path_parts, file_data):
        current_level = tree
        for part in path_parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        if "files" not in current_level:
            current_level["files"] = []
        current_level["files"].extend(file_data)

    tree = {}
    for root, dirs, files in os.walk(local_path):
        relative_path = os.path.relpath(root, local_path).replace("\\", "/")
        path_parts = relative_path.split("/") if relative_path != "." else []

        for part in path_parts:
            create_remote_folder(driver, part)
            folder_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, part))
            )
            folder_link.click()

        file_data = []
        for file in files:
            file_path = os.path.join(root, file)
            file_result = retry_upload(driver, file_path)
            file_data.append(file_result)

        add_to_tree(tree, path_parts, file_data)

        for _ in range(len(path_parts)):
            driver.back()

    return tree

# Configuración del WebDriver
service = Service("C:/Users/josev/Escritorio/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://repositoriot.inah.gob.mx/arrastrar/index.php")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "correo")))
    driver.find_element(By.NAME, "correo").send_keys("al049738@uacam.mx")
    driver.find_element(By.NAME, "contrasenia").send_keys("DSA22093")
    driver.find_element(By.NAME, "iniciar").click()

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "file_upload")))
    print("Inicio de sesión exitoso")

    folder_root = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.LINK_TEXT, "ARQUITECTURA")))
    folder_root.click()

    folio_hdd = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.LINK_TEXT, "ARQ-01")))
    folio_hdd.click()

    local_path = "C:/Users/josev/Escritorio/Tramo 7/Prospección/2022"
    tree_structure = replicate_structure(driver, local_path)

    with open("resultado_subida.json", "w", encoding="utf-8") as json_file:
        json.dump(tree_structure, json_file, ensure_ascii=False, indent=4)
    print("Estructura replicada exitosamente en resultado_subida.json")
finally:
    driver.quit()
