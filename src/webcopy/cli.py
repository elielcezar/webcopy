"""
CLI Module - Interface de linha de comando para o WebCopy.
"""

import click
import sys
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

from .downloader import Downloader
from .parser import HTMLParser
from .organizer import FileOrganizer


def validate_url(ctx, param, value):
    """Valida se a URL fornecida é válida."""
    try:
        result = urlparse(value)
        if not all([result.scheme, result.netloc]):
            raise click.BadParameter("URL inválida. Use formato: https://example.com")
        if result.scheme not in ("http", "https"):
            raise click.BadParameter("URL deve começar com http:// ou https://")
        return value
    except Exception as e:
        raise click.BadParameter(f"URL inválida: {e}")


def generate_output_name(url: str) -> str:
    """Gera nome do diretório de saída baseado no domínio e timestamp."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_")  # Remove : de portas
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{domain}_{timestamp}"


@click.command()
@click.argument("url", callback=validate_url)
@click.option(
    "--output", "-o",
    default=None,
    help="Nome customizado para o diretório de saída"
)
@click.option(
    "--output-dir", "-d",
    default="output",
    help="Diretório base para salvar os sites (padrão: output)"
)
def main(url: str, output: str, output_dir: str):
    """
    WebCopy - Faz cópia organizada de páginas web.
    
    Baixa a página HTML especificada e todos os seus assets (CSS, JS, imagens),
    organizando-os em uma estrutura de pastas padronizada.
    
    Exemplo:
    
        webcopy https://example.com
        
        webcopy https://example.com --output meu-site
    """
    click.echo(f"[WebCopy] Iniciando copia de: {url}")
    click.echo()
    
    # Determina o nome do diretório de saída
    if output:
        site_dir_name = output
    else:
        site_dir_name = generate_output_name(url)
    
    # Cria o caminho completo
    base_path = Path(output_dir)
    site_path = base_path / site_dir_name
    
    try:
        # Inicializa os módulos
        downloader = Downloader()
        parser = HTMLParser(url)
        organizer = FileOrganizer(site_path)
        
        # 1. Baixa o HTML principal
        click.echo("[+] Baixando pagina principal...")
        html_content = downloader.download_text(url)
        
        if not html_content:
            click.echo("[ERRO] Nao foi possivel baixar a pagina.", err=True)
            sys.exit(1)
        
        # 2. Faz parse do HTML e extrai URLs de assets
        click.echo("[+] Analisando pagina e extraindo assets...")
        assets = parser.extract_assets(html_content)
        
        click.echo(f"    Encontrados: {len(assets['css'])} CSS, {len(assets['js'])} JS, "
                   f"{len(assets['images'])} imagens, {len(assets['fonts'])} fontes, "
                   f"{len(assets['other'])} outros")
        
        # 3. Cria estrutura de diretórios
        organizer.create_structure()
        
        # 4. Baixa e salva cada asset
        url_map = {}  # Mapeia URL original -> caminho local
        
        # Baixa CSS
        if assets['css']:
            click.echo("[+] Baixando arquivos CSS...")
            for css_url in assets['css']:
                content = downloader.download_bytes(css_url)
                if content:
                    local_path = organizer.save_css(css_url, content)
                    url_map[css_url] = local_path
                    
                    # Extrai assets de dentro do CSS
                    css_text = content.decode('utf-8', errors='ignore')
                    css_assets = parser.extract_css_urls(css_text, css_url)
                    
                    for asset_url in css_assets:
                        if asset_url not in url_map:
                            asset_content = downloader.download_bytes(asset_url)
                            if asset_content:
                                asset_local = organizer.save_asset(asset_url, asset_content)
                                url_map[asset_url] = asset_local
        
        # Baixa JavaScript
        if assets['js']:
            click.echo("[+] Baixando arquivos JavaScript...")
            for js_url in assets['js']:
                content = downloader.download_bytes(js_url)
                if content:
                    local_path = organizer.save_js(js_url, content)
                    url_map[js_url] = local_path
        
        # Baixa imagens
        if assets['images']:
            click.echo("[+] Baixando imagens...")
            for img_url in assets['images']:
                content = downloader.download_bytes(img_url)
                if content:
                    local_path = organizer.save_image(img_url, content)
                    url_map[img_url] = local_path
        
        # Baixa fontes
        if assets['fonts']:
            click.echo("[+] Baixando fontes...")
            for font_url in assets['fonts']:
                content = downloader.download_bytes(font_url)
                if content:
                    local_path = organizer.save_font(font_url, content)
                    url_map[font_url] = font_url
        
        # Baixa outros assets
        if assets['other']:
            click.echo("[+] Baixando outros recursos...")
            for other_url in assets['other']:
                content = downloader.download_bytes(other_url)
                if content:
                    local_path = organizer.save_other(other_url, content)
                    url_map[other_url] = local_path
        
        # 5. Reescreve URLs no HTML
        click.echo("[+] Reescrevendo URLs no HTML...")
        if url_map:
            modified_html = parser.rewrite_html_urls(html_content, url_map)
        else:
            # Se não há assets, usa HTML original sem modificações
            modified_html = html_content
        
        # 6. Reescreve URLs nos arquivos CSS
        click.echo("[+] Reescrevendo URLs nos arquivos CSS...")
        organizer.rewrite_css_urls(url_map)
        
        # 7. Salva o HTML final
        organizer.save_html(modified_html)
        
        click.echo()
        click.echo(f"[OK] Copia concluida com sucesso!")
        click.echo(f"[>] Arquivos salvos em: {site_path.absolute()}")
        click.echo()
        click.echo("Para visualizar, abra o arquivo index.html no navegador.")
        
    except KeyboardInterrupt:
        click.echo("\n[!] Operacao cancelada pelo usuario.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"[ERRO] {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
