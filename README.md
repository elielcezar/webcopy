# WebCopy

Ferramenta CLI em Python para fazer cópias organizadas e estruturadas de páginas web. Baixa uma página HTML e todos os seus assets (CSS, JavaScript, imagens, fontes), organizando-os em uma estrutura de pastas padronizada que funciona localmente como um site estático completo.

## 🎯 Objetivo

Criar cópias fiéis de páginas web que rodem localmente em HTML+CSS+JS, com todos os assets minimamente organizados em pastas como um projeto padrão.

## ⚙️ Arquitetura

O projeto é estruturado em módulos Python com responsabilidades bem definidas:

```
WebCopy/
├── src/webcopy/
│   ├── cli.py          # Interface CLI com click
│   ├── downloader.py   # Download HTTP com retry e suporte a Brotli
│   ├── parser.py       # Parse HTML/CSS e extração de URLs
│   └── organizer.py    # Organização de arquivos e reescrita de URLs
├── output/             # Sites baixados (ignorado no git)
├── requirements.txt    # Dependências
└── setup.py           # Configuração de instalação
```

### Fluxo de Execução

1. **Download**: Baixa HTML principal via requests
2. **Parse**: BeautifulSoup4 extrai URLs de assets (CSS, JS, imagens, fontes)
3. **Parse CSS**: Extrai URLs de dentro de arquivos CSS (`url()`)
4. **Download Assets**: Baixa cada asset sequencialmente
5. **Organização**: Salva arquivos em estrutura organizada por tipo
6. **Reescrita**: Reescreve URLs no HTML e CSS para caminhos locais
7. **Saída**: Gera site funcional em `output/dominio_timestamp/`

## 📦 Instalação

```bash
# Entre no diretório do projeto
cd WebCopy

# Instale as dependências
pip install -r requirements.txt

# Instale o pacote em modo de desenvolvimento
pip install -e .

# OU use o script de instalação:
# Windows: install.bat
# Linux/Mac: bash install.sh
```

**Nota Importante**: Se você receber o erro "No module named webcopy", certifique-se de executar `pip install -e .` na raiz do projeto (não dentro da pasta `src`).

## 🚀 Uso

### Interface Web (Recomendado) 🌐

A forma mais fácil de usar o WebCopy é através da interface web:

```bash
# Inicie o servidor web
python run_web.py

# Acesse no navegador
# http://localhost:5000
```

Depois é só inserir a URL, acompanhar o progresso e baixar o resultado!

📖 **[Documentação completa da Interface Web](WEB_INTERFACE.md)**

### Linha de Comando (CLI)

```bash
# Uso básico - baixa a página e cria diretório com timestamp
webcopy https://example.com

# Especificar nome de saída customizado
webcopy https://example.com --output meu-site

# Especificar diretório base diferente
webcopy https://example.com --output-dir meus-sites

# Ou usando Python diretamente
python -m webcopy https://example.com
```

### Exemplo Real

```bash
$ python -m webcopy https://the7.io/fse-crypto/

[WebCopy] Iniciando copia de: https://the7.io/fse-crypto/
[+] Baixando pagina principal...
[+] Analisando pagina e extraindo assets...
    Encontrados: 9 CSS, 7 JS, 123 imagens, 0 fontes, 1 outros
[+] Baixando arquivos CSS...
[+] Baixando arquivos JavaScript...
[+] Baixando imagens...
[+] Baixando outros recursos...
[+] Reescrevendo URLs no HTML...
[+] Reescrevendo URLs nos arquivos CSS...

[OK] Copia concluida com sucesso!
[>] Arquivos salvos em: output/the7.io_2026-01-31_12-30-45

Para visualizar, abra o arquivo index.html no navegador.
```

## 📁 Estrutura de Saída

Cada site baixado será organizado assim:

