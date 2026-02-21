# Correção SSL Let's Encrypt no CloudPanel (Sites com Proxy Reverso)

## Problema

Certificados Let's Encrypt falham com erro **404** na validação ACME em sites configurados com **proxy reverso** (Node.js, Next.js, etc.) no CloudPanel.

Erro típico:
```
Domain could not be validated, error message: error type: urn:ietf:params:acme:error:unauthorized,
error detail: 212.85.19.190: Invalid response from
https://dominio.com.br/.well-known/acme-challenge/TOKEN: 404
```

## Causa

O bloco `location ~ /.well-known` no vhost **não possui diretiva `root`**.
Como o site é 100% proxy reverso, o CloudPanel não inclui um `root` no `{{settings}}`.
O Nginx não sabe de qual diretório servir os arquivos de desafio ACME → retorna 404.

## Correção

No CloudPanel, editar o **Vhost** do domínio afetado e alterar o bloco `.well-known`:

```nginx
# ❌ ANTES (sem root - causa o erro 404):
location ~ /.well-known {
    auth_basic off;
    allow all;
}

# ✅ DEPOIS (com root - funciona):
location ~ /.well-known {
    auth_basic off;
    allow all;
    root /home/USUARIO/htdocs/DOMINIO;
}
```

### Como descobrir o caminho correto

O padrão do CloudPanel é:

```
/home/{usuario-do-site}/htdocs/{dominio}/
```

Para confirmar:

```bash
# Ver logs do Nginx para descobrir o usuário do site
nginx -T 2>/dev/null | grep -B2 -A5 "server_name SEU_DOMINIO"
# Procure a linha: access_log /home/USUARIO/logs/...

# Listar o htdocs do usuário
ls -la /home/USUARIO/htdocs/
```

### Garantir que o diretório .well-known existe

```bash
mkdir -p /home/USUARIO/htdocs/DOMINIO/.well-known/acme-challenge/
```

### Testar antes de emitir

```bash
# Criar arquivo de teste
echo "ok" > /home/USUARIO/htdocs/DOMINIO/.well-known/acme-challenge/teste

# Recarregar Nginx
nginx -t && systemctl reload nginx

# Testar via HTTPS (é assim que o Let's Encrypt valida após o redirect HTTP→HTTPS)
curl -k https://SEU_DOMINIO/.well-known/acme-challenge/teste
# Deve retornar: ok

# Limpar teste
rm /home/USUARIO/htdocs/DOMINIO/.well-known/acme-challenge/teste
```

Se retornar "ok", emitir o certificado pelo painel do CloudPanel.

## Exemplo Real (novo.hajar.com.br)

- **Usuário**: hajar-novo
- **Root correto**: `/home/hajar-novo/htdocs/novo.hajar.com.br`
- **Bloco corrigido**:

```nginx
location ~ /.well-known {
    auth_basic off;
    allow all;
    root /home/hajar-novo/htdocs/novo.hajar.com.br;
}
```

## Domínios do Servidor (referência rápida)

| Domínio | Certificado SSL |
|---------|----------------|
| novo.hajar.com.br | ✅ Corrigido |
| admin.hajar.com.br | Verificar |
| admin.weloverave.club | Verificar |
| app.task-list.com.br | Verificar |
| cms.ecwd.cloud | Verificar |
| ecwd.cloud | Verificar |
| elielcezar.com | Verificar |
| financeiro.ecwd.cloud | Verificar |
| hublink.ecwd.cloud | Verificar |
| n8n.ecwd.cloud | Verificar |
| safe.ecwd.cloud | Verificar |
| safe.ecwd.pro | Verificar |
| scriby.co | Verificar |
| task-list.com.br | Verificar |
| tecvibes.com.br | Verificar |
| weloverave.club | Verificar |

## Notas

- **CloudPanel 6.0.8** não usa certbot — usa cliente ACME interno via `clpctl`
- O problema só afeta sites com **proxy reverso** (Node.js, Next.js, etc.), pois sites estáticos/PHP já têm `root` definido pelo CloudPanel
- A emissão via CLI também é possível: `clpctl lets-encrypt:install:certificate --domainName=DOMINIO`
- Após corrigir todos, os warnings de `ssl_stapling` no `nginx -t` devem desaparecer

## Prevenção

1. Sempre que criar um novo site com proxy reverso no CloudPanel, adicionar o `root` no bloco `.well-known`
2. Monitorar expiração dos certificados periodicamente
3. Após atualizações do CloudPanel, verificar se os certificados continuam renovando
