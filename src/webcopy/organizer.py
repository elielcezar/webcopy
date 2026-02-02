"""
Organizer Module - Organiza arquivos baixados em estrutura de pastas padronizada.
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse, unquote


class FileOrganizer:
    """Classe responsável por organizar arquivos em estrutura de pastas."""
    
    # Extensões conhecidas por tipo
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff'}
    FONT_EXTENSIONS = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}
    
    # Mapeamento de Content-Type para extensão
    CONTENT_TYPE_MAP = {
        'text/css': '.css',
        'application/javascript': '.js',
        'text/javascript': '.js',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/svg+xml': '.svg',
        'image/webp': '.webp',
        'image/x-icon': '.ico',
        'font/woff': '.woff',
        'font/woff2': '.woff2',
        'application/font-woff': '.woff',
        'application/font-woff2': '.woff2',
        'font/ttf': '.ttf',
        'font/otf': '.otf',
    }
    
    def __init__(self, output_path: Path):
        """
        Inicializa o organizador.
        
        Args:
            output_path: Caminho base para salvar os arquivos.
        """
        self.output_path = Path(output_path)
        self.css_dir = self.output_path / 'css'
        self.js_dir = self.output_path / 'js'
        self.images_dir = self.output_path / 'images'
        self.fonts_dir = self.output_path / 'fonts'
        self.assets_dir = self.output_path / 'assets'
        
        # Mapeia nomes de arquivos para evitar colisões
        self._filename_counter: Dict[str, int] = {}
        
        # Mapeia URLs para caminhos locais salvos
        self._saved_files: Dict[str, str] = {}
    
    def create_structure(self):
        """Cria a estrutura de diretórios."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.css_dir.mkdir(exist_ok=True)
        self.js_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.fonts_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
    
    def _get_extension(self, url: str) -> str:
        """Extrai a extensão de um arquivo da URL."""
        parsed = urlparse(url)
        path = unquote(parsed.path).lower()
        
        if '.' in path:
            ext = '.' + path.rsplit('.', 1)[-1]
            # Remove query strings que podem ter vazado
            ext = ext.split('?')[0].split('#')[0]
            # Limita tamanho da extensão
            if len(ext) <= 6:
                return ext
        return ""
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza um nome de arquivo removendo caracteres inválidos.
        
        Args:
            filename: Nome original do arquivo.
            
        Returns:
            Nome sanitizado.
        """
        # Remove caracteres inválidos para sistemas de arquivos
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove query strings e fragments
        filename = filename.split('?')[0].split('#')[0]
        # Limita tamanho
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            name = name[:90]
            filename = f"{name}.{ext}" if ext else name
        return filename
    
    def _get_filename_from_url(self, url: str) -> str:
        """
        Extrai o nome do arquivo de uma URL.
        
        Args:
            url: URL do recurso.
            
        Returns:
            Nome do arquivo.
        """
        parsed = urlparse(url)
        path = unquote(parsed.path)
        
        # Pega o último segmento do path
        if path and path != '/':
            filename = path.rstrip('/').split('/')[-1]
            if filename:
                return self._sanitize_filename(filename)
        
        # Se não conseguiu extrair, gera um nome baseado no hash da URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        ext = self._get_extension(url) or ''
        return f"file_{url_hash}{ext}"
    
    def _get_unique_filename(self, directory: Path, filename: str) -> str:
        """
        Garante que o nome do arquivo seja único no diretório.
        
        Args:
            directory: Diretório onde o arquivo será salvo.
            filename: Nome desejado.
            
        Returns:
            Nome único.
        """
        full_path = directory / filename
        
        if not full_path.exists():
            return filename
        
        # Adiciona contador para tornar único
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter}.{ext}" if ext else f"{name}_{counter}"
            if not (directory / new_filename).exists():
                return new_filename
            counter += 1
    
    def _save_file(self, directory: Path, url: str, content: bytes) -> str:
        """
        Salva um arquivo no diretório especificado.
        
        Args:
            directory: Diretório de destino.
            url: URL original do recurso.
            content: Conteúdo do arquivo em bytes.
            
        Returns:
            Caminho relativo do arquivo salvo (em relação ao output_path).
        """
        filename = self._get_filename_from_url(url)
        unique_filename = self._get_unique_filename(directory, filename)
        
        file_path = directory / unique_filename
        file_path.write_bytes(content)
        
        # Calcula caminho relativo ao output_path
        relative_path = file_path.relative_to(self.output_path)
        local_path = str(relative_path).replace('\\', '/')
        
        # Salva no mapa
        self._saved_files[url] = local_path
        
        return local_path
    
    def save_css(self, url: str, content: bytes) -> str:
        """Salva um arquivo CSS."""
        return self._save_file(self.css_dir, url, content)
    
    def save_js(self, url: str, content: bytes) -> str:
        """Salva um arquivo JavaScript."""
        return self._save_file(self.js_dir, url, content)
    
    def save_image(self, url: str, content: bytes) -> str:
        """Salva uma imagem."""
        return self._save_file(self.images_dir, url, content)
    
    def save_font(self, url: str, content: bytes) -> str:
        """Salva uma fonte."""
        return self._save_file(self.fonts_dir, url, content)
    
    def save_other(self, url: str, content: bytes) -> str:
        """Salva outros tipos de assets."""
        return self._save_file(self.assets_dir, url, content)
    
    def save_asset(self, url: str, content: bytes) -> str:
        """
        Salva um asset automaticamente categorizando pelo tipo.
        
        Args:
            url: URL do recurso.
            content: Conteúdo em bytes.
            
        Returns:
            Caminho relativo do arquivo salvo.
        """
        ext = self._get_extension(url)
        
        if ext == '.css':
            return self.save_css(url, content)
        elif ext == '.js':
            return self.save_js(url, content)
        elif ext in self.IMAGE_EXTENSIONS:
            return self.save_image(url, content)
        elif ext in self.FONT_EXTENSIONS:
            return self.save_font(url, content)
        else:
            return self.save_other(url, content)
    
    def save_html(self, content: str, filename: str = "index.html"):
        """
        Salva o arquivo HTML principal.
        
        Args:
            content: Conteúdo HTML.
            filename: Nome do arquivo (padrão: index.html).
        """
        file_path = self.output_path / filename
        file_path.write_text(content, encoding='utf-8')
    
    def rewrite_css_urls(self, url_map: Dict[str, str]):
        """
        Reescreve URLs dentro de todos os arquivos CSS salvos.
        
        Args:
            url_map: Mapa de URL original -> caminho local.
        """
        css_url_pattern = re.compile(r'url\(["\']?([^"\')\s]+)["\']?\)', re.IGNORECASE)
        
        for css_file in self.css_dir.glob('*.css'):
            try:
                content = css_file.read_text(encoding='utf-8', errors='ignore')
                modified = False
                
                def replace_url(match):
                    nonlocal modified
                    original_url = match.group(1)
                    
                    # Ignora data URLs
                    if original_url.startswith('data:'):
                        return match.group(0)
                    
                    # Procura no mapa
                    for orig_url, local_path in url_map.items():
                        # Verifica se a URL do CSS termina com o mesmo caminho
                        if original_url in orig_url or orig_url.endswith(original_url):
                            modified = True
                            # Calcula caminho relativo do CSS para o asset
                            relative_path = '../' + local_path
                            return f'url("{relative_path}")'
                    
                    return match.group(0)
                
                new_content = css_url_pattern.sub(replace_url, content)
                
                if modified:
                    css_file.write_text(new_content, encoding='utf-8')
                    
            except Exception as e:
                # Ignora erros de encoding em arquivos CSS
                pass
    
    def get_saved_files(self) -> Dict[str, str]:
        """Retorna o mapa de URLs para caminhos locais."""
        return self._saved_files.copy()
