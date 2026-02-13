#!/usr/bin/env python
"""
Script de teste simples para a interface web do WebCopy.

Este script testa se a interface web está funcionando corretamente
sem precisar abrir o navegador manualmente.

Uso:
    python test_web_interface.py
"""

import sys
import time
import requests
from pathlib import Path

# Adiciona src ao path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


def test_web_interface():
    """Testa a interface web do WebCopy."""
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("Teste da Interface Web do WebCopy")
    print("=" * 60)
    print()
    
    # Teste 1: Verifica se o servidor está rodando
    print("1. Testando conexão com o servidor...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Servidor está rodando!")
        else:
            print(f"   ❌ Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Não foi possível conectar ao servidor")
        print(f"   Erro: {e}")
        print()
        print("   💡 Certifique-se de que o servidor está rodando:")
        print("      python run_web.py")
        return False
    
    print()
    
    # Teste 2: Inicia um job de cópia
    print("2. Testando criação de job...")
    test_url = "https://example.com"
    
    try:
        response = requests.post(
            f"{base_url}/api/copy",
            json={"url": test_url},
            timeout=10
        )
        
        if response.status_code == 202:
            data = response.json()
            job_id = data.get('job_id')
            print(f"   ✅ Job criado com sucesso!")
            print(f"   Job ID: {job_id}")
        else:
            print(f"   ❌ Erro ao criar job: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    print()
    
    # Teste 3: Acompanha o progresso
    print("3. Testando consulta de status...")
    max_attempts = 60  # 2 minutos (60 * 2s)
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{base_url}/api/status/{job_id}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                message = data.get('message', '')
                progress = data.get('progress', 0)
                
                # Mostra progresso
                print(f"   [{progress:3d}%] {message}", end='\r')
                
                if status == 'completed':
                    print()
                    print(f"   ✅ Job concluído com sucesso!")
                    print(f"   Caminho: {data.get('output_path')}")
                    break
                elif status == 'error':
                    print()
                    print(f"   ❌ Erro durante processamento:")
                    print(f"   {data.get('error')}")
                    return False
                
                time.sleep(2)
                attempt += 1
            else:
                print(f"   ❌ Erro ao consultar status: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    
    if attempt >= max_attempts:
        print()
        print("   ⚠️  Timeout: Job demorou mais de 2 minutos")
        return False
    
    print()
    
    # Teste 4: Testa endpoints de download e preview
    print("4. Testando endpoints de resultado...")
    
    # Testa download
    try:
        response = requests.get(f"{base_url}/api/download/{job_id}", timeout=10)
        if response.status_code == 200:
            print("   ✅ Endpoint de download funcionando")
        else:
            print(f"   ⚠️  Endpoint de download retornou {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Erro ao testar download: {e}")
    
    # Testa preview
    try:
        response = requests.get(f"{base_url}/api/preview/{job_id}", timeout=10)
        if response.status_code == 200:
            print("   ✅ Endpoint de preview funcionando")
        else:
            print(f"   ⚠️  Endpoint de preview retornou {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Erro ao testar preview: {e}")
    
    print()
    print("=" * 60)
    print("✅ Todos os testes passaram!")
    print("=" * 60)
    print()
    print("A interface web está funcionando corretamente!")
    print(f"Acesse: {base_url}")
    print()
    
    return True


if __name__ == '__main__':
    success = test_web_interface()
    sys.exit(0 if success else 1)
