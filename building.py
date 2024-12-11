#INICIO_legacy

import os
import time
import sys
import json
from pathlib import Path
from selenium import webdriver
from urllib.parse import unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

DRIVER_ROOT = 'C:/Users/ADMIN/Desktop/chromedriver-win64/chromedriver.exe'
CORREO = 'cipp98@gmail.com'
CONTRASENIA = 'DSA22359'

#FIN_legacy


def get_tree(driver):
    driver.find_element(By.CSS_SELECTOR, "a[href='arbol.php']").click()

    time.sleep(10)



#INICIO_legacy

# Configuración del WebDriver
service = Service(DRIVER_ROOT)
driver = webdriver.Chrome(service=service)

try:
    
    # Inicio de sesión
    driver.get("https://repositoriot.inah.gob.mx/arrastrar/index.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "correo")))
    driver.find_element(By.NAME, "correo").send_keys(CORREO)
    driver.find_element(By.NAME, "contrasenia").send_keys(CONTRASENIA)
    driver.find_element(By.NAME, "iniciar").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file_upload")))
    print("Inicio de sesión exitoso")

#FIN_legacy

    get_tree(driver)

#legacy
finally:
    driver.quit()
#legacy