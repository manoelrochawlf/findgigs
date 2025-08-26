import time
import tkinter as tk
from tkinter import simpledialog
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# PAINEL GRÁFICO PARA LOGIN

root = tk.Tk()
root.withdraw()  # Esconde a janela principal

# Usuário digita e-mail e senha
email = simpledialog.askstring("Login Workana", "Digite seu e-mail:")
senha = simpledialog.askstring("Login Workana", "Digite sua senha:", show="*")

if not email or not senha:
    print("E-mail ou senha não fornecidos. Encerrando.")
    exit()


# CONFIGURAÇÃO DO CHROME

options = uc.ChromeOptions()
# options.add_argument("--disable-extensions")
# options.add_argument("--no-sandbox")
# options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)

# Cria espera explícita
wait = WebDriverWait(driver, 15)


# LOGIN NO SITE
driver.get("https://www.workana.com/login")

time.sleep(3)  # espera inicial

# Fecha banner de cookies
try:
    botao_cookies = wait.until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    botao_cookies.click()
    print("Banner de cookies fechado.")
except:
    print("Nenhum banner de cookies encontrado ou já fechado.")


# Espera campos de email e senha carregarem
email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input")))
senha_input = wait.until(EC.presence_of_element_located((By.ID, "password-input")))


# Preenche login
email_input.send_keys(email)
senha_input.send_keys(senha)

# Clica no botão de login
login_button = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn[type='submit']"))
)
login_button.click()

# Aguarda redirecionamento ou algum elemento que indique login concluído
time.sleep(5)  


# ACESSA MEUS PROJETOS
driver.get("https://www.workana.com/jobs")

# Espera os filtros carregarem
time.sleep(3)  # Ajuste se precisar

# Seleciona o checkbox da categoria TI e Programação
try:
    label_ti = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='category-it-programming']"))
    )
    label_ti.click()  # Clica no label, não no input
    time.sleep(3)  # espera os projetos filtrarem
except Exception as e:
    print("Erro ao aplicar filtro de TI e Programação:", e)


# FUNÇÃO PARA BUSCAR PROJETOS

def buscar_projetos():
    try:
        projetos = driver.find_elements(By.CLASS_NAME, "project-item")
        print(f"{len(projetos)} projetos encontrados após aplicar filtro de TI e Programação:")
        for p in projetos:
            try:
                titulo = p.find_element(By.TAG_NAME, "h2").text
                print("Projeto encontrado:", titulo)
            except:
                continue
    except Exception as e:
        print("Erro ao buscar projetos:", e)

    try:
        projetos = driver.find_elements(By.CLASS_NAME, "project-item")
        print(f"Procurando projetos WEB... ({len(projetos)} encontrados)")
        for p in projetos:
            try:
                titulo = p.find_element(By.TAG_NAME, "h2").text
                if "WEB" in titulo.upper():
                    print("Projeto encontrado:", titulo)
            except:
                continue
    except Exception as e:
        print("Erro ao buscar projetos:", e)

# LOOP PRINCIPAL (a cada 2 minutos)

try:
    while True:
        buscar_projetos()
        print("Aguardando 2 minutos para nova verificação...\n")
        time.sleep(120)
except KeyboardInterrupt:
    print("Execução interrompida pelo usuário.")
finally:
    driver.quit()
    print("Driver encerrado.")