```
output/
└── example.com_2026-01-31_12-30-45/
    ├── index.html          # HTML principal (com URLs reescritas)
    ├── css/               # Todos os arquivos CSS
    │   ├── style.css
    │   └── main.css
    ├── js/                # Todos os arquivos JavaScript
    │   ├── app.js
    │   └── vendor.js
    ├── images/            # Imagens (jpg, png, gif, svg, webp)
    │   ├── logo.svg
    │   └── hero.webp
    ├── fonts/             # Fontes web (woff, woff2, ttf, otf)
    │   └── custom-font.woff2
    └── assets/            # Outros recursos (favicon, etc)
        └── favicon.ico
```

## ✨ Recursos

### Interface & Usabilidade
- ✅ **Interface Web moderna e amigável** (Flask + HTML/CSS/JS)
- ✅ **Progresso em tempo real** com status detalhado
- ✅ **Download em ZIP** do site completo
- ✅ **Preview no navegador** antes de baixar
- ✅ Interface CLI completa (click)

### Funcionalidades Core
- ✅ Download de HTML e todos os assets referenciados
- ✅ Organização automática por tipo de arquivo (CSS, JS, images, fonts, assets)
- ✅ Reescrita inteligente de URLs para funcionamento local
- ✅ Suporte a recursos de CDNs externos (baixa e hospeda localmente)
- ✅ Tratamento de URLs relativas e absolutas
- ✅ Suporte a compressão Brotli (br) e Gzip
- ✅ Extração de assets dentro de arquivos CSS (`url()`, `@font-face`)
- ✅ Retry automático em caso de falhas de rede
- ✅ Parser HTML resiliente (html.parser nativo do Python)
- ✅ Nomes de arquivo únicos para evitar colisões

## 🔧 Detalhes Técnicos

### Gerenciamento de Compressão

O projeto suporta automaticamente:
- **Gzip** (padrão do requests)
- **Brotli** (requer `brotli` instalado)

