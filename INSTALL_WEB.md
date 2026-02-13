# 🛠️ Instalação da Interface Web

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

## Instalação Passo a Passo

### 1. Navegue até o diretório do projeto

```bash
cd D:\Eliel\WebCopy\webcopy
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

Isso instalará:
- requests (HTTP)
- beautifulsoup4 (HTML parsing)
- lxml (XML/HTML parser)
- click (CLI)
- brotli (compressão)
- **flask** (servidor web) ✨ NOVO
- **flask-cors** (CORS) ✨ NOVO

### 3. Verifique a instalação

```bash
python -c "import flask; print('Flask instalado com sucesso!')"
```

Se não houver erros, está tudo pronto!

## Iniciando o Servidor

### Método 1: Script run_web.py (Recomendado)

```bash
python run_web.py
```

Você verá:

```
============================================================
WebCopy - Interface Web
============================================================
🌐 Servidor iniciado em: http://localhost:5000
📁 Diretório de saída: D:\Eliel\WebCopy\webcopy\output
============================================================

Pressione Ctrl+C para parar o servidor
```

### Método 2: Módulo Python

```bash
python -m webcopy.web.app
```

### Método 3: Flask CLI

```bash
# Windows
set FLASK_APP=src\webcopy\web\app.py
flask run

# Linux/Mac
export FLASK_APP=src/webcopy/web/app.py
flask run
```

## Acessando a Interface

1. Abra seu navegador
2. Acesse: **http://localhost:5000**
3. Pronto! A interface deve aparecer

## Testando a Instalação

Execute o script de teste:

```bash
# Certifique-se de que o servidor está rodando em outro terminal
python test_web_interface.py
```

O teste irá:
1. ✅ Verificar conexão com o servidor
2. ✅ Criar um job de teste
3. ✅ Acompanhar o progresso
4. ✅ Testar download e preview

## Solução de Problemas

### Erro: "No module named 'flask'"

**Solução:**
```bash
pip install flask>=3.0.0 flask-cors>=4.0.0
```

### Erro: "No module named 'webcopy'"

**Solução:**
```bash
# Certifique-se de estar na raiz do projeto
cd D:\Eliel\WebCopy\webcopy
pip install -e .
```

### Erro: "Address already in use" (Porta 5000 ocupada)

**Solução 1:** Pare o processo que está usando a porta 5000

**Solução 2:** Mude a porta no `run_web.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Usa porta 8080
```

Depois acesse: http://localhost:8080

### Erro: "Permission denied"

**Solução (Windows):**
```bash
# Execute como administrador ou use outra porta (> 1024)
```

**Solução (Linux/Mac):**
```bash
# Use porta > 1024 ou execute com sudo (não recomendado)
```

### Interface não carrega (página em branco)

**Verificações:**

1. Servidor está rodando?
```bash
# Deve mostrar logs do Flask
```

2. Porta correta?
```bash
# Verifique se está acessando http://localhost:5000
```

3. Firewall bloqueando?
```bash
# Temporariamente desabilite o firewall para testar
```

4. Console do navegador tem erros?
```bash
# Pressione F12 e veja a aba Console
```

### Assets não carregam (CSS/JS)

**Verificação:**

```bash
# Estrutura de pastas deve estar assim:
src/webcopy/web/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    └── index.html
```

Se os arquivos não estiverem lá, algo deu errado na criação dos arquivos.

## Configuração Avançada

### Modo Produção

Para usar em produção (não recomendado para uso local):

1. Instale gunicorn:
```bash
pip install gunicorn
```

2. Execute:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 webcopy.web.app:app
```

### Variáveis de Ambiente

```bash
# Windows
set FLASK_ENV=development
set FLASK_DEBUG=1

# Linux/Mac
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### CORS para Desenvolvimento

Se precisar acessar de outro domínio, edite `src/webcopy/web/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Adicione esta linha
```

## Verificação Final

Execute este checklist:

- [ ] Python 3.8+ instalado
- [ ] pip funcionando
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Servidor inicia sem erros (`python run_web.py`)
- [ ] Interface carrega no navegador (http://localhost:5000)
- [ ] Consegue inserir uma URL
- [ ] Teste completo funciona (`python test_web_interface.py`)

Se todos os itens estão marcados, **a instalação está completa! 🎉**

## Próximos Passos

1. Leia o [QUICKSTART.md](QUICKSTART.md) para uso básico
2. Leia o [WEB_INTERFACE.md](WEB_INTERFACE.md) para documentação completa
3. Teste com um site real: https://example.com

## Suporte

Se encontrar problemas:

1. Verifique os logs do servidor (terminal onde rodou `run_web.py`)
2. Verifique o console do navegador (F12 → Console)
3. Leia a seção "Solução de Problemas" acima
4. Consulte o [README.md](README.md) principal

---

**Boa sorte! 🚀**
