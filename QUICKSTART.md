# 🚀 Guia Rápido - Interface Web

## Iniciando em 3 Passos

### 1️⃣ Instalar

```bash
cd webcopy
pip install -r requirements.txt
```

### 2️⃣ Iniciar

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

### 3️⃣ Usar

1. Abra seu navegador em **http://localhost:5000**
2. Cole a URL do site: `https://example.com`
3. Clique em **"Copiar Site"**
4. Aguarde o processamento (barra de progresso em tempo real)
5. Quando concluir:
   - **Download ZIP**: Baixa tudo em um arquivo compactado
   - **Visualizar**: Abre o site no navegador para preview

## 📸 Exemplo de Uso

```bash
# Terminal 1: Inicia o servidor
$ python run_web.py
🌐 Servidor iniciado em: http://localhost:5000

# Navegador: Acesse http://localhost:5000
# 1. Digite: https://example.com
# 2. Clique: Copiar Site
# 3. Aguarde: Barra de progresso mostra status
# 4. Pronto: Download ZIP ou Visualizar

# Os arquivos ficam em:
output/
└── example.com_2026-02-13_12-30-45/
    ├── index.html
    ├── css/
    ├── js/
    ├── images/
    └── ...
```

## 🔧 Resolvendo Problemas

### Erro: "No module named 'flask'"

```bash
pip install flask>=3.0.0 flask-cors>=4.0.0
```

### Erro: Porta 5000 já está em uso

Edite `run_web.py` e mude a porta:

```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Mude para 8080
```

### Erro: "No module named webcopy"

```bash
# Certifique-se de estar na raiz do projeto
cd WebCopy/webcopy
pip install -e .
```

## 💡 Dicas

- **Múltiplos Jobs**: Você pode iniciar várias cópias ao mesmo tempo
- **Preview Seguro**: O preview abre o site localmente (sem conexão externa)
- **ZIP Automático**: O arquivo ZIP é criado automaticamente após o download
- **Arquivos Salvos**: Todos os sites ficam em `output/` mesmo após fechar o servidor

## 📚 Mais Informações

- **[Documentação Completa da Web Interface](WEB_INTERFACE.md)**
- **[README Principal](README.md)**

## ❓ Perguntas Frequentes

**P: A CLI ainda funciona?**  
R: Sim! O comando `webcopy https://example.com` continua funcionando normalmente.

**P: Os jobs são persistidos?**  
R: Não. Se você reiniciar o servidor, perde o histórico. Os arquivos continuam em `output/`.

**P: Posso usar em produção?**  
R: A interface está em modo debug. Para produção, use um servidor WSGI (gunicorn, uwsgi).

**P: Como limpar arquivos antigos?**  
R: Atualmente é manual. Basta apagar pastas antigas em `output/`.
