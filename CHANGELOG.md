# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.1.0] - 2026-02-13

### ✨ Adicionado

#### Interface Web Completa
- **Interface web moderna** com Flask para copiar sites através do navegador
- **Progresso em tempo real** com polling a cada 2 segundos
- **Download automático em ZIP** após conclusão
- **Preview no navegador** do site copiado
- **Design responsivo** mobile-friendly com gradientes modernos
- **Validação de URL** no frontend e backend
- **Tratamento de erros** amigável com mensagens claras

#### Arquivos Novos
- `src/webcopy/web/__init__.py` - Módulo web
- `src/webcopy/web/app.py` - Flask app principal com rotas e gerenciamento de jobs
- `src/webcopy/web/tasks.py` - Lógica de background tasks com callbacks
- `src/webcopy/web/templates/index.html` - Interface HTML com 3 estados (form, progress, result)
- `src/webcopy/web/static/css/style.css` - Estilos modernos com animações CSS
- `src/webcopy/web/static/js/app.js` - JavaScript para polling e UI dinâmica
- `run_web.py` - Script de inicialização do servidor web
- `WEB_INTERFACE.md` - Documentação completa da interface web
- `QUICKSTART.md` - Guia rápido de uso
- `test_web_interface.py` - Script de teste automatizado
- `CHANGELOG.md` - Este arquivo

#### Dependências
- `flask>=3.0.0` - Framework web
- `flask-cors>=4.0.0` - CORS para desenvolvimento

#### API Endpoints
- `GET /` - Interface HTML principal
- `POST /api/copy` - Inicia processo de cópia
- `GET /api/status/<job_id>` - Consulta status e progresso
- `GET /api/download/<job_id>` - Download do arquivo ZIP
- `GET /api/preview/<job_id>` - Preview do site copiado
- `GET /api/jobs` - Lista todos os jobs (debug)

### 🔧 Modificado

#### README.md
- Adicionada seção "Interface Web" como método recomendado
- Atualizada lista de recursos com features da interface web
- Adicionadas novas dependências (Flask)
- Atualizada seção de melhorias futuras

#### requirements.txt
- Adicionado `flask>=3.0.0`
- Adicionado `flask-cors>=4.0.0`

#### .gitignore
- Adicionado `*.zip` para ignorar arquivos ZIP gerados
- Adicionado `instance/` e `.webassets-cache` (Flask)

### 🏗️ Arquitetura

A interface web foi implementada como um módulo separado que **reutiliza toda a lógica existente** do WebCopy:

```
Interface Web (Flask)
    ↓
Background Tasks (Threading)
    ↓
Módulos Core (Downloader, Parser, Organizer)
    ↓
Output (Arquivos + ZIP)
```

**Vantagens:**
- ✅ Zero impacto no CLI existente
- ✅ Código core não foi modificado
- ✅ Fácil manutenção e extensão
- ✅ Jobs em memória (simples e eficiente para uso local)

### 📊 Complexidade

- **Arquivos novos:** 11 arquivos
- **Linhas de código:** ~1200 linhas
- **Tempo de desenvolvimento:** 4-6 horas
- **Modificações em código existente:** Nenhuma (apenas adições)

### 🎯 Uso

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
python run_web.py

# Acessar interface
# http://localhost:5000
```

---

## [1.0.0] - 2026-01-31

### ✨ Release Inicial

- Interface CLI completa com click
- Download de HTML e todos os assets
- Organização automática em pastas (CSS, JS, images, fonts, assets)
- Reescrita de URLs para funcionamento local
- Suporte a compressão Brotli e Gzip
- Extração de assets dentro de CSS
- Retry automático em falhas de rede
- Parser HTML resiliente
