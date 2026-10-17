from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from .database import Base, engine
from . import models  # noqa: F401  (registra os modelos no metadata)
from .routers import auth, categorias, tarefas

# Cria as tabelas se não existirem (em projetos maiores, usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Tarefas e Categorias",
    version="1.0.0",
    description=(
        "API REST para gerenciar tarefas organizadas por categorias. "
        "Leitura (GET) é pública; criação, alteração e exclusão exigem token JWT "
        "(registre-se em /auth/registrar e faça login em /auth/login)."
    ),
)

# ---------------- CORS ----------------
# Só as origens listadas em CORS_ORIGINS podem chamar a API a partir de um navegador.
# Não usamos cookies (o token vai no cabeçalho Authorization), então
# allow_credentials fica desligado, o que também permite restringir métodos/cabeçalhos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def erro_de_validacao(request: Request, exc: RequestValidationError):
    """O FastAPI devolve 422 por padrão. O roteiro pede 400 para dados inválidos,
    então padronizamos a resposta com uma mensagem legível por campo."""
    detalhes = [
        {"campo": ".".join(str(p) for p in e["loc"] if p not in ("body",)), "erro": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Dados inválidos", "erros": detalhes},
    )


app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(tarefas.router)


@app.get("/", tags=["Saúde"])
def raiz():
    return {"status": "ok", "mensagem": "API de Tarefas no ar"}
