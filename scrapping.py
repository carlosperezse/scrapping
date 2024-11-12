import os
import mimetypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to detect all files in a folder and determine MIME types
def get_all_files_with_mime_types(folder_path):
    files_with_mime_types = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(full_path)  # Guess MIME type based on file extension
            files_with_mime_types.append((full_path, mime_type or "application/octet-stream"))
    return files_with_mime_types

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

    # Step 6: Wait for the main page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "file_upload"))
    )
    print("Login successful!")

    # Step 7: Navigate to the "ARQUITECTURA" directory
    procesamiento_folder = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "ARQUITECTURA"))
    )
    procesamiento_folder.click()

    # Step 8: Navigate to the "ARQ-01" subdirectory
    prc02_folder = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "ARQ-01"))
    )
    prc02_folder.click()

    # Step 9: Wait for the Dropzone form in the "PRC-02" folder
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "file_upload"))
    )
    print("Navigated to PRC-02 folder!")

    # Step 10: Detect all files and their MIME types
    folder_path = "D:/Documentos/Wondershare"  # Replace with your folder path
    all_files_with_mime_types = get_all_files_with_mime_types(folder_path)
    print(f"Files to upload: {all_files_with_mime_types}")

    # Step 11: Use JavaScript to simulate file uploads using Dropzone.js
    dropzone_script = """
    const dropzone = Dropzone.instances[0]; // Get the Dropzone instance
    const files = arguments[0];  // Array of files with paths and MIME types
    files.forEach(file => {
        const filePath = file[0];
        const mimeType = file[1];
        const fileName = filePath.split(/(\\|\/)/g).pop(); // Extract file name
        const fileObject = new File([''], fileName, { type: mimeType });
        dropzone.addFile(fileObject); // Add file to Dropzone
    });
    """
    driver.execute_script(dropzone_script, all_files_with_mime_types)

    # Step 12: Wait for upload completion
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dz-success"))  # Replace with actual success indicator
    )
    print("All files uploaded successfully to PRC-02!")

finally:
    # Step 13: Close the browser
    driver.quit()
