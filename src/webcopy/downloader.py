"""
Downloader Module - Gerencia requisições HTTP para baixar páginas e assets.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional
import click


class Downloader:
    """Classe responsável por fazer downloads de recursos web."""
    
    # User-Agent que simula um navegador real
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Inicializa o downloader.
        
        Args:
            timeout: Timeout em segundos para cada requisição.
            max_retries: Número máximo de tentativas em caso de falha.
        """
        self.timeout = timeout
        self.session = self._create_session(max_retries)
        self._downloaded_urls = set()  # Cache de URLs já baixadas
    
    def _create_session(self, max_retries: int) -> requests.Session:
        """Cria uma sessão HTTP com retry logic."""
        session = requests.Session()
        
        # Configura retry para falhas de rede
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers padrão
        session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
        })
        
        return session
    
    def download_text(self, url: str) -> Optional[str]:
        """
        Baixa uma URL e retorna o conteúdo como texto.
        
        Args:
            url: URL para baixar.
            
        Returns:
            Conteúdo da página como string, ou None se falhar.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Detecta encoding correto
            # Se o servidor não especificou encoding, tenta detectar
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding or 'utf-8'
            
            # Usa .text que já lida com decodificação automática
            return response.text
            
        except requests.exceptions.Timeout:
            click.echo(f"    [!] Timeout ao baixar: {url}", err=True)
            return None
        except requests.exceptions.HTTPError as e:
            click.echo(f"    [!] Erro HTTP {e.response.status_code}: {url}", err=True)
            return None
        except requests.exceptions.RequestException as e:
            click.echo(f"    [!] Erro ao baixar {url}: {e}", err=True)
            return None
        except Exception as e:
            click.echo(f"    [!] Erro inesperado ao baixar {url}: {e}", err=True)
            return None
    
    def download_bytes(self, url: str) -> Optional[bytes]:
        """
        Baixa uma URL e retorna o conteúdo como bytes.
        
        Args:
            url: URL para baixar.
            
        Returns:
            Conteúdo como bytes, ou None se falhar.
        """
        # Evita baixar a mesma URL duas vezes
        if url in self._downloaded_urls:
            return None
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self._downloaded_urls.add(url)
            return response.content
            
        except requests.exceptions.Timeout:
            click.echo(f"    [!] Timeout ao baixar: {url}", err=True)
            return None
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            click.echo(f"    [!] Erro HTTP {status}: {url}", err=True)
            return None
        except requests.exceptions.RequestException as e:
            click.echo(f"    [!] Erro ao baixar: {url}", err=True)
            return None
    
    def get_content_type(self, url: str) -> Optional[str]:
        """
        Faz uma requisição HEAD para obter o Content-Type de uma URL.
        
        Args:
            url: URL para verificar.
            
        Returns:
            Content-Type ou None se falhar.
        """
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            return response.headers.get('Content-Type', '').split(';')[0].strip()
        except:
            return None
    
    def is_downloaded(self, url: str) -> bool:
        """Verifica se uma URL já foi baixada."""
        return url in self._downloaded_urls
