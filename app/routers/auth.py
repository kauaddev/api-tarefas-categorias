from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import Token, UsuarioCreate, UsuarioOut
from ..security import criar_token, gerar_hash, usuario_atual, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Usuario).where(Usuario.username == dados.username)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome de usuário já cadastrado")
    usuario = Usuario(username=dados.username, senha_hash=gerar_hash(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.username == form.username))
    # Mesma mensagem para usuário inexistente e senha errada (não revela qual falhou)
    if usuario is None or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=criar_token(usuario.username))


@router.get("/me", response_model=UsuarioOut)
def quem_sou_eu(usuario: Usuario = Depends(usuario_atual)):
    """Endpoint protegido de demonstração: devolve o usuário do token."""
    return usuario
