# 🔌 Exemplos de Uso da API

Exemplos práticos de como usar a API REST do WebCopy.

## Base URL

```
http://localhost:5000
```

## Autenticação

Não há autenticação (uso local).

## Exemplos

### 1. Iniciar Cópia de um Site

**Request:**

```bash
curl -X POST http://localhost:5000/api/copy \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response (202 Accepted):**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "message": "Job iniciado com sucesso"
}
```

### 2. Consultar Status de um Job

**Request:**

```bash
curl http://localhost:5000/api/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (200 OK) - Em Progresso:**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "url": "https://example.com",
  "status": "processing",
  "message": "Baixando imagens... 45/123",
  "progress": 65,
  "steps": [
    {
      "message": "Baixar página principal",
      "status": "completed"
    },
    {
      "message": "Analisar página",
      "status": "completed"
    },
    {
      "message": "Baixar CSS (9/9)",
      "status": "completed"
    },
    {
      "message": "Baixar JavaScript (7/7)",
      "status": "completed"
    },
    {
      "message": "Baixar imagens (45/123)",
      "status": "current"
    }
  ],
  "output_path": null,
  "zip_path": null,
  "error": null,
  "created_at": "2026-02-13T10:30:00.000000",
  "updated_at": "2026-02-13T10:30:45.000000"
}
```

**Response (200 OK) - Concluído:**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "url": "https://example.com",
  "status": "completed",
  "message": "Cópia concluída com sucesso!",
  "progress": 100,
  "steps": [...],
  "output_path": "D:\\Eliel\\WebCopy\\webcopy\\output\\example.com_2026-02-13_10-30-00",
  "zip_path": "D:\\Eliel\\WebCopy\\webcopy\\output\\example.com_2026-02-13_10-30-00.zip",
  "error": null,
  "created_at": "2026-02-13T10:30:00.000000",
  "updated_at": "2026-02-13T10:31:30.000000",
  "completed_at": "2026-02-13T10:31:30.000000"
}
```

**Response (200 OK) - Erro:**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "url": "https://invalid-url.com",
  "status": "error",
  "message": "Erro: Não foi possível baixar a página",
  "progress": 0,
  "steps": [],
  "output_path": null,
  "zip_path": null,
  "error": "Não foi possível baixar a página",
  "created_at": "2026-02-13T10:30:00.000000",
  "updated_at": "2026-02-13T10:30:05.000000",
  "completed_at": "2026-02-13T10:30:05.000000"
}
```

### 3. Download do ZIP

**Request:**

```bash
curl -O -J http://localhost:5000/api/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
- Status: 200 OK
- Content-Type: application/zip
- Content-Disposition: attachment; filename="example.com_2026-02-13_10-30-00.zip"
- Body: (binary ZIP file)

### 4. Preview do Site

**Request:**

```bash
# Abre o index.html
curl http://localhost:5000/api/preview/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Abre um arquivo específico
curl http://localhost:5000/api/preview/a1b2c3d4-e5f6-7890-abcd-ef1234567890/css/style.css
```

**Response:**
- Status: 200 OK
- Content-Type: text/html (ou apropriado para o arquivo)
- Body: (conteúdo do arquivo)

### 5. Listar Todos os Jobs (Debug)

**Request:**

```bash
curl http://localhost:5000/api/jobs
```

**Response (200 OK):**

```json
{
  "total": 3,
  "jobs": [
    {
      "job_id": "job-1",
      "url": "https://example.com",
      "status": "completed",
      "progress": 100,
      ...
    },
    {
      "job_id": "job-2",
      "url": "https://another-site.com",
      "status": "processing",
      "progress": 45,
      ...
    },
    {
      "job_id": "job-3",
      "url": "https://failed-site.com",
      "status": "error",
      "error": "Timeout",
      ...
    }
  ]
}
```

## Códigos de Status HTTP

| Código | Significado | Quando Ocorre |
|--------|-------------|---------------|
| 200 | OK | Consulta bem-sucedida |
| 202 | Accepted | Job criado com sucesso |
| 400 | Bad Request | URL inválida ou job não concluído |
| 404 | Not Found | Job ou arquivo não encontrado |
| 500 | Internal Server Error | Erro no servidor |

## Erros Comuns

### URL Inválida

**Request:**
```bash
curl -X POST http://localhost:5000/api/copy \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-valid-url"}'
```

**Response (400 Bad Request):**
```json
{
  "error": "URL inválida. Use formato: https://example.com"
}
```

### Job Não Encontrado

**Request:**
```bash
curl http://localhost:5000/api/status/invalid-job-id
```

**Response (404 Not Found):**
```json
{
  "error": "Job não encontrado"
}
```

### Download Antes de Concluir

**Request:**
```bash
curl http://localhost:5000/api/download/job-still-processing
```

**Response (400 Bad Request):**
```json
{
  "error": "Job ainda não foi concluído"
}
```

## Exemplos em Python

### Exemplo Completo

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# 1. Inicia cópia
response = requests.post(
    f"{BASE_URL}/api/copy",
    json={"url": "https://example.com"}
)

if response.status_code == 202:
    job_id = response.json()["job_id"]
    print(f"Job criado: {job_id}")
    
    # 2. Acompanha progresso
    while True:
        response = requests.get(f"{BASE_URL}/api/status/{job_id}")
        data = response.json()
        
        status = data["status"]
        progress = data["progress"]
        message = data["message"]
        
        print(f"[{progress}%] {message}")
        
        if status == "completed":
            print("✅ Concluído!")
            output_path = data["output_path"]
            print(f"Arquivos em: {output_path}")
            
            # 3. Baixa ZIP
            response = requests.get(f"{BASE_URL}/api/download/{job_id}")
            with open("site.zip", "wb") as f:
                f.write(response.content)
            print("ZIP baixado: site.zip")
            break
        
        elif status == "error":
            print(f"❌ Erro: {data['error']}")
            break
        
        time.sleep(2)  # Aguarda 2 segundos
```