Sites modernos como [the7.io](https://the7.io/fse-crypto/) usam compressão Brotli (`Content-Encoding: br`). A biblioteca `brotli` é essencial para descomprimir esse conteúdo corretamente.

### Reescrita de URLs

O sistema mantém um dicionário mapeando URLs originais para caminhos locais:

```python
{
  'https://example.com/style.css': 'css/style.css',
  'https://cdn.example.com/app.js': 'js/app.js',
  '/images/logo.png': 'images/logo.png'
}
```

Todas as referências no HTML e CSS são reescritas para usar esses caminhos locais.

### Organização de Arquivos

- **CSS**: Identificado por extensão `.css` e Content-Type
- **JavaScript**: Extensão `.js` e tags `<script>`
- **Imagens**: Extensões `.jpg`, `.png`, `.gif`, `.svg`, `.webp`, etc.
- **Fontes**: Extensões `.woff`, `.woff2`, `.ttf`, `.otf`, `.eot`
- **Outros**: Favicons, manifestos, e recursos diversos

### Parser HTML

Usa `html.parser` (nativo do Python) em vez de `lxml` para:
- Melhor preservação do HTML original
- Menos problemas de encoding
- Funciona sem dependências C compiladas

## ⚠️ Limitações

- Apenas baixa a página especificada (não faz crawling de links internos)
- Não suporta SPAs (Single Page Applications) com conteúdo carregado via JavaScript
- Não processa JavaScript que carrega assets dinamicamente (fetch, XHR)
- Recursos que requerem autenticação não serão baixados
- Sites com proteção anti-bot agressiva podem bloquear o acesso
- JavaScript inline e eventos podem não funcionar corretamente offline

## 🐛 Solução de Problemas

### "No module named webcopy"

**Causa**: O pacote não está instalado ou foi instalado em um ambiente Python diferente.

**Solução**:
```bash
# Certifique-se de estar na raiz do projeto
cd WebCopy

# Instale em modo de desenvolvimento
pip install -e .

# Ou reinstale
pip uninstall webcopy -y && pip install -e .
```

### HTML com caracteres estranhos/corrompidos

**Causa**: Site usa compressão Brotli sem a biblioteca `brotli` instalada.

**Solução**:
```bash
pip install brotli
```

Após instalar, execute o webcopy novamente. O HTML será decodificado corretamente.

### Assets não são baixados

**Causa Comum**: 
1. URLs relativas não resolvidas corretamente
2. Assets protegidos por CORS ou autenticação
3. URLs dinâmicas geradas por JavaScript

**Verificação**:
- Confira os avisos `[!]` no console durante o download
- Assets de CDNs externos podem ter rate limiting

### Site não funciona localmente

**Possíveis causas**:
1. JavaScript requer servidor (APIs, fetch, etc.)
2. Recursos bloqueados por CORS no browser
3. Service Workers tentando fazer cache

**Dica**: Abra com um servidor local simples:
```bash
cd output/site-baixado
python -m http.server 8000
# Acesse http://localhost:8000
```

## 📚 Dependências

- **Python 3.8+** - Linguagem base
- **requests** (>=2.31.0) - Requisições HTTP com retry e sessões
- **beautifulsoup4** (>=4.12.0) - Parse de HTML e extração de elementos
- **lxml** (>=5.0.0) - Parser XML/HTML performático
- **click** (>=8.1.0) - Interface CLI amigável
- **brotli** (>=1.0.0) - Suporte a compressão Brotli (essencial!)
- **flask** (>=3.0.0) - Interface web
- **flask-cors** (>=4.0.0) - CORS para desenvolvimento web

## 🔮 Melhorias Futuras

### ✅ Recentemente Implementadas
- ✅ Interface web com Flask (Janeiro 2026)
- ✅ Progresso em tempo real via polling
- ✅ Download em ZIP
- ✅ Preview no navegador

### Não Implementadas (Escopo Básico)
- [ ] Crawling de múltiplas páginas
- [ ] Download paralelo (threading/async)
- [ ] Minificação de assets
- [ ] Suporte para SPAs (Selenium/Playwright)
- [ ] Versionamento de sites

### Melhorias na Interface Web
- [ ] WebSockets para progresso (substituir polling)
- [ ] Persistência de jobs em banco de dados
- [ ] Histórico de downloads
- [ ] Autenticação de usuários
- [ ] Cancelamento de jobs em andamento

### Implementações Possíveis
- [ ] Modo verboso com mais detalhes de debug
- [ ] Blacklist/whitelist de domínios
- [ ] Limite de tamanho de arquivo
- [ ] Estatísticas de download (tempo, tamanho, etc.)
- [ ] Configuração via arquivo (config.yaml)

## 🤝 Contexto para IAs

Este projeto foi desenvolvido para criar cópias organizadas de páginas web para uso offline. A principal descoberta durante o desenvolvimento foi a necessidade de suporte a **compressão Brotli**, que sites modernos usam extensivamente.

### Decisões de Design

1. **html.parser vs lxml**: Escolhido html.parser para evitar problemas de encoding
2. **Download sequencial**: Simplicidade sobre performance (evita rate limiting)
3. **Estrutura fixa**: Pastas padronizadas facilitam navegação
4. **Sem crawling**: Mantém escopo controlado e previsível
5. **Reescrita completa**: Garante funcionamento offline sem dependências externas

### Problemas Resolvidos

1. **Brotli Compression**: Sites modernos (Cloudflare, WordPress) usam Brotli
2. **URLs relativas**: Conversão correta usando `urllib.parse.urljoin`
3. **Assets em CSS**: Parser recursivo extrai `url()` e `@font-face`
4. **Encoding**: UTF-8 com fallback para apparent_encoding
5. **Colisão de nomes**: Sistema de nomes únicos por hash ou contador

## 📄 Licença

MIT License - Sinta-se livre para usar, modificar e distribuir.

## 👨‍💻 Desenvolvimento

Desenvolvido em Janeiro de 2026 como ferramenta para preservação de conteúdo web e estudo offline.
