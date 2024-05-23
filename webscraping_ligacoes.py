import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import datetime

# Configuração do WebDriver
option = webdriver.ChromeOptions()
option.add_argument('--headless')
option.add_argument('--no-sandbox')
option.add_argument('--disable-dev-shm-usage')
chromedriver_path = '/usr/local/bin/chromedriver'  # Caminho para o chromedriver no Linux
s = Service(chromedriver_path)

# Função para salvar mensagens no arquivo de log
def salvar_log(log_file, job_id, mensagem):
    log_msg = f"[{job_id}] [{datetime.datetime.now()}] {mensagem}\n"
    log_file.write(log_msg)
    log_file.flush()  # Força a gravação imediata no arquivo
    print(log_msg)

# Função de login
def login(driver, log_file, job_id):
    driver.get('https://xsp2.gc.italk.net.br/Login/')
    campo_usuario = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'EnteredUserID'))
    )
    campo_senha = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'Password'))
    )
    campo_usuario.send_keys('INFORME SEU USUARIO DE LOGIN NO BROADSOFT XSP(AS)')
    campo_senha.send_keys('INFORME SUA SENHA DE USUARIO DE LOGIN NO BROADSOFT XSP(AS)')
    driver.execute_script("submitForm()")
    salvar_log(log_file, job_id, "Login bem-sucedido!")

# Função para coletar dados do usuário
def coletar_dados_usuario(driver, email, log_file, job_id):
    try:
        salvar_log(log_file, job_id, f"Coletando dados para o usuário {email}")

        driver.get('https://xsp2.gc.italk.net.br/Operator/Users/')

        select_opcao = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'findOp0'))
        )
        select_opcao.find_element(By.XPATH, "//option[@value='EQUAL_TO']").click()

        campo_pesquisa = driver.find_element(By.ID, 'findValue0')
        campo_pesquisa.send_keys(email)

        botao_pesquisa = driver.find_element(By.ID, 'search0')
        botao_pesquisa.click()

        link_usuario = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{email.split('@')[0]}')]"))
        )
        salvar_log(log_file, job_id, f"Usuário {email} encontrado!")
        link_usuario.click()

        perfil_usuario_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/User/Addresses/')]"))
        )
        perfil_usuario_link.click()

        ramal_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'extension'))
        )
        ramal = ramal_element.get_attribute('value')
        salvar_log(log_file, job_id, f"Ramal para o usuário {email} encontrado: {ramal}")

        tipos_chamadas = {
            'Efetuadas': 'https://xsp2.gc.italk.net.br/User/BasicCallLogs/index.jsp?type=0',
            'Recebidas': 'https://xsp2.gc.italk.net.br/User/BasicCallLogs/index.jsp?type=1',
            'Perdidas': 'https://xsp2.gc.italk.net.br/User/BasicCallLogs/index.jsp?type=2'
        }

        todos_registros = []

        for tipo, url in tipos_chamadas.items():
            driver.get(url)

            try:
                mensagem_ausencia = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//td[@colspan='10' and contains(text(), 'Não ha entradas presentes')]"))
                )
                salvar_log(log_file, job_id, f"Sem dados de ligações {tipo.lower()} para o usuário {email}")
                todos_registros.append((tipo, ["Sem dados de ligações"]))
            except TimeoutException:
                registros_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//tr[starts-with(@id, 'Row')]"))
                )

                registros = []
                for registro_element in registros_element:
                    nome = registro_element.find_element(By.XPATH, ".//td[3]").text
                    numero_telefone = registro_element.find_element(By.XPATH, ".//td[5]").text
                    data_hora = registro_element.find_element(By.XPATH, ".//td[7]").text
                    registro_formatado = f"Número de Telefone: {numero_telefone}, Data/Hora: {data_hora}"
                    registros.append(registro_formatado)
                    salvar_log(log_file, job_id, f"{tipo} - {registro_formatado}")

                todos_registros.append((tipo, registros))

        return ramal, todos_registros
    except Exception as e:
        salvar_log(log_file, job_id, f"Erro ao coletar dados para {email}: {str(e)}")
        return None, []

# Função principal para ser chamada externamente
def processar_emails(job_id, emails):
    dados_coletados = []

    # Define o nome do arquivo de log com a data atual
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
    nome_arquivo_log = f'{job_id}_log_{data_atual}.log'
    caminho_arquivo_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', nome_arquivo_log)

    # Abre o arquivo de log em modo de adição
    with open(caminho_arquivo_log, 'a') as log_file:

        # Inicializa o WebDriver
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=option)
        login(driver, log_file, job_id)

        # Para cada email na lista, coleta os dados do usuário
        for email in emails:
            ramal, todos_registros = coletar_dados_usuario(driver, email, log_file, job_id)
            if ramal is not None:
                for tipo, registros in todos_registros:
                    for registro in registros:
                        dados_coletados.append(f"{email},{ramal},{tipo},{registro}")

        # Encerra o WebDriver
        driver.quit()

        # Define o nome do arquivo como o job_id
        nome_arquivo = f'{job_id}.txt'
        caminho_arquivo_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)),'saves', nome_arquivo)

        # Salva os dados em um arquivo TXT
        with open(caminho_arquivo_dados, 'w') as arquivo_dados:
            for linha in dados_coletados:
                arquivo_dados.write(linha + '\n')

        # Imprime a mensagem de conclusão
        salvar_log(log_file, job_id, f"Os dados foram salvos no arquivo: {caminho_arquivo_dados}")
        print(f"Arquivo de resultado para JOB ID {job_id}: {nome_arquivo}")

    # Retorna o nome do arquivo de dados processados
    return nome_arquivo

# Função principal para processar os e-mails passados como argumentos da linha de comando
def main():
    if len(sys.argv) < 3:
        print("Uso correto: python3.6 nome_do_script.py [job_id] [email1,email2,email3,...]")
        return

    job_id = sys.argv[1]
    emails = sys.argv[2].split(',')  # Dividindo a string de e-mails em uma lista

    arquivo_resultado = processar_emails(job_id, emails)
    print(f"Arquivo de resultado para JOB ID {job_id}: {arquivo_resultado}")

if __name__ == "__main__":
    main()