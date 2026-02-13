"""
Tasks Module - Lógica de processamento em background para o WebCopy Web.
"""

import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import Callable, Optional, Dict, Any

# Import dos módulos core do WebCopy
from ..downloader import Downloader
from ..parser import HTMLParser
from ..organizer import FileOrganizer


def generate_output_name(url: str) -> str:
    """Gera nome do diretório de saída baseado no domínio e timestamp."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace(":", "_")  # Remove : de portas
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{domain}_{timestamp}"


def process_website(
    url: str,
    output_dir: str = "output",
    output_name: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Processa uma URL e faz download completo do site.
    
    Args:
        url: URL da página a ser copiada
        output_dir: Diretório base para salvar (padrão: output)
        output_name: Nome customizado para o diretório de saída
        progress_callback: Função callback para reportar progresso
    
    Returns:
        Dict com informações do resultado (success, path, error, etc.)
    """
    result = {
        'success': False,
        'url': url,
        'output_path': None,
        'error': None
    }
    
    def update_progress(message: str, progress: int = 0, step_status: str = 'current', steps: list = None):
        """Helper para atualizar progresso."""
        if progress_callback:
            progress_callback({
                'message': message,
                'progress': progress,
                'step_status': step_status,
                'steps': steps or []
            })
    
    try:
        # Determina o nome do diretório de saída
        if output_name:
            site_dir_name = output_name
        else:
            site_dir_name = generate_output_name(url)
        
        # Cria o caminho completo
        base_path = Path(output_dir)
        site_path = base_path / site_dir_name
        
        steps = []
        
        # 1. Baixa o HTML principal
        update_progress('Baixando página principal...', 5, 'current', steps)
        steps.append({'message': 'Baixar página principal', 'status': 'current'})
        
        downloader = Downloader()
        parser = HTMLParser(url)
        organizer = FileOrganizer(site_path)
        
        html_content = downloader.download_text(url)
        
        if not html_content:
            result['error'] = 'Não foi possível baixar a página'
            return result
        
        steps[-1]['status'] = 'completed'
        
        # 2. Faz parse do HTML e extrai URLs de assets
        update_progress('Analisando página e extraindo assets...', 10, 'current', steps)
        steps.append({'message': 'Analisar página', 'status': 'current'})
        
        assets = parser.extract_assets(html_content)
        
        total_assets = (
            len(assets['css']) + 
            len(assets['js']) + 
            len(assets['images']) + 
            len(assets['fonts']) + 
            len(assets['other'])
        )
        
        steps[-1]['status'] = 'completed'
        steps.append({
            'message': f'Encontrados: {len(assets["css"])} CSS, {len(assets["js"])} JS, '
                      f'{len(assets["images"])} imagens, {len(assets["fonts"])} fontes',
            'status': 'completed'
        })
        
        # 3. Cria estrutura de diretórios
        organizer.create_structure()
        
        # 4. Baixa e salva cada asset
        url_map = {}  # Mapeia URL original -> caminho local
        downloaded_count = 0
        
        # Baixa CSS
        if assets['css']:
            steps.append({'message': f'Baixar CSS (0/{len(assets["css"])})', 'status': 'current'})
            update_progress(f'Baixando arquivos CSS...', 15, 'current', steps)
            
            for idx, css_url in enumerate(assets['css'], 1):
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
                
                downloaded_count += 1
                progress = 15 + int((downloaded_count / max(total_assets, 1)) * 50)
                steps[-1]['message'] = f'Baixar CSS ({idx}/{len(assets["css"])})'
                update_progress(f'Baixando CSS... {idx}/{len(assets["css"])}', progress, 'current', steps)
            
            steps[-1]['status'] = 'completed'
        
        # Baixa JavaScript
        if assets['js']:
            steps.append({'message': f'Baixar JavaScript (0/{len(assets["js"])})', 'status': 'current'})
            update_progress('Baixando arquivos JavaScript...', 30, 'current', steps)
            
            for idx, js_url in enumerate(assets['js'], 1):
                content = downloader.download_bytes(js_url)
                if content:
                    local_path = organizer.save_js(js_url, content)
                    url_map[js_url] = local_path
                
                downloaded_count += 1
                progress = 15 + int((downloaded_count / max(total_assets, 1)) * 50)
                steps[-1]['message'] = f'Baixar JavaScript ({idx}/{len(assets["js"])})'
                update_progress(f'Baixando JS... {idx}/{len(assets["js"])}', progress, 'current', steps)
            
            steps[-1]['status'] = 'completed'
        
        # Baixa imagens
        if assets['images']:
            steps.append({'message': f'Baixar imagens (0/{len(assets["images"])})', 'status': 'current'})
            update_progress('Baixando imagens...', 45, 'current', steps)
            
            for idx, img_url in enumerate(assets['images'], 1):
                content = downloader.download_bytes(img_url)
                if content:
                    local_path = organizer.save_image(img_url, content)
                    url_map[img_url] = local_path
                
                downloaded_count += 1
                progress = 15 + int((downloaded_count / max(total_assets, 1)) * 50)
                
                # Update every 10 images to avoid too many updates
                if idx % 10 == 0 or idx == len(assets['images']):
                    steps[-1]['message'] = f'Baixar imagens ({idx}/{len(assets["images"])})'
                    update_progress(f'Baixando imagens... {idx}/{len(assets["images"])}', progress, 'current', steps)
            
            steps[-1]['status'] = 'completed'
        
        # Baixa fontes
        if assets['fonts']:
            steps.append({'message': f'Baixar fontes (0/{len(assets["fonts"])})', 'status': 'current'})
            update_progress('Baixando fontes...', 70, 'current', steps)
            
            for idx, font_url in enumerate(assets['fonts'], 1):
                content = downloader.download_bytes(font_url)
                if content:
                    local_path = organizer.save_font(font_url, content)
                    url_map[font_url] = local_path
                
                downloaded_count += 1
                progress = 15 + int((downloaded_count / max(total_assets, 1)) * 50)
                steps[-1]['message'] = f'Baixar fontes ({idx}/{len(assets["fonts"])})'
                update_progress(f'Baixando fontes... {idx}/{len(assets["fonts"])}', progress, 'current', steps)
            
            steps[-1]['status'] = 'completed'
        
        # Baixa outros assets
        if assets['other']:
            steps.append({'message': f'Baixar outros recursos (0/{len(assets["other"])})', 'status': 'current'})
            update_progress('Baixando outros recursos...', 75, 'current', steps)
            
            for idx, other_url in enumerate(assets['other'], 1):
                content = downloader.download_bytes(other_url)
                if content:
                    local_path = organizer.save_other(other_url, content)
                    url_map[other_url] = local_path
                
                downloaded_count += 1
                progress = 15 + int((downloaded_count / max(total_assets, 1)) * 50)
                steps[-1]['message'] = f'Baixar outros recursos ({idx}/{len(assets["other"])})'
                update_progress(f'Baixando outros... {idx}/{len(assets["other"])}', progress, 'current', steps)
            
            steps[-1]['status'] = 'completed'
        
        # 5. Reescreve URLs no HTML
        steps.append({'message': 'Reescrever URLs no HTML', 'status': 'current'})
        update_progress('Reescrevendo URLs no HTML...', 85, 'current', steps)
        
        if url_map:
            modified_html = parser.rewrite_html_urls(html_content, url_map)
        else:
            modified_html = html_content
        
        steps[-1]['status'] = 'completed'
        
        # 6. Reescreve URLs nos arquivos CSS
        steps.append({'message': 'Reescrever URLs nos arquivos CSS', 'status': 'current'})
        update_progress('Reescrevendo URLs nos arquivos CSS...', 90, 'current', steps)
        organizer.rewrite_css_urls(url_map)
        steps[-1]['status'] = 'completed'
        
        # 7. Salva o HTML final
        steps.append({'message': 'Salvar HTML final', 'status': 'current'})
        update_progress('Salvando HTML final...', 95, 'current', steps)
        organizer.save_html(modified_html)
        steps[-1]['status'] = 'completed'
        
        # Concluído
        update_progress('Cópia concluída com sucesso!', 100, 'completed', steps)
        
        result['success'] = True
        result['output_path'] = str(site_path.absolute())
        
    except Exception as e:
        result['error'] = str(e)
        update_progress(f'Erro: {str(e)}', 0, 'error', [])
    
    return result
