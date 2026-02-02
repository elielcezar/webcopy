"""
Parser Module - Analisa HTML e CSS para extrair URLs de assets.
"""

import re
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class HTMLParser:
    """Classe responsável por parsear HTML e extrair URLs de assets."""
    
    # Extensões conhecidas por tipo
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff'}
    FONT_EXTENSIONS = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}
    
    # Regex para extrair url() de CSS
    CSS_URL_PATTERN = re.compile(r'url\(["\']?([^"\')\s]+)["\']?\)', re.IGNORECASE)
    
    def __init__(self, base_url: str):
        """
        Inicializa o parser.
        
        Args:
            base_url: URL base para resolver URLs relativas.
        """
        self.base_url = base_url
        self._soup = None
    
    def _resolve_url(self, url: str, context_url: str = None) -> str:
        """
        Resolve uma URL relativa para absoluta.
        
        Args:
            url: URL a resolver (pode ser relativa ou absoluta).
            context_url: URL de contexto (para assets dentro de CSS).
            
        Returns:
            URL absoluta.
        """
        if not url:
            return ""
        
        # Ignora data URLs e javascript
        if url.startswith(('data:', 'javascript:', 'mailto:', '#')):
            return ""
        
        # Remove espaços em branco
        url = url.strip()
        
        # Usa URL de contexto ou base
        base = context_url if context_url else self.base_url
        
        return urljoin(base, url)
    
    def _get_extension(self, url: str) -> str:
        """Extrai a extensão de um arquivo da URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Remove query string para pegar extensão
        if '.' in path:
            ext = '.' + path.rsplit('.', 1)[-1]
            # Limita tamanho da extensão (evita falsos positivos)
            if len(ext) <= 6:
                return ext
        return ""
    
    def _categorize_url(self, url: str) -> str:
        """
        Categoriza uma URL pelo tipo de asset.
        
        Returns:
            'css', 'js', 'images', 'fonts', ou 'other'
        """
        ext = self._get_extension(url)
        
        if ext == '.css':
            return 'css'
        elif ext == '.js':
            return 'js'
        elif ext in self.IMAGE_EXTENSIONS:
            return 'images'
        elif ext in self.FONT_EXTENSIONS:
            return 'fonts'
        else:
            return 'other'
    
    def extract_assets(self, html_content: str) -> Dict[str, List[str]]:
        """
        Extrai todas as URLs de assets do HTML.
        
        Args:
            html_content: Conteúdo HTML a analisar.
            
        Returns:
            Dicionário com listas de URLs por tipo:
            {'css': [...], 'js': [...], 'images': [...], 'fonts': [...], 'other': [...]}
        """
        self._soup = BeautifulSoup(html_content, 'html.parser')
        
        assets: Dict[str, Set[str]] = {
            'css': set(),
            'js': set(),
            'images': set(),
            'fonts': set(),
            'other': set()
        }
        
        # Extrai CSS de <link rel="stylesheet">
        for link in self._soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                url = self._resolve_url(href)
                if url:
                    assets['css'].add(url)
        
        # Extrai CSS de <link> sem rel mas com .css
        for link in self._soup.find_all('link', href=True):
            href = link.get('href', '')
            if '.css' in href.lower():
                url = self._resolve_url(href)
                if url:
                    assets['css'].add(url)
        
        # Extrai JavaScript de <script src>
        for script in self._soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                url = self._resolve_url(src)
                if url:
                    assets['js'].add(url)
        
        # Extrai imagens de <img src> e <img srcset>
        for img in self._soup.find_all('img'):
            # src principal
            src = img.get('src')
            if src:
                url = self._resolve_url(src)
                if url and not url.startswith('data:'):
                    assets['images'].add(url)
            
            # srcset (múltiplas resoluções)
            srcset = img.get('srcset')
            if srcset:
                for item in srcset.split(','):
                    parts = item.strip().split()
                    if parts:
                        url = self._resolve_url(parts[0])
                        if url and not url.startswith('data:'):
                            assets['images'].add(url)
        
        # Extrai imagens de <source> (picture element)
        for source in self._soup.find_all('source'):
            srcset = source.get('srcset')
            if srcset:
                for item in srcset.split(','):
                    parts = item.strip().split()
                    if parts:
                        url = self._resolve_url(parts[0])
                        if url and not url.startswith('data:'):
                            assets['images'].add(url)
        
        # Extrai favicon e outros ícones
        for link in self._soup.find_all('link', rel=True):
            rel = ' '.join(link.get('rel', []))
            if 'icon' in rel.lower():
                href = link.get('href')
                if href:
                    url = self._resolve_url(href)
                    if url:
                        assets['other'].add(url)
        
        # Extrai imagens de background em style inline
        for tag in self._soup.find_all(style=True):
            style = tag.get('style', '')
            for match in self.CSS_URL_PATTERN.findall(style):
                url = self._resolve_url(match)
                if url:
                    category = self._categorize_url(url)
                    assets[category].add(url)
        
        # Extrai URLs de <style> tags
        for style_tag in self._soup.find_all('style'):
            if style_tag.string:
                for match in self.CSS_URL_PATTERN.findall(style_tag.string):
                    url = self._resolve_url(match)
                    if url:
                        category = self._categorize_url(url)
                        assets[category].add(url)
        
        # Extrai preload/prefetch de recursos
        for link in self._soup.find_all('link', rel=lambda x: x and ('preload' in x or 'prefetch' in x)):
            href = link.get('href')
            if href:
                url = self._resolve_url(href)
                if url:
                    category = self._categorize_url(url)
                    assets[category].add(url)
        
        # Converte sets para listas ordenadas
        return {k: sorted(list(v)) for k, v in assets.items()}
    
    def extract_css_urls(self, css_content: str, css_url: str) -> List[str]:
        """
        Extrai todas as URLs de dentro de um arquivo CSS.
        
        Args:
            css_content: Conteúdo do arquivo CSS.
            css_url: URL do arquivo CSS (para resolver URLs relativas).
            
        Returns:
            Lista de URLs absolutas encontradas.
        """
        urls = []
        
        for match in self.CSS_URL_PATTERN.findall(css_content):
            url = self._resolve_url(match, css_url)
            if url:
                urls.append(url)
        
        return urls
    
    def rewrite_html_urls(self, html_content: str, url_map: Dict[str, str]) -> str:
        """
        Reescreve todas as URLs no HTML para apontar para caminhos locais.
        
        Args:
            html_content: Conteúdo HTML original.
            url_map: Mapa de URL original -> caminho local.
            
        Returns:
            HTML com URLs reescritas.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Reescreve <link href>
        for link in soup.find_all('link', href=True):
            original_href = link.get('href')
            absolute_url = self._resolve_url(original_href)
            if absolute_url in url_map:
                link['href'] = url_map[absolute_url]
        
        # Reescreve <script src>
        for script in soup.find_all('script', src=True):
            original_src = script.get('src')
            absolute_url = self._resolve_url(original_src)
            if absolute_url in url_map:
                script['src'] = url_map[absolute_url]
        
        # Reescreve <img src>
        for img in soup.find_all('img', src=True):
            original_src = img.get('src')
            if not original_src.startswith('data:'):
                absolute_url = self._resolve_url(original_src)
                if absolute_url in url_map:
                    img['src'] = url_map[absolute_url]
        
        # Reescreve <img srcset>
        for img in soup.find_all('img', srcset=True):
            srcset = img.get('srcset')
            new_srcset_parts = []
            for item in srcset.split(','):
                parts = item.strip().split()
                if parts:
                    original_url = parts[0]
                    absolute_url = self._resolve_url(original_url)
                    if absolute_url in url_map:
                        parts[0] = url_map[absolute_url]
                    new_srcset_parts.append(' '.join(parts))
            img['srcset'] = ', '.join(new_srcset_parts)
        
        # Reescreve <source srcset>
        for source in soup.find_all('source', srcset=True):
            srcset = source.get('srcset')
            new_srcset_parts = []
            for item in srcset.split(','):
                parts = item.strip().split()
                if parts:
                    original_url = parts[0]
                    absolute_url = self._resolve_url(original_url)
                    if absolute_url in url_map:
                        parts[0] = url_map[absolute_url]
                    new_srcset_parts.append(' '.join(parts))
            source['srcset'] = ', '.join(new_srcset_parts)
        
        # Reescreve style inline com url()
        for tag in soup.find_all(style=True):
            style = tag.get('style', '')
            new_style = self._rewrite_css_urls(style, url_map)
            if new_style != style:
                tag['style'] = new_style
        
        # Reescreve <style> tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                new_css = self._rewrite_css_urls(style_tag.string, url_map)
                style_tag.string = new_css
        
        # Retorna HTML sem formatação adicional para preservar o original
        return str(soup)
    
    def _rewrite_css_urls(self, css_content: str, url_map: Dict[str, str]) -> str:
        """
        Reescreve URLs url() em conteúdo CSS.
        
        Args:
            css_content: Conteúdo CSS.
            url_map: Mapa de URL -> caminho local.
            
        Returns:
            CSS com URLs reescritas.
        """
        def replace_url(match):
            original_url = match.group(1)
            absolute_url = self._resolve_url(original_url)
            
            if absolute_url in url_map:
                return f'url("{url_map[absolute_url]}")'
            return match.group(0)
        
        return self.CSS_URL_PATTERN.sub(replace_url, css_content)
