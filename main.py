import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===============================
# CREDENCIAIS FIXAS
# ===============================
email = "caicrs.contact@gmail.com"  # Substitua pelo seu email
senha = "926759058#Leguas"         # Substitua pela sua senha

# ===============================
# CONFIGURAÇÃO DO NAVEGADOR
# ===============================
abrir_visivelmente = False  # Altere para False para rodar em modo headless

options = uc.ChromeOptions()
if not abrir_visivelmente:
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Necessário para algumas versões do Windows
# options.add_argument("--disable-extensions")
# options.add_argument("--no-sandbox")
# options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)

# Cria espera explícita
wait = WebDriverWait(driver, 15)

# LOGIN NO SITE
driver.get("https://www.99freelas.com.br/login")

print("Aguardando 10 segundos antes de fazer login...")
for i in range(10, 0, -1):
    print(f"Aguardando... {i} segundos")
    time.sleep(1)

# Espera campos de email e senha carregarem
email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
senha_input = wait.until(EC.presence_of_element_located((By.ID, "senha")))

# Preenche login
email_input.send_keys(email)
senha_input.send_keys(senha)

# Clica no botão de login
login_button = wait.until(EC.element_to_be_clickable((By.ID, "btnEfetuarLogin")))
login_button.click()

# Aguarda redirecionamento ou algum elemento que indique login concluído
time.sleep(5)  # Ajuste se precisar de mais tempo

# ===============================
# ACESSA MEUS PROJETOS
# ===============================
driver.get("https://www.99freelas.com.br/projects?order=mais-recentes&categoria=web-mobile-e-software")

# ===============================
# FUNÇÃO PARA BUSCAR PROJETOS
# ===============================
def buscar_projetos():
    try:
        # Aguarda a lista de resultados carregar
        wait = WebDriverWait(driver, 10)
        lista_projetos = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-list")))
        
        # Encontra todos os itens de projeto
        projetos = lista_projetos.find_elements(By.CLASS_NAME, "result-item")
        print(f"\nEncontramos {len(projetos)} projetos novos!")
        print("=" * 50)
        
        for projeto in projetos:
            try:
                # Extrai informações básicas usando XPath relativo ao projeto atual
                try:
                    titulo_element = projeto.find_element(By.XPATH, ".//h1[contains(@class, 'title')]//a")
                    titulo = titulo_element.text
                    link = titulo_element.get_attribute("href")
                except Exception as e:
                    print(f"Erro ao extrair título/link: {str(e)}")
                    titulo = "Título não disponível"
                    link = "Link não disponível"

                # Extrai informações adicionais
                try:
                    info = projeto.find_element(By.CLASS_NAME, "information").text
                except Exception as e:
                    print(f"Erro ao extrair informações: {str(e)}")
                    info = "Informações não disponíveis"

                # Extrai descrição
                try:
                    descricao_element = projeto.find_element(By.CLASS_NAME, "description")
                    # Tenta expandir a descrição
                    try:
                        expandir_btn = descricao_element.find_element(By.CLASS_NAME, "more-link")
                        driver.execute_script("arguments[0].click();", expandir_btn)
                        time.sleep(1)  # Aumentei o tempo de espera
                    except:
                        pass  # Ignora se não houver botão expandir
                    
                    descricao = descricao_element.get_attribute('textContent').strip()
                    descricao = descricao.replace("Expandir", "").replace("Esconder", "").replace("…", "").strip()
                except Exception as e:
                    print(f"Erro ao extrair descrição: {str(e)}")
                    descricao = "Descrição não disponível"

                # Extrai habilidades
                try:
                    habilidades = projeto.find_element(By.CLASS_NAME, "habilidades").text
                except:
                    habilidades = "Não especificadas"

                # Extrai informações do cliente
                try:
                    cliente_element = projeto.find_element(By.CLASS_NAME, "client")
                    cliente_nome = cliente_element.find_element(By.XPATH, ".//a").text
                    cliente = cliente_nome if cliente_nome else "Cliente não identificado"
                except:
                    cliente = "Cliente não identificado"

                # Extrai avaliação
                try:
                    avaliacao_element = projeto.find_element(By.CLASS_NAME, "avaliacoes-text").text
                except:
                    avaliacao_element = "Sem avaliações"

                # Imprime as informações formatadas
                print(f"\nTítulo: {titulo}")
                print(f"Link: {link}")
                print(f"Informações: {info}")
                print(f"Cliente: {cliente} - {avaliacao_element}")
                print(f"Habilidades: {habilidades}")
                print("\nDescrição completa:")
                print("-" * 20)
                print(descricao)
                print("-" * 50)

            except Exception as e:
                print(f"Erro ao processar um projeto específico: {str(e)}")
                continue

    except Exception as e:
        print(f"Erro ao buscar projetos: {str(e)}")
        
    print("\nAguardando 2 minutos para nova verificação...")

# ===============================
# LOOP PRINCIPAL (a cada 2 minutos)
# ===============================
try:
    while True:
        buscar_projetos()
        time.sleep(120)
except KeyboardInterrupt:
    print("Execução interrompida pelo usuário.")
finally:
    driver.quit()
    print("Driver encerrado.")
