# Projeto de Webscraping PBX Broadsoft

## Descrição

Este projeto realiza webscraping de dados de ultimas ligações de usuários do PBX Broadsoft, transformando-os em dados para montagem de relatórios. Ele é composto por um servidor Flask que gerencia as requisições e os processos de webscraping, e um script de webscraping utilizando Selenium.

## Funcionalidades

- **Servidor Flask**: Gerencia a interface web e os processos de webscraping.
- **Webscraping**: Coleta os dados de ligações (Efetuadas, Recebidas, Perdidas) de usuários do PBX Broadsoft.
- **Logs**: Gera e armazena logs de cada processo de webscraping.
- **Relatórios**: Gera e salva relatórios em formato de texto contendo os dados das ligações.

## Requisitos

- **Sistema Operacional**: CentOS 7
- **Python**: 3.6
- **Bibliotecas Python**:
  - Flask
  - Flask-SocketIO
  - Selenium
- **Webdriver Chrome**: Verificar o disponivel no momento https://developer.chrome.com/docs/chromedriver/downloads/version-selection?hl=pt-br.

## Instalação

### 1. Preparar o Ambiente

Instale as dependências necessárias:

```bash
sudo yum update
sudo yum install -y python36 python36-pip
pip install flask flask-socketio selenium
```

### 1. Preparar o Ambiente
```bash
wget https://chromedriver.storage.googleapis.com/<versão>/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
```

### 2. Download do projeto do Github
```
git clone https://github.com/seu-usuario/nome-do-repositorio.git](https://github.com/gothout/RelatorioBroadsoftCall.git
```

### 2.1 Login na sua conta Broadsoft
```
No arquivo webscraping_ligações.py, modifique as linhas:
35: campo_usuario.send_keys('INFORME SEU USUARIO DE LOGIN NO BROADSOFT XSP(AS)')
36: campo_senha.send_keys('INFORME SUA SENHA DE USUARIO DE LOGIN NO BROADSOFT XSP(AS)')
```

### 4. Arquivos do Projeto
 - /app.py: Arquivo principal que configura o servidor Flask e gerencia as rotas para iniciar os processos de webscraping, visualizar os job IDs, acessar os logs e baixar os relatórios.
 - /webscraping_ligacoes.py: Script que realiza o webscraping dos dados de ligações de usuários do PBX Broadsoft usando Selenium.
 - /logs/: Armazena os logs gerados pelos processos de webscraping.
 - /saves/: Armazena os relatórios gerados após a coleta dos dados.
 - /templates/: Contém os templates HTML para a interface web.
 - /jobids.txt/: Armazena os job IDs para rastreamento dos processos de webscraping.
 - /log_flask.log/: Armazena os logs completos da aplicação Flask.
 - 
## Utilização

### Iniciar o Servidor Flask:
Execute o comando abaixo para iniciar o servidor Flask:

```bash
sudo python3.6 app.py
```

### Acessar a Interface Web:
Abra um navegador e acesse `http://localhost:5000` para visualizar a interface web.

### Enviar Requisição de Webscraping:
Insira os e-mails dos usuários para os quais deseja coletar os dados de ligação e clique em "Enviar".
O servidor Flask gerará um job ID e iniciará um processo de webscraping em segundo plano.
Para visualizar o carregamento do job ID gerado, apenas insira o código do Job ID e clique em "Ver Log"

## Rotas

### Rota `/`
- **Método:** GET
- **Descrição:** Renderiza a página principal do site, que é o arquivo `index.html`.
- **Função:** `index()`
- **Retorno:** `render_template('index.html')`

### Rota `/submit`
- **Método:** POST
- **Descrição:** Recebe um formulário com um campo de e-mails, gera um `job_id` usando o comando `uuidgen` e inicia um processo separado para executar um script Python (`webscraping_ligacoes.py`) com o `job_id` e os e-mails como argumentos. O `job_id` é salvo em um arquivo de texto.
- **Função:** `submit()`
- **Retorno:** String informando que o job foi iniciado, junto com o `job_id` e os e-mails.

### Rota `/job_ids`
- **Método:** GET
- **Descrição:** Lê os `job_ids` salvos, verifica se existem arquivos de log correspondentes e retorna uma lista de `job_ids` com as datas de criação dos logs ou um símbolo indicando que o log não foi encontrado.
- **Função:** `get_job_ids()`
- **Retorno:** JSON com uma lista de `job_ids` e as datas de criação dos logs.

### Rota `/latest_log`
- **Método:** GET
- **Descrição:** (Não implementado completamente) Deveria retornar o conteúdo do log mais recente, mas atualmente retorna uma mensagem padrão.
- **Função:** `get_latest_log()`
- **Retorno:** JSON com um conteúdo de log padrão.

### Rota `/log/<job_id>`
- **Método:** GET
- **Descrição:** Retorna o conteúdo do arquivo de log correspondente ao `job_id` fornecido.
- **Função:** `get_log_by_job_id(job_id)`
- **Parâmetro:** `job_id` (identificador do job)
- **Retorno:** JSON com o conteúdo do log ou uma mensagem informando que o arquivo de log não foi encontrado.

### Rota `/download/<job_id>`
- **Método:** GET
- **Descrição:** Permite o download do arquivo de saída correspondente ao `job_id` fornecido.
- **Função:** `download_file(job_id)`
- **Parâmetro:** `job_id` (identificador do job)
- **Retorno:** O arquivo para download como anexo.

## Eventos do SocketIO

### Evento `join_job`
- **Descrição:** Adiciona o cliente à sala correspondente ao `job_id` fornecido e começa a emitir atualizações de log para essa sala.
- **Função:** `on_join(data)`
- **Parâmetro:** `data` (deve conter `job_id`)

### Evento `leave_job`
- **Descrição:** Remove o cliente da sala correspondente ao `job_id` fornecido.
- **Função:** `on_leave(data)`
- **Parâmetro:** `data` (deve conter `job_id`)

## Funções Auxiliares

### `save_job_id(job_id)`
- **Descrição:** Salva um `job_id` em um arquivo de texto (`jobids.txt`).

### `read_job_ids()`
- **Descrição:** Lê e retorna todos os `job_ids` salvos no arquivo de texto (`jobids.txt`).

### `emit_log_for_job(job_id)`
- **Descrição:** Emite o conteúdo do log correspondente ao `job_id` para a sala do `job_id` continuamente a cada segundo.
- **Parâmetro:** `job_id` (identificador do job)

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.
