#!/usr/bin/env python
"""
Script para iniciar a interface web do WebCopy.

Uso:
    python run_web.py
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar webcopy
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from webcopy.web.app import app

if __name__ == '__main__':
    # Cria diretório output se não existir
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("WebCopy - Interface Web")
    print("=" * 60)
    print(f"  Servidor iniciado em: http://localhost:3009")
    print(f"  Diretorio de saida:   {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("Pressione Ctrl+C para parar o servidor")
    print()
    
    app.run(host='0.0.0.0', port=3009, debug=True, threaded=True)
