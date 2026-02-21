# Instalacao do WebCopy

Guia definitivo de instalacao e execucao do WebCopy (CLI + Interface Web).

## Pre-requisitos

- **Python 3.8+** instalado ([python.org](https://www.python.org/downloads/))
- Navegador web moderno (Chrome, Firefox, Edge)

Verifique se o Python esta instalado:

```bash
python --version
```

## Instalacao

> **IMPORTANTE (Windows):** Se voce tem mais de uma versao do Python instalada
> (ex: Laragon + Python oficial), use **sempre** `python -m pip` em vez de `pip`
> para garantir que instala no Python correto.
>
> Para verificar: `python -c "import sys; print(sys.executable)"` mostra qual Python esta ativo.

Abra o terminal na **raiz do projeto** (onde esta o `setup.py`) e execute:

```bash
# 1. Instalar TODAS as dependencias (incluindo Flask para interface web)
python -m pip install -r requirements.txt

# 2. Instalar o pacote webcopy em modo desenvolvimento
python -m pip install -e .
```

Pronto. Isso instala tudo que e necessario.

## Verificar Instalacao

```bash
python -c "import flask; import webcopy; print('Tudo instalado com sucesso')"
```

Se nao houver erros, esta tudo certo.

## Executar a Interface Web

```bash
python run_web.py
```

Acesse no navegador: **http://localhost:5000**

### Como usar:

1. Cole a URL do site que deseja copiar
2. Clique em **"Copiar Site"**
3. Acompanhe o progresso em tempo real
4. Use **"Download ZIP"** ou **"Visualizar"** quando concluir

Os sites baixados ficam salvos na pasta `output/`.

## Executar via CLI (alternativa)

```bash
# Copiar um site via linha de comando
webcopy https://example.com

# Ou usando Python diretamente
python -m webcopy https://example.com
```

## Solucao de Problemas

| Erro | Causa | Solucao |
|------|-------|---------|
| `No module named 'flask'` | `pip` e `python` apontam para Pythons diferentes | `python -m pip install -r requirements.txt` |
| `No module named 'webcopy'` | Pacote nao instalado | `python -m pip install -e .` (na raiz do projeto) |
| `UnicodeEncodeError` com emojis | Terminal Windows nao suporta UTF-8 | Remover emojis do `run_web.py` ou usar `set PYTHONIOENCODING=utf-8` |
| `Address already in use` (porta 5000) | Outra aplicacao usando a porta | Edite a porta em `run_web.py` para 8080 |

## Resumo Rapido (copiar e colar)

```bash
python -m pip install -r requirements.txt && python -m pip install -e . && python run_web.py
```
