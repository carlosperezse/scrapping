from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Path to the ChromeDriver
service = Service("C:/Users/JOSE/Desktop/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    # Step 1: Open the Login Page
    driver.get("https://repositoriot.inah.gob.mx/arrastrar/index.php")

    # Step 2: Wait for the login form to appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "correo"))
    )

    # Step 3: Enter username
    username_field = driver.find_element(By.NAME, "correo")
    username_field.send_keys("al049738@uacam.mx")

    # Step 4: Enter password
    password_field = driver.find_element(By.NAME, "contrasenia")
    password_field.send_keys("DSA22093")

    # Step 5: Click the login button
    login_button = driver.find_element(By.NAME, "iniciar")
    login_button.click()

    # Step 6: Wait for the Dropzone form to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "file_upload"))
    )
    print("Login successful!")

    # Step 7: Use Dropzone's JavaScript API to upload a file
    file_path = "C:/Users/JOSE/Desktop/boveda_script_report.log"  # Replace with your file path
    dropzone_script = """
    let myDropzone = Dropzone.instances[0]; // Assuming the Dropzone is initialized
    let file = new File([''], arguments[0], { type: 'text/plain' }); // Adjust file type if needed
    myDropzone.addFile(file); // Add file to Dropzone queue
    """
    driver.execute_script(dropzone_script, file_path)

    # Step 8: Wait for the upload to complete (use Dropzone events)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dz-success"))  # Replace with actual success indicator class
    )
    print("File uploaded successfully using Dropzone.js API!")

finally:
    # Step 10: Close the browser
    driver.quit()
