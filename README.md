# API de Tarefas e Categorias

API REST desenvolvida como Atividade Prática da disciplina **Arquitetura e Desenvolvimento de APIs** (Uninter, 2026).

## Descrição e problema resolvido

Pessoas que organizam estudos, trabalho e tarefas do dia a dia costumam depender de listas soltas, sem agrupamento nem filtros. Esta API oferece o *back-end* de um gerenciador de tarefas: cada **tarefa** pode ser associada a uma **categoria** (por exemplo, "Estudos" ou "Trabalho"), marcada como concluída e consultada com filtros.

Qualquer cliente HTTP (aplicativo web, mobile, script) pode usar a API. A leitura é pública; criar, alterar e excluir exige autenticação com **token JWT**.

### Funcionalidades

- CRUD completo de **tarefas** e de **categorias**
- Filtros de tarefas por status (`concluida`), categoria (`categoria_id`) e texto no título (`busca`)
- Cadastro e login de usuários, com senha armazenada como hash **bcrypt**
- Proteção dos endpoints de escrita com **JWT**
- **CORS** restrito às origens configuradas
- Validação de entrada e respostas de erro padronizadas em JSON
- Documentação interativa (Swagger/OpenAPI) gerada automaticamente
- 57 testes automatizados

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 ou superior |
| Framework | FastAPI |
| Servidor | Uvicorn |
| Banco de dados | SQLite |
| ORM | SQLAlchemy 2.0 |
| Validação | Pydantic 2 |
| Autenticação | PyJWT (token) e bcrypt (hash de senha) |
| Testes | pytest e httpx (via `TestClient` do FastAPI) |

## Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/) instalado (marque a opção **Add Python to PATH** na instalação)
- [Git](https://git-scm.com/) para clonar o repositório
- Nenhum servidor de banco de dados: o SQLite já vem com o Python

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/kauaddev/api-tarefas-categorias.git
cd api-tarefas-categorias
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Se aparecer o erro de "execução de scripts desabilitada", rode antes:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Quando o ambiente estiver ativo, o prompt começa com `(.venv)`.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

Para também rodar os testes, use `pip install -r requirements-dev.txt`.

## Configuração do banco de dados e das variáveis de ambiente

### Variáveis de ambiente

Copie o arquivo de exemplo e edite o resultado:

```powershell
copy .env.example .env        # Windows
```

```bash
cp .env.example .env          # Linux / macOS
```

| Variável | Obrigatória | Descrição | Exemplo |
|---|---|---|---|
| `DATABASE_URL` | Não | Endereço do banco. Padrão: SQLite local | `sqlite:///./tarefas.db` |
| `SECRET_KEY` | **Sim** | Chave que assina os tokens JWT | *(gere uma, veja abaixo)* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Validade do token em minutos (padrão 30) | `30` |
| `CORS_ORIGINS` | Não | Origens liberadas no CORS, separadas por vírgula | `http://localhost:3000,http://localhost:5173` |

Gere uma `SECRET_KEY` segura e cole no `.env`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **Atenção:** o arquivo `.env` contém segredos e está no `.gitignore`. Nunca o envie ao repositório. Sem `SECRET_KEY`, a API se recusa a iniciar.

### Banco de dados

Não é preciso criar nada manualmente: **as tabelas são criadas automaticamente** na primeira execução, no arquivo `tarefas.db`.

A estrutura também está documentada em [`database/schema.sql`](database/schema.sql). Para recriar o banco manualmente, se preferir:

```bash
sqlite3 tarefas.db < database/schema.sql
```

Modelo de dados:

```
categorias (1) ──────< (N) tarefas        usuarios
 id, nome (único)           id, titulo, descricao,    id, username (único),
                            concluida, criada_em,     senha_hash, criado_em
                            categoria_id (FK, opcional)
```

## Como iniciar a aplicação

Na pasta raiz do projeto, com o ambiente virtual ativo:

```bash
uvicorn app.main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000`. A opção `--reload` reinicia o servidor a cada alteração no código (use apenas em desenvolvimento). Para parar, pressione `Ctrl + C`.

## Documentação (Swagger)

| Interface | Endereço |
|---|---|
| Swagger UI (testar clicando) | http://127.0.0.1:8000/docs |
| ReDoc (leitura) | http://127.0.0.1:8000/redoc |
| Especificação OpenAPI (JSON) | http://127.0.0.1:8000/openapi.json |

## Resumo dos principais endpoints

| Método | Endpoint | Finalidade | Autenticação | Respostas |
|---|---|---|---|---|
| POST | `/auth/registrar` | Cadastrar usuário | Não | 201 / 400 / 409 |
| POST | `/auth/login` | Obter token JWT (formulário) | Não | 200 / 401 |
| GET | `/auth/me` | Dados do usuário logado | **Sim** | 200 / 401 |
| GET | `/tarefas` | Listar tarefas (`?concluida=`, `?categoria_id=`, `?busca=`) | Não | 200 |
| GET | `/tarefas/{id}` | Consultar uma tarefa | Não | 200 / 404 |
| POST | `/tarefas` | Criar tarefa | **Sim** | 201 / 400 / 401 |
| PATCH | `/tarefas/{id}` | Atualizar tarefa (parcial) | **Sim** | 200 / 400 / 401 / 404 |
| DELETE | `/tarefas/{id}` | Excluir tarefa | **Sim** | 204 / 401 / 404 |
| GET | `/categorias` | Listar categorias | Não | 200 |
| GET | `/categorias/{id}` | Consultar uma categoria | Não | 200 / 404 |
| POST | `/categorias` | Criar categoria | **Sim** | 201 / 400 / 401 / 409 |
| PATCH | `/categorias/{id}` | Renomear categoria | **Sim** | 200 / 400 / 401 / 404 / 409 |
| DELETE | `/categorias/{id}` | Excluir categoria (sem tarefas) | **Sim** | 204 / 401 / 404 / 409 |

**Por que PATCH e não PUT?** O PATCH altera apenas os campos enviados. Para marcar uma tarefa como concluída basta enviar `{"concluida": true}`, sem reenviar o recurso inteiro.

### Formato dos erros

```json
{ "detail": "Tarefa não encontrada" }
```

Erros de validação (400) indicam o campo com problema:

```json
{
  "detail": "Dados inválidos",
  "erros": [{ "campo": "titulo", "erro": "Field required" }]
}
```

## Exemplos de requisição

Os exemplos usam a API rodando em `http://127.0.0.1:8000`.

### Linux, macOS ou Git Bash (cURL)

```bash
# 1. Registrar um usuário
curl -X POST http://127.0.0.1:8000/auth/registrar \
  -H "Content-Type: application/json" \
  -d '{"username": "aluno", "senha": "senha-forte-123"}'

# 2. Fazer login e guardar o token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=aluno&password=senha-forte-123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Criar uma categoria (endpoint protegido)
curl -X POST http://127.0.0.1:8000/categorias \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Estudos"}'

# 4. Criar uma tarefa nessa categoria
curl -X POST http://127.0.0.1:8000/tarefas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Entregar trabalho de APIs", "categoria_id": 1}'

# 5. Listar tarefas pendentes (público, sem token)
curl "http://127.0.0.1:8000/tarefas?concluida=false"

# 6. Marcar a tarefa como concluída
curl -X PATCH http://127.0.0.1:8000/tarefas/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"concluida": true}'

# 7. Excluir a tarefa (resposta 204, sem corpo)
curl -X DELETE http://127.0.0.1:8000/tarefas/1 -H "Authorization: Bearer $TOKEN"
```

### Windows (PowerShell)

```powershell
# 1. Registrar um usuário
$corpo = @{ username = "aluno"; senha = "senha-forte-123" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/auth/registrar `
  -ContentType "application/json" -Body $corpo

# 2. Fazer login e guardar o token
$login = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/auth/login `
  -Body @{ username = "aluno"; password = "senha-forte-123" }
$cab = @{ Authorization = "Bearer $($login.access_token)" }

# 3. Criar uma categoria (endpoint protegido)
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/categorias -Headers $cab `
  -ContentType "application/json" -Body '{"nome": "Estudos"}'

# 4. Criar uma tarefa
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tarefas -Headers $cab `
  -ContentType "application/json" -Body '{"titulo": "Entregar trabalho de APIs", "categoria_id": 1}'

# 5. Listar tarefas (público)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tarefas?concluida=false"
```

## Autenticação e como testar sem expor credenciais

**Fluxo:**

1. O cliente cria uma conta em `POST /auth/registrar`. A senha é guardada como hash bcrypt, nunca em texto puro.
2. O cliente faz login em `POST /auth/login` e recebe um token JWT com validade limitada.
3. Nos endpoints protegidos, o cliente envia o cabeçalho `Authorization: Bearer <token>`.
4. A API valida a assinatura e a validade do token. Se faltar ou for inválido, responde **401**.

**Para testar, não existe usuário nem senha padrão:** crie o seu próprio usuário em `/auth/registrar`. Nenhuma credencial está no repositório.

**No Swagger:** abra `/docs`, registre-se, clique em **Authorize** (cadeado), informe usuário e senha e confirme. O Swagger passa a enviar o token em todas as chamadas. Deixe `client_id` e `client_secret` em branco.

## CORS

O navegador bloqueia, por padrão, que uma página de uma origem chame uma API de outra origem. O CORS é o mecanismo pelo qual a API declara quem pode.

Configuração adotada (`app/main.py`):

| Item | Valor |
|---|---|
| Origens permitidas | As de `CORS_ORIGINS` (padrão: `localhost:3000` e `localhost:5173`) |
| Métodos | GET, POST, PATCH, DELETE, OPTIONS |
| Cabeçalhos | `Authorization`, `Content-Type` |
| Credenciais (cookies) | Desligadas, pois o token vai no cabeçalho `Authorization` |

Não se usa `*` (qualquer origem). Para liberar outro front-end, acrescente a origem em `CORS_ORIGINS`.

## Testes

```bash
pytest
```

São 57 testes automatizados (autenticação, categorias, tarefas e CORS). Cada teste usa um banco SQLite **em memória**, isolado, e não altera o `tarefas.db`.

## Estrutura do projeto

```
.
├── app/
│   ├── main.py            # aplicação, CORS, tratamento de erros, registro das rotas
│   ├── config.py          # leitura das variáveis de ambiente
│   ├── database.py        # conexão e sessão do banco
│   ├── models.py          # modelos ORM (tabelas)
│   ├── schemas.py         # modelos Pydantic (validação de entrada e saída)
│   ├── security.py        # hash de senha, criação e validação do JWT
│   └── routers/
│       ├── auth.py        # registro, login e /auth/me
│       ├── categorias.py  # CRUD de categorias
│       └── tarefas.py     # CRUD de tarefas
├── database/schema.sql    # estrutura do banco
├── tests/                 # testes automatizados (pytest)
├── .env.example           # modelo das variáveis de ambiente
├── requirements.txt       # dependências de execução
├── requirements-dev.txt   # dependências de execução + testes
└── pytest.ini
```

## Limitações conhecidas

- O cadastro de usuários é aberto, e as tarefas são compartilhadas entre usuários (não há "dono" da tarefa).
- Não há limite de tentativas de login nem HTTPS embutido; em produção, a API deve ficar atrás de um proxy com HTTPS.
- As tabelas são criadas com `create_all`; em um projeto maior, o ideal seria usar migrations (Alembic).

## Autoria

Trabalho desenvolvido por: **[Nome completo — RU]**
