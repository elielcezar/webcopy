#!/bin/bash
# Script para instalar o WebCopy em modo desenvolvimento
echo "Instalando WebCopy..."
python -m pip install -e .
echo ""
echo "Instalacao concluida!"
echo "Agora voce pode usar: python -m webcopy https://exemplo.com"
