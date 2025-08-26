import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# EMAIL E SENHA FIXOS
email = "komest.contact@gmail.com"
senha = "926759058#Komest"

# CONFIGURAÇÃO DO CHROME
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)

# Garante que a janela tenha tamanho fixo
driver.set_window_size(1200, 800)

# Cria espera explícita
wait = WebDriverWait(driver, 20)

try:
    # LOGIN NO SITE
    driver.get("https://www.workana.com/login")
    time.sleep(5)  # espera extra para carregar

    # Fecha banner de cookies (se existir)
    try:
        botao_cookies = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        botao_cookies.click()
        print("Banner de cookies fechado.")
    except:
        print("Nenhum banner de cookies encontrado ou já fechado.")

    # Preenche campos de login
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input")))
    senha_input = wait.until(EC.presence_of_element_located((By.ID, "password-input")))

    email_input.send_keys(email)
    senha_input.send_keys(senha)

    # Clica no botão de login
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn[type='submit']"))
    )
    login_button.click()

    # Aguarda redirecionamento
    time.sleep(7)

    # ACESSA DIRETAMENTE A CATEGORIA TI E PROGRAMAÇÃO
    driver.get("https://www.workana.com/jobs?category=it-programming&language=pt")
    time.sleep(5)  # espera os projetos carregarem

    # FUNÇÃO PARA BUSCAR PROJETOS
    def buscar_projetos():
        try:
            projetos = driver.find_elements(By.CLASS_NAME, "project-item")
            print(f"{len(projetos)} projetos encontrados na categoria TI e Programação:")
            for p in projetos:
                try:
                    titulo = p.find_element(By.TAG_NAME, "h2").text
                    print("Projeto encontrado:", titulo)
                except:
                    continue
        except Exception as e:
            print("Erro ao buscar projetos:", e)

        # Filtrar projetos que contenham "WEB" no título
        try:
            projetos = driver.find_elements(By.CLASS_NAME, "project-item")
            print(f"Procurando projetos WEB... ({len(projetos)} encontrados)")
            for p in projetos:
                try:
                    titulo = p.find_element(By.TAG_NAME, "h2").text
                    if "WEB" in titulo.upper():
                        print("Projeto WEB encontrado:", titulo)
                except:
                    continue
        except Exception as e:
            print("Erro ao buscar projetos WEB:", e)

    # LOOP PRINCIPAL (a cada 2 minutos)
    try:
        while True:
            buscar_projetos()
            print("Aguardando 2 minutos para nova verificação...\n")
            time.sleep(120)
    except KeyboardInterrupt:
        print("Execução interrompida pelo usuário.")

finally:
    # Encerra driver com segurança
    if driver:
        driver.quit()
        print("Driver encerrado.")
