import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import hashlib
import re
from database.database import get_redis_connection, save_project_to_mariadb

uc.TARGET_VERSION = 139
email = "komest.contact@gmail.com"
senha = "926759058#Komest"


options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")

abrir_visivelmente = False
if not abrir_visivelmente:
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

driver = uc.Chrome(options=options)
driver.set_window_size(1200, 800)
wait = WebDriverWait(driver, 20)

# Conexão com Redis
redis_client = get_redis_connection()

# ===============================
# FUNÇÕES UTILITÁRIAS
# ===============================

def generate_project_id(titulo, link, fonte):
    """Gera um ID único baseado no título, link e fonte"""
    unique_string = f"{titulo}_{link}_{fonte}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def is_duplicate(project_id):
    """Verifica se o projeto já existe no Redis"""
    return redis_client.exists(f"project:{project_id}")

def save_to_redis(project_id):
    """Salva o projeto no Redis para verificação futura"""
    redis_client.setex(f"project:{project_id}", 86400 * 7, "processed")

def extrair_titulo(projeto):
    """Extrai o título do projeto"""
    try:
        return projeto.find_element(By.TAG_NAME, "h2").text.strip()
    except:
        return "Título não disponível"

def extrair_link(projeto):
    """Extrai o link do projeto"""
    try:
        return projeto.find_element(By.TAG_NAME, "a").get_attribute("href")
    except:
        return ""

def extrair_publicado(projeto):
    """Extrai a data de publicação"""
    try:
        return projeto.find_element(By.CLASS_NAME, "date").text.strip()
    except:
        return "N/A"

def extrair_propostas(projeto):
    """Extrai o número de propostas"""
    try:
        propostas_text = projeto.find_element(By.CLASS_NAME, "bids").text.strip()
        numeros = re.findall(r'\d+', propostas_text)
        return int(numeros[0]) if numeros else 0
    except:
        return 0

def extrair_descricao(projeto):
    """Extrai a descrição do projeto"""
    try:
        descricao_element = projeto.find_element(By.CLASS_NAME, "html-desc")
        return descricao_element.text.strip()
    except:
        return "Descrição não disponível"

def extrair_habilidades(projeto):
    """Extrai as habilidades requeridas"""
    try:
        habilidades_elements = projeto.find_elements(By.CSS_SELECTOR, ".skills h3")
        habilidades = [h.text.strip() for h in habilidades_elements if h.text.strip()]
        return ', '.join(habilidades) if habilidades else "Não especificadas"
    except:
        return "Não especificadas"

def extrair_budget(projeto):
    """Extrai o orçamento do projeto"""
    try:
        return projeto.find_element(By.CLASS_NAME, "budget").text.strip()
    except:
        return "N/A"

def extrair_cliente(projeto):
    """Extrai informações do cliente"""
    try:
        cliente_element = projeto.find_element(By.CLASS_NAME, "author-info")
        return cliente_element.text.strip()
    except:
        return "Cliente não identificado"

def extrair_tipo_projeto(projeto):
    """Extrai o tipo de projeto"""
    try:
        budget_text = extrair_budget(projeto).lower()
        if 'hora' in budget_text or 'hour' in budget_text:
            return "Hourly"
        elif 'fixo' in budget_text or 'fixed' in budget_text:
            return "Fixed Price"
        else:
            return "Unknown"
    except:
        return "Unknown"

def processar_projeto(projeto):
    """Processa um projeto individual do Workana"""
    try:
        # Extrai informações básicas
        titulo = extrair_titulo(projeto)
        link = extrair_link(projeto)
        
        if not titulo or not link:
            return None
        
        # Gera ID único
        project_id = generate_project_id(titulo, link, "workana")
        
        # Verifica duplicata
        if is_duplicate(project_id):
            print(f"⏭️  Projeto duplicado: {titulo}")
            return None
        
        # Extrai informações adicionais
        projeto_data = {
            'id': project_id,
            'titulo': titulo,
            'link': link,
            'descricao': extrair_descricao(projeto),
            'cliente': extrair_cliente(projeto),
            'cliente_link': None,
            'habilidades': extrair_habilidades(projeto),
            'propostas': extrair_propostas(projeto),
            'tempo_restante': None,
            'avaliacao': None,
            'num_avaliacoes': None,
            'budget': extrair_budget(projeto),
            'publicado': extrair_publicado(projeto),
            'tipo': extrair_tipo_projeto(projeto)
        }
        
        return projeto_data
        
    except Exception as e:
        print(f"❌ Erro ao processar projeto Workana: {e}")
        return None

