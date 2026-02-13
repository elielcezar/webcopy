"""
Flask App - Interface web para o WebCopy.
"""

import os
import uuid
import threading
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from urllib.parse import urlparse

from .tasks import process_website


# Inicializa Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'webcopy-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Armazena jobs em memória (dict thread-safe básico)
jobs: Dict[str, Dict[str, Any]] = {}
jobs_lock = threading.Lock()


def validate_url(url: str) -> bool:
    """Valida se a URL é válida."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ('http', 'https')
    except:
        return False


def update_job_status(job_id: str, updates: Dict[str, Any]):
    """Atualiza o status de um job de forma thread-safe."""
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(updates)


def run_copy_task(job_id: str, url: str, output_dir: str):
    """Executa a tarefa de cópia em background."""
    def progress_callback(progress_data: Dict[str, Any]):
        """Callback para atualizar progresso do job."""
        update_job_status(job_id, {
            'message': progress_data.get('message', ''),
            'progress': progress_data.get('progress', 0),
            'steps': progress_data.get('steps', []),
            'updated_at': datetime.now().isoformat()
        })
    
    try:
        # Processa o website
        result = process_website(
            url=url,
            output_dir=output_dir,
            progress_callback=progress_callback
        )
        
        if result['success']:
            # Cria ZIP do site baixado
            output_path = Path(result['output_path'])
            zip_path = None
            
            if output_path.exists():
                try:
                    # Cria arquivo ZIP
                    zip_base = str(output_path.parent / output_path.name)
                    zip_path = shutil.make_archive(zip_base, 'zip', output_path)
                except Exception as e:
                    print(f"Erro ao criar ZIP: {e}")
            
            update_job_status(job_id, {
                'status': 'completed',
                'message': 'Cópia concluída com sucesso!',
                'progress': 100,
                'output_path': result['output_path'],
                'zip_path': zip_path,
                'completed_at': datetime.now().isoformat()
            })
        else:
            update_job_status(job_id, {
                'status': 'error',
                'error': result.get('error', 'Erro desconhecido'),
                'message': f'Erro: {result.get("error", "Erro desconhecido")}',
                'completed_at': datetime.now().isoformat()
            })
    
    except Exception as e:
        update_job_status(job_id, {
            'status': 'error',
            'error': str(e),
            'message': f'Erro: {str(e)}',
            'completed_at': datetime.now().isoformat()
        })


@app.route('/')
def index():
    """Página principal da interface web."""
    return render_template('index.html')


@app.route('/api/copy', methods=['POST'])
def api_copy():
    """
    Inicia o processo de cópia de um site.
    
    Body JSON:
        {
            "url": "https://example.com"
        }
    
    Returns:
        {
            "job_id": "uuid-here",
            "status": "processing",
            "message": "Job iniciado"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL é obrigatória'}), 400
        
        url = data['url'].strip()
        
        # Valida URL
        if not validate_url(url):
            return jsonify({'error': 'URL inválida. Use formato: https://example.com'}), 400
        
        # Gera ID único para o job
        job_id = str(uuid.uuid4())
        
        # Cria entrada do job
        with jobs_lock:
            jobs[job_id] = {
                'job_id': job_id,
                'url': url,
                'status': 'processing',
                'message': 'Iniciando...',
                'progress': 0,
                'steps': [],
                'output_path': None,
                'zip_path': None,
                'error': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        # Inicia thread para processar em background
        output_dir = os.path.join(os.getcwd(), 'output')
        thread = threading.Thread(
            target=run_copy_task,
            args=(job_id, url, output_dir),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'processing',
            'message': 'Job iniciado com sucesso'
        }), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def api_status(job_id: str):
    """
    Consulta o status de um job.
    
    Returns:
        {
            "job_id": "uuid",
            "status": "processing|completed|error",
            "message": "Status message",
            "progress": 0-100,
            "steps": [...],
            "url": "https://...",
            "output_path": "/path/to/output",
            "error": "error message if any"
        }
    """
    with jobs_lock:
        job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    return jsonify(job), 200


@app.route('/api/download/<job_id>', methods=['GET'])
def api_download(job_id: str):
    """
    Faz download do arquivo ZIP do site copiado.
    """
    with jobs_lock:
        job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job ainda não foi concluído'}), 400
    
    zip_path = job.get('zip_path')
    
    if not zip_path or not os.path.exists(zip_path):
        return jsonify({'error': 'Arquivo ZIP não encontrado'}), 404
    
    # Extrai nome do arquivo do path
    zip_filename = os.path.basename(zip_path)
    
    return send_file(
        zip_path,
        as_attachment=True,
        download_name=zip_filename,
        mimetype='application/zip'
    )


@app.route('/api/preview/<job_id>', methods=['GET'])
@app.route('/api/preview/<job_id>/<path:filename>', methods=['GET'])
def api_preview(job_id: str, filename: str = 'index.html'):
    """
    Serve o site copiado para preview no navegador.
    """
    with jobs_lock:
        job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job ainda não foi concluído'}), 400
    
    output_path = job.get('output_path')
    
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': 'Diretório de saída não encontrado'}), 404
    
    # Serve arquivo do diretório de saída
    try:
        return send_from_directory(output_path, filename)
    except Exception as e:
        return jsonify({'error': f'Arquivo não encontrado: {str(e)}'}), 404


@app.route('/api/jobs', methods=['GET'])
def api_jobs():
    """
    Lista todos os jobs (útil para debug/desenvolvimento).
    """
    with jobs_lock:
        all_jobs = list(jobs.values())
    
    return jsonify({
        'total': len(all_jobs),
        'jobs': all_jobs
    }), 200


@app.errorhandler(404)
def not_found(e):
    """Handler para 404."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint não encontrado'}), 404
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handler para 500."""
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    # Cria diretório output se não existir
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("WebCopy - Interface Web")
    print("=" * 60)
    print(f"Servidor iniciado em: http://localhost:5000")
    print(f"Diretório de saída: {output_dir.absolute()}")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