### Exemplo com Tratamento de Erros

```python
import requests
from typing import Optional

def copy_website(url: str) -> Optional[str]:
    """
    Copia um website e retorna o caminho do ZIP.
    
    Returns:
        Caminho do ZIP ou None em caso de erro.
    """
    try:
        # Inicia job
        response = requests.post(
            "http://localhost:5000/api/copy",
            json={"url": url},
            timeout=10
        )
        response.raise_for_status()
        
        job_id = response.json()["job_id"]
        
        # Aguarda conclusão
        max_attempts = 300  # 10 minutos (300 * 2s)
        for _ in range(max_attempts):
            response = requests.get(
                f"http://localhost:5000/api/status/{job_id}",
                timeout=5
            )
            data = response.json()
            
            if data["status"] == "completed":
                # Download ZIP
                response = requests.get(
                    f"http://localhost:5000/api/download/{job_id}"
                )
                
                zip_filename = f"{job_id}.zip"
                with open(zip_filename, "wb") as f:
                    f.write(response.content)
                
                return zip_filename
            
            elif data["status"] == "error":
                print(f"Erro: {data['error']}")
                return None
            
            time.sleep(2)
        
        print("Timeout: Job demorou muito")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Erro de rede: {e}")
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

# Uso
zip_path = copy_website("https://example.com")
if zip_path:
    print(f"Site baixado: {zip_path}")
```

## Exemplos em JavaScript

### Fetch API

```javascript
async function copyWebsite(url) {
  try {
    // 1. Inicia job
    const response = await fetch('http://localhost:5000/api/copy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    });
    
    const data = await response.json();
    const jobId = data.job_id;
    
    console.log(`Job criado: ${jobId}`);
    
    // 2. Polling de status
    while (true) {
      const statusResponse = await fetch(
        `http://localhost:5000/api/status/${jobId}`
      );
      const statusData = await statusResponse.json();
      
      console.log(`[${statusData.progress}%] ${statusData.message}`);
      
      if (statusData.status === 'completed') {
        console.log('✅ Concluído!');
        
        // 3. Download
        window.location.href = 
          `http://localhost:5000/api/download/${jobId}`;
        break;
      } else if (statusData.status === 'error') {
        console.error(`❌ Erro: ${statusData.error}`);
        break;
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  } catch (error) {
    console.error('Erro:', error);
  }
}

// Uso
copyWebsite('https://example.com');
```

## Integração com Outras Ferramentas

### cURL Script

```bash
#!/bin/bash

URL="https://example.com"
BASE_URL="http://localhost:5000"

# Inicia job
RESPONSE=$(curl -s -X POST "$BASE_URL/api/copy" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$URL\"}")

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# Aguarda conclusão
while true; do
  STATUS=$(curl -s "$BASE_URL/api/status/$JOB_ID")
  STATE=$(echo $STATUS | jq -r '.status')
  PROGRESS=$(echo $STATUS | jq -r '.progress')
  MESSAGE=$(echo $STATUS | jq -r '.message')
  
  echo "[$PROGRESS%] $MESSAGE"
  
  if [ "$STATE" = "completed" ]; then
    echo "✅ Concluído!"
    curl -O -J "$BASE_URL/api/download/$JOB_ID"
    break
  elif [ "$STATE" = "error" ]; then
    ERROR=$(echo $STATUS | jq -r '.error')
    echo "❌ Erro: $ERROR"
    break
  fi
  
  sleep 2
done
```

### Postman Collection

Importe esta collection no Postman:

```json
{
  "info": {
    "name": "WebCopy API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Iniciar Cópia",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"https://example.com\"\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/copy",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "copy"]
        }
      }
    },
    {
      "name": "Consultar Status",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:5000/api/status/:job_id",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "status", ":job_id"],
          "variable": [
            {
              "key": "job_id",
              "value": "seu-job-id-aqui"
            }
          ]
        }
      }
    }
  ]
}
```

---

**Mais informações:** [WEB_INTERFACE.md](WEB_INTERFACE.md)