# ===============================
# FUNÇÃO PRINCIPAL DE BUSCA
# ===============================

def buscar_projetos():
    try:
        time.sleep(3)
        
        projetos = driver.find_elements(By.CLASS_NAME, "project-item")
        print(f"\n🔍 Encontramos {len(projetos)} projetos no Workana!")
        print("=" * 60)
        
        novos_projetos = 0
        projetos_processados = 0
        
        for projeto in projetos:
            projetos_processados += 1
            projeto_data = processar_projeto(projeto)
            
            if projeto_data:
                if save_project_to_mariadb(projeto_data, "workana"):
                    save_to_redis(projeto_data['id'])
                    novos_projetos += 1
                    
                    print(f"\n✅ NOVO PROJETO SALVO:")
                    print(f"   ID: {projeto_data['id']}")
                    print(f"   Título: {projeto_data['titulo']}")
                    print(f"   Tipo: {projeto_data['tipo']}")
                    print(f"   Budget: {projeto_data['budget']}")
                    print(f"   Propostas: {projeto_data['propostas']}")
                    print(f"   Publicado: {projeto_data['publicado']}")
                    print(f"   Link: {projeto_data['link']}")
                    print("-" * 40)
            
            time.sleep(0.3)
        
        print(f"\n📊 RESUMO:")
        print(f"   Projetos processados: {projetos_processados}")
        print(f"   Novos projetos salvos: {novos_projetos}")
        print(f"   Projetos duplicados: {projetos_processados - novos_projetos}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar projetos Workana: {str(e)}")

# ===============================
# FUNÇÕES DE LOGIN E NAVEGAÇÃO
# ===============================

def fechar_banner_cookies():
    """Fecha o banner de cookies se existir"""
    try:
        botao_cookies = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        botao_cookies.click()
        print("✅ Banner de cookies fechado.")
        time.sleep(1)
    except:
        print("ℹ️  Nenhum banner de cookies encontrado.")

def fazer_login():
    """Realiza o login no Workana"""
    print("🌐 Acessando Workana...")
    driver.get("https://www.workana.com/login")
    
    print("⏳ Aguardando página carregar...")
    time.sleep(5)
    
    try:
        fechar_banner_cookies()
        
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input")))
        senha_input = wait.until(EC.presence_of_element_located((By.ID, "password-input")))
        
        email_input.clear()
        email_input.send_keys(email)
        senha_input.clear()
        senha_input.send_keys(senha)
        
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn[type='submit']"))
        )
        login_button.click()
        
        time.sleep(7)
        print("✅ Login realizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

def acessar_categoria_ti():
    """Acessa a categoria de TI e Programação"""
    try:
        print("🌐 Acessando categoria TI e Programação...")
        driver.get("https://www.workana.com/jobs?category=it-programming&language=pt")
        time.sleep(5)
        
        if "it-programming" in driver.current_url:
            print("✅ Categoria TI e Programação carregada com sucesso!")
            return True
        else:
            print("❌ Não foi possível acessar a categoria TI")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao acessar categoria: {e}")
        return False

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================

def main():
    """Função principal"""
    try:
        if not fazer_login():
            print("❌ Falha no login. Encerrando...")
            return
        
        if not acessar_categoria_ti():
            print("❌ Falha ao acessar categoria. Encerrando...")
            return
        
        contador = 1
        while True:
            print(f"\n🔄 VERIFICAÇÃO #{contador} - {time.strftime('%d/%m/%Y %H:%M:%S')}")
            print("=" * 50)
            
            buscar_projetos()
            
            print(f"\n⏰ Próxima verificação em 2 minutos...")
            for i in range(120, 0, -1):
                if i % 30 == 0 or i <= 5:
                    print(f"   ⏳ {i} segundos restantes...")
                time.sleep(1)
            
            contador += 1
            
            if contador % 3 == 0:
                print("🔄 Recarregando página...")
                driver.refresh()
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        try:
            driver.quit()
            print("✅ Driver do navegador encerrado.")
        except:
            pass
        
        print("👋 Script Workana finalizado.")

if __name__ == "__main__":
    main()