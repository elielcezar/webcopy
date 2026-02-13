# Interface Web do WebCopy

Interface web moderna para copiar sites através do navegador.

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
# Se ainda não instalou
pip install -r requirements.txt

# Ou instale as novas dependências
pip install flask>=3.0.0 flask-cors>=4.0.0
```

### 2. Iniciar o Servidor

```bash
# Na raiz do projeto webcopy/
python run_web.py
```

O servidor iniciará em: **http://localhost:5000**

### 3. Usar a Interface

1. Abra seu navegador em `http://localhost:5000`
2. Digite a URL do site que deseja copiar
3. Clique em "Copiar Site"
4. Acompanhe o progresso em tempo real
5. Quando concluído:
   - Clique em "Download ZIP" para baixar o site
   - Clique em "Visualizar" para ver o preview no navegador

## 📁 Estrutura

```
webcopy/
├── src/webcopy/web/
│   ├── __init__.py
│   ├── app.py              # Flask app principal
│   ├── tasks.py            # Lógica de background
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Estilos
│   │   └── js/
│   │       └── app.js      # JavaScript
│   └── templates/
│       └── index.html      # Interface HTML
└── run_web.py             # Script de inicialização
```

## 🔌 API Endpoints

### POST `/api/copy`
Inicia processo de cópia.

**Body:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "job_id": "uuid-aqui",
  "status": "processing",
  "message": "Job iniciado com sucesso"
}
```

### GET `/api/status/<job_id>`
Consulta status de um job.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing|completed|error",
  "message": "Status message",
  "progress": 75,
  "steps": [...],
  "url": "https://example.com",
  "output_path": "/path/to/output",
  "error": null
}
```

### GET `/api/download/<job_id>`
Baixa o arquivo ZIP do site copiado.

### GET `/api/preview/<job_id>`
Abre preview do site copiado.

### GET `/api/jobs`
Lista todos os jobs (útil para debug).

## ⚙️ Configuração

### Porta Customizada

Edite `run_web.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Diretório de Saída

Por padrão, os sites são salvos em `output/`. Para mudar, edite a variável `output_dir` em `app.py`.

## 🎨 Features

- ✅ Interface moderna e responsiva
- ✅ Progresso em tempo real com polling
- ✅ Download em ZIP automático
- ✅ Preview do site no navegador
- ✅ Validação de URL no frontend e backend
- ✅ Tratamento de erros amigável
- ✅ Animações CSS suaves
- ✅ Mobile-friendly

## 🔧 Desenvolvimento

### Debug Mode

O servidor roda em modo debug por padrão. Para produção, edite:

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### CORS

Se precisar acessar de outro domínio, o Flask-CORS já está instalado. Adicione em `app.py`:

```python
from flask_cors import CORS
CORS(app)
```

## ⚠️ Limitações

- Jobs são armazenados em memória (reiniciar servidor perde histórico)
- Apenas uma cópia por vez por navegador (mas múltiplos jobs simultâneos são suportados)
- Arquivos ZIP não são limpos automaticamente (faça limpeza manual em `output/`)

## 🔮 Melhorias Futuras

- [ ] WebSockets para progresso em tempo real (sem polling)
- [ ] Persistência de jobs em banco de dados
- [ ] Histórico de downloads
- [ ] Limpeza automática de arquivos antigos
- [ ] Autenticação de usuários
- [ ] Queue system para múltiplos jobs
- [ ] Estimativa de tempo restante
- [ ] Cancelamento de jobs em andamento
