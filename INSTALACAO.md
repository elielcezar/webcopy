# Instalacao do WebCopy

Guia definitivo de instalacao e execucao do WebCopy (CLI + Interface Web).

## Pre-requisitos

- **Python 3.8+** instalado ([python.org](https://www.python.org/downloads/))
- Navegador web moderno (Chrome, Firefox, Edge)

Verifique se o Python esta instalado:

```bash
python --version
```

## Instalacao

> **IMPORTANTE (Windows):** Se voce tem mais de uma versao do Python instalada
> (ex: Laragon + Python oficial), use **sempre** `python -m pip` em vez de `pip`
> para garantir que instala no Python correto.
>
> Para verificar: `python -c "import sys; print(sys.executable)"` mostra qual Python esta ativo.

Abra o terminal na **raiz do projeto** (onde esta o `setup.py`) e execute:

```bash
# 1. Instalar TODAS as dependencias (incluindo Flask para interface web)
python -m pip install -r requirements.txt

# 2. Instalar o pacote webcopy em modo desenvolvimento
python -m pip install -e .
```

Pronto. Isso instala tudo que e necessario.

## Verificar Instalacao

```bash
python -c "import flask; import webcopy; print('Tudo instalado com sucesso')"
```

Se nao houver erros, esta tudo certo.

## Executar a Interface Web

```bash
python run_web.py
```

Acesse no navegador: **http://localhost:5000**

### Como usar:

1. Cole a URL do site que deseja copiar
2. Clique em **"Copiar Site"**
3. Acompanhe o progresso em tempo real
4. Use **"Download ZIP"** ou **"Visualizar"** quando concluir

Os sites baixados ficam salvos na pasta `output/`.

## Executar via CLI (alternativa)

```bash
# Copiar um site via linha de comando
webcopy https://example.com

# Ou usando Python diretamente
python -m webcopy https://example.com
```

## Solucao de Problemas

| Erro | Causa | Solucao |
|------|-------|---------|
| `No module named 'flask'` | `pip` e `python` apontam para Pythons diferentes | `python -m pip install -r requirements.txt` |
| `No module named 'webcopy'` | Pacote nao instalado | `python -m pip install -e .` (na raiz do projeto) |
| `UnicodeEncodeError` com emojis | Terminal Windows nao suporta UTF-8 | Remover emojis do `run_web.py` ou usar `set PYTHONIOENCODING=utf-8` |
| `Address already in use` (porta 5000) | Outra aplicacao usando a porta | Edite a porta em `run_web.py` para 8080 |

## Instalacao em VPS (Ubuntu + CloudPanel)

Guia para instalar o WebCopy em um servidor VPS Ubuntu com CloudPanel e HTTPS.

### Pre-requisitos

- VPS com **Ubuntu 22.04+**
- **CloudPanel** instalado
- Dominio configurado apontando para o IP do servidor (ex: `webcopy.ecwd.cloud`)
- Acesso SSH ao usuario do site

### 1. Instalar Python (como root)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
python3 --version
```

O Python instalado como root fica disponivel para todos os usuarios do sistema.

### 2. Criar o site no CloudPanel

No painel do CloudPanel, crie um novo site com o dominio desejado (ex: `webcopy.ecwd.cloud`).
Isso cria automaticamente o usuario e o diretorio `/home/webcopy/htdocs/webcopy.ecwd.cloud/`.

### 3. Clonar o projeto e configurar (como usuario do site)

```bash
ssh webcopy@SEU_IP

cd ~/htdocs/webcopy.ecwd.cloud/
git clone https://github.com/SEU_USUARIO/webcopy.git .
```

> Se o diretorio nao estiver vazio, clone em uma pasta temporaria e mova os arquivos.

### 4. Criar ambiente virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

Verificar:

```bash
python -c "import flask; import webcopy; print('Tudo instalado com sucesso')"
```

### 5. Testar

```bash
python run_web.py
```

O servidor inicia na porta configurada em `run_web.py` (padrao: 3009).
Pressione `Ctrl+C` para parar o teste.

### 6. Configurar o Vhost no CloudPanel

No CloudPanel, va em **Sites > seu-dominio > Vhost** e substitua o conteudo por:

```nginx
server {
  listen 80;
  listen [::]:80;
  listen 443 quic;
  listen 443 ssl;
  listen [::]:443 quic;
  listen [::]:443 ssl;
  http2 on;
  http3 off;

  {{ssl_certificate_key}}
  {{ssl_certificate}}

  server_name webcopy.ecwd.cloud;

  {{nginx_access_log}}
  {{nginx_error_log}}

  if ($scheme != "https") {
    rewrite ^ https://$host$request_uri permanent;
  }

  location ~ /.well-known {
    auth_basic off;
    allow all;
  }

  {{settings}}

  include /etc/nginx/global_settings;

  location / {
    proxy_pass http://127.0.0.1:3009;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    proxy_read_timeout 300s;
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;
  }
}
```

> **Importante:** O `location /` envia TODAS as requisicoes para o Flask (HTML, API, arquivos estaticos).
> Ajuste `server_name` e a porta em `proxy_pass` conforme necessario.

### 7. Criar servico Systemd (rodar permanentemente)

Para que o WebCopy continue rodando apos fechar o terminal ou reiniciar o servidor, crie um servico systemd (como root):

```bash
sudo nano /etc/systemd/system/webcopy.service
```

Cole o conteudo:

```ini
[Unit]
Description=WebCopy - Interface Web
After=network.target

[Service]
Type=simple
User=webcopy
WorkingDirectory=/home/webcopy/htdocs/webcopy.ecwd.cloud
ExecStart=/home/webcopy/htdocs/webcopy.ecwd.cloud/venv/bin/python run_web.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable webcopy
sudo systemctl start webcopy
sudo systemctl status webcopy
```

### 8. Atualizar o projeto no servidor

Para atualizar com novas versoes:

```bash
ssh webcopy@SEU_IP
cd ~/htdocs/webcopy.ecwd.cloud/
git pull
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
sudo systemctl restart webcopy
```

### Solucao de Problemas (VPS)

| Erro | Causa | Solucao |
|------|-------|---------|
| Connection timeout na porta 3009 | Firewall bloqueia portas diretas | Acesse via dominio HTTPS, nao pela porta |
| 502 Bad Gateway | Flask nao esta rodando | `sudo systemctl status webcopy` e verifique os logs |
| 504 Gateway Timeout | Processo demorado (site grande) | Os timeouts do proxy ja estao configurados para 300s |
| Site nao abre apos reboot | Servico nao habilitado | `sudo systemctl enable webcopy` |

## Resumo Rapido - Local (copiar e colar)

```bash
python -m pip install -r requirements.txt && python -m pip install -e . && python run_web.py
```

## Resumo Rapido - VPS (copiar e colar)

```bash
sudo apt install python3 python3-pip python3-venv -y
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && pip install -e .
python run_web.py
```

## Reiniciar o projeto
```bash
source venv/bin/activate
python run_web.py
```