import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import hashlib
import re
from database import get_redis_connection, get_mariadb_connection

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

driver = uc.Chrome(options=options)

# Cria espera explícita
wait = WebDriverWait(driver, 15)

# Conexões com Redis e MariaDB
redis_client = get_redis_connection()
db_conn = get_mariadb_connection()

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
    redis_client.setex(f"project:{project_id}", 86400 * 7, "processed")  # 7 dias

def save_to_mariadb(project_data, fonte):
    """Salva o projeto no MariaDB"""
    try:
        cursor = db_conn.cursor()
        
        sql = """
        INSERT INTO freelas_projects 
        (id, titulo, link, descricao, cliente, cliente_link, habilidades, 
         propostas, tempo_restante, avaliacao, num_avaliacoes, fonte)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            project_data['id'],
            project_data['titulo'],
            project_data['link'],
            project_data['descricao'],
            project_data['cliente'],
            project_data['cliente_link'],
            project_data['habilidades'],
            project_data['propostas'],
            project_data['tempo_restante'],
            project_data['avaliacao'],
            project_data['num_avaliacoes'],
            fonte
        )
        
        cursor.execute(sql, valores)
        db_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar no MariaDB: {e}")
        db_conn.rollback()
        return False

def extrair_descricao(projeto):
    """Extrai a descrição do projeto"""
    try:
        descricao_element = projeto.find_element(By.CLASS_NAME, "description")
        try:
            expandir_btn = descricao_element.find_element(By.CLASS_NAME, "more-link")
            driver.execute_script("arguments[0].click();", expandir_btn)
            time.sleep(1)
        except:
            pass
        descricao = descricao_element.get_attribute('textContent').strip()
        return descricao.replace("Expandir", "").replace("Esconder", "").replace("…", "").strip()
    except:
        return "Descrição não disponível"

def extrair_cliente(projeto):
    """Extrai o nome do cliente"""
    try:
        cliente_element = projeto.find_element(By.CLASS_NAME, "client")
        return cliente_element.find_element(By.XPATH, ".//a").text
    except:
        return "Cliente não identificado"

def extrair_cliente_link(projeto):
    """Extrai o link do cliente"""
    try:
        cliente_element = projeto.find_element(By.CLASS_NAME, "client")
        return cliente_element.find_element(By.XPATH, ".//a").get_attribute("href")
    except:
        return ""

def extrair_habilidades(projeto):
    """Extrai as habilidades requeridas"""
    try:
        return projeto.find_element(By.CLASS_NAME, "habilidades").text
    except:
        return "Não especificadas"

def extrair_propostas(info_text):
    """Extrai o número de propostas do texto de informações"""
    try:
        if "Propostas:" in info_text:
            propostas_text = info_text.split("Propostas:")[1].split("|")[0].strip()
            return int(re.search(r'\d+', propostas_text).group())
        return 0
    except:
        return 0

def extrair_tempo_restante(projeto):
    """Extrai o tempo restante para o projeto"""
    try:
        return projeto.find_element(By.CLASS_NAME, "datetime-restante").text
    except:
        return "Não informado"

def extrair_avaliacao(projeto):
    """Extrai a avaliação do cliente"""
    try:
        cliente_element = projeto.find_element(By.CLASS_NAME, "client")
        avaliacao_score = cliente_element.find_element(By.CLASS_NAME, "avaliacoes-star").get_attribute("data-score")
        return float(avaliacao_score) if avaliacao_score else 0.0
    except:
        return 0.0

def extrair_num_avaliacoes(projeto):
    """Extrai o número de avaliações do cliente"""
    try:
        cliente_element = projeto.find_element(By.CLASS_NAME, "client")
        avaliacao_text = cliente_element.find_element(By.CLASS_NAME, "avaliacoes-text").text
        # Extrai números do texto de avaliação
        numeros = re.findall(r'\d+', avaliacao_text)
        return int(numeros[0]) if numeros else 0
    except:
        return 0

def processar_projeto(projeto):
    """Processa um projeto individual do 99freelas"""
    try:
        # Extrai informações básicas
        titulo_element = projeto.find_element(By.XPATH, ".//h1[contains(@class, 'title')]//a")
        titulo = titulo_element.text
        link = titulo_element.get_attribute("href")
        
        # Gera ID único
        project_id = generate_project_id(titulo, link, "99freelas")
        
        # Verifica duplicata
        if is_duplicate(project_id):
            print(f"⏭️  Projeto duplicado: {titulo}")
            return None
        
        # Extrai informações adicionais
        info_block = projeto.find_element(By.CLASS_NAME, "information").text
        
        projeto_data = {
            'id': project_id,
            'titulo': titulo,
            'link': link,
            'descricao': extrair_descricao(projeto),
            'cliente': extrair_cliente(projeto),
            'cliente_link': extrair_cliente_link(projeto),
            'habilidades': extrair_habilidades(projeto),
            'propostas': extrair_propostas(info_block),
            'tempo_restante': extrair_tempo_restante(projeto),
            'avaliacao': extrair_avaliacao(projeto),
            'num_avaliacoes': extrair_num_avaliacoes(projeto)
        }
        
        return projeto_data
        
    except Exception as e:
        print(f"❌ Erro ao processar projeto: {e}")
        return None

# ===============================
# FUNÇÃO PRINCIPAL DE BUSCA
# ===============================

def buscar_projetos():
    try:
        # Aguarda a lista de resultados carregar
        lista_projetos = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-list")))
        
        # Encontra todos os itens de projeto
        projetos = lista_projetos.find_elements(By.CLASS_NAME, "result-item")
        print(f"\n🔍 Encontramos {len(projetos)} projetos no 99freelas!")
        print("=" * 60)
        
        novos_projetos = 0
        projetos_processados = 0
        
        for projeto in projetos:
            projetos_processados += 1
            projeto_data = processar_projeto(projeto)
            
            if projeto_data:
                # Salva no banco de dados
                if save_to_mariadb(projeto_data, "99freelas"):
                    # Marca como processado no Redis
                    save_to_redis(projeto_data['id'])
                    novos_projetos += 1
                    
                    # Exibe informações do projeto salvo
                    print(f"\n✅ NOVO PROJETO SALVO:")
                    print(f"   ID: {projeto_data['id']}")
                    print(f"   Título: {projeto_data['titulo']}")
                    print(f"   Cliente: {projeto_data['cliente']}")
                    print(f"   Propostas: {projeto_data['propostas']}")
                    print(f"   Avaliação: {projeto_data['avaliacao']}")
                    print(f"   Link: {projeto_data['link']}")
                    print("-" * 40)
            
            # Pequena pausa entre projetos para não sobrecarregar
            time.sleep(0.5)
        
        print(f"\n📊 RESUMO:")
        print(f"   Projetos processados: {projetos_processados}")
        print(f"   Novos projetos salvos: {novos_projetos}")
        print(f"   Projetos duplicados: {projetos_processados - novos_projetos}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar projetos: {str(e)}")

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================

def fazer_login():
    """Realiza o login no site"""
    print("🌐 Acessando 99freelas...")
    driver.get("https://www.99freelas.com.br/login")
    
    print("⏳ Aguardando 5 segundos antes de fazer login...")
    time.sleep(5)
    
    try:
        # Espera campos de email e senha carregarem
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        senha_input = wait.until(EC.presence_of_element_located((By.ID, "senha")))
        
        # Preenche login
        email_input.send_keys(email)
        senha_input.send_keys(senha)
        
        # Clica no botão de login
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "btnEfetuarLogin")))
        login_button.click()
        
        # Aguarda login ser concluído
        time.sleep(5)
        print("✅ Login realizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

def main():
    """Função principal"""
    try:
        # Realiza login
        if not fazer_login():
            print("❌ Falha no login. Encerrando...")
            return
        
        # Acessa a página de projetos
        print("🌐 Acessando projetos...")
        driver.get("https://www.99freelas.com.br/projects?order=mais-recentes&categoria=web-mobile-e-software")
        time.sleep(5)
        
        # Loop principal de verificação
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
            
            # Recarrega a página a cada 5 verificações
            if contador % 5 == 0:
                print("🔄 Recarregando página...")
                driver.refresh()
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        # Encerra conexões e driver
        try:
            db_conn.close()
            print("✅ Conexão com MariaDB fechada.")
        except:
            pass
            
        try:
            driver.quit()
            print("✅ Driver do navegador encerrado.")
        except:
            pass
        
        print("👋 Script finalizado.")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    main()