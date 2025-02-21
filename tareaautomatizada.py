import os
import time
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuración del bot de Telegram
TELEGRAM_BOT_TOKEN = "7922512452:AAGhfzYMzhJPfV1TA1dBy2w6hICCIXHdNds"
TELEGRAM_CHAT_ID = "5540982553"

def enviar_mensaje_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    datos = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        requests.post(url, data=datos)
        print("📩 Mensaje enviado a Telegram")
    except Exception as e:
        print(f"⚠️ Error enviando mensaje a Telegram: {e}")

# Verificar si Chrome está instalado en el VPS
def instalar_chrome():
    try:
        subprocess.run(["google-chrome", "--version"], check=True)
        print("✅ Google Chrome ya está instalado.")
    except subprocess.CalledProcessError:
        print("⚠️ Google Chrome no encontrado. Instalando...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "google-chrome-stable"], check=True)
        print("✅ Google Chrome instalado.")

# Instalar Chrome si no está disponible
instalar_chrome()

# Obtener la ruta donde está corriendo el script
ruta_script = os.path.dirname(os.path.abspath(__file__))

# Crear la carpeta 'excel' si no existe
download_dir = os.path.join(ruta_script, "excel")
os.makedirs(download_dir, exist_ok=True)

# Configurar Chrome en modo headless
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Modo headless optimizado
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-software-rasterizer")  # Previene errores gráficos en VPS
chrome_options.add_argument("--remote-debugging-port=0")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Configuración de descargas
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Descargar e instalar automáticamente ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1. Ir a la página de login
    driver.get("https://cybernovasystems.com/prueba/sistema_tlc/login.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

    # 2. Ingresar usuario y contraseña
    driver.find_element(By.NAME, "email").send_keys("nina@sistema.com")
    driver.find_element(By.NAME, "password").send_keys("1", Keys.RETURN)

    # 3. Esperar la redirección
    WebDriverWait(driver, 10).until(EC.url_contains("modulo"))

    # 4. Ir a la página del módulo Trabajos
    driver.get("https://cybernovasystems.com/prueba/sistema_tlc/vista/modulo.php?modulo=Trabajos")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "exportarExcel")))

    # 5. Descargar el archivo Excel
    driver.find_element(By.ID, "exportarExcel").click()
    time.sleep(10)  # Esperar la descarga

    # 6. Verificar si el archivo se descargó en la carpeta "excel"
    archivos = os.listdir(download_dir)
    archivo_descargado = None
    for archivo in archivos:
        if archivo.endswith(".xls") or archivo.endswith(".xlsx"):
            archivo_descargado = os.path.join(download_dir, archivo)
            break

    if archivo_descargado:
        mensaje = f"✅ Descarga completada.\nArchivo: {archivo_descargado}"
        enviar_mensaje_telegram(mensaje)
    else:
        enviar_mensaje_telegram("⚠️ No se encontró el archivo Excel después de la descarga.")

except Exception as e:
    mensaje_error = f"❌ Error en el script:\n{str(e)}"
    enviar_mensaje_telegram(mensaje_error)

finally:
    driver.quit()
