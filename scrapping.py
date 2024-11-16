import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración inicial
DRIVER_ROOT = 'C:/Users/josev/Escritorio/chromedriver-win64/chromedriver.exe'
CORREO = 'al049738@uacam.mx'
CONTRASENIA = 'DSA22093'
DIRECTORIO_URL = 'https://repositoriot.inah.gob.mx/arrastrar/index.php?path=uploads/PROCESAMIENTO/PRC-03/1M3120970209/FRENTE_1/*'

# Configuración del WebDriver
service = Service(DRIVER_ROOT)
driver = webdriver.Chrome(service=service)

try:
    # Iniciar sesión
    driver.get("https://repositoriot.inah.gob.mx/arrastrar/index.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "correo")))
    driver.find_element(By.NAME, "correo").send_keys(CORREO)
    driver.find_element(By.NAME, "contrasenia").send_keys(CONTRASENIA)
    driver.find_element(By.NAME, "iniciar").click()

    # Esperar inicio de sesión y navegar al directorio
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file_upload")))
    driver.get(DIRECTORIO_URL)

    # Esperar a que se carguen todos los archivos en la página
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "group")))
    print(f"Navegación al directorio {DIRECTORIO_URL} exitosa y archivos cargados")

    # Eliminar archivos que cumplan las condiciones
    while True:
        try:
            # Buscar todos los elementos nuevamente en cada iteración
            archivos = driver.find_elements(By.CLASS_NAME, "group")
            if not archivos:
                print("No hay más archivos para procesar.")
                break

            # Procesar cada archivo
            for archivo in archivos:
                try:
                    # Obtener el botón de eliminar y el atributo 'onclick'
                    eliminar_boton = archivo.find_element(By.CLASS_NAME, "btn-danger")
                    onclick_atributo = eliminar_boton.get_attribute("onclick")

                    # Extraer la URL del archivo desde el atributo 'onclick'
                    if "confirmar_archivo" in onclick_atributo:
                        url_archivo = onclick_atributo.split('"')[1]  # Extraer la URL entre comillas
                        print(f"Eliminando archivo: {url_archivo}")

                        # Hacer clic en el botón de eliminar
                        eliminar_boton.click()

                        # Confirmar eliminación con el modal de SweetAlert2
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "swal2-confirm"))).click()

                        # Esperar a que la acción se complete
                        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "swal2-popup")))
                        break  # Salir del bucle interno para volver a buscar los elementos
                except Exception as e:
                    print(f"Error al procesar un archivo: {e}")

        except Exception as e:
            print(f"Error general al buscar archivos: {e}")
            break

finally:
    driver.quit()
