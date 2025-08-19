import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===============================
# CREDENCIAIS FIXAS
# ===============================
email = "komest.contact@gmail.com"  # Substitua pelo seu email
senha = "926759058#Komest"        # Substitua pela sua senha

options = uc.ChromeOptions()
# options.add_argument("--disable-extensions")
# options.add_argument("--no-sandbox")
# options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)

# Cria espera explícita
wait = WebDriverWait(driver, 15)

# LOGIN NO SITE
driver.get("https://www.workana.com/login")

print("Aguardando botão de cookies aparecer...")
try:
    # Espera e clica no botão de aceitar cookies
    cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
    cookie_button.click()
    print("Cookies aceitos!")
except Exception as e:
    print("Aviso: Botão de cookies não encontrado ou já aceito anteriormente")

print("Aguardando 10 segundos antes de fazer login...")
for i in range(10, 0, -1):
    print(f"Aguardando... {i} segundos")
    time.sleep(1)

# Espera campos de email e senha carregarem
email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input")))
senha_input = wait.until(EC.presence_of_element_located((By.ID, "password-input")))

# Preenche login
email_input.send_keys(email)
senha_input.send_keys(senha)

# Clica no botão de login
login_button = wait.until(EC.element_to_be_clickable((By.NAME, "submit")))
login_button.click()

# Aguarda redirecionamento ou algum elemento que indique login concluído
time.sleep(5)  # Ajuste se precisar de mais tempo

print("Login realizado com sucesso!")

# Encerra o driver
driver.quit()
print("Driver encerrado.")
