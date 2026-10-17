from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import config
from .database import get_db
from .models import Usuario

# tokenUrl faz o botão "Authorize" do Swagger chamar o nosso /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_token(username: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expira}
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def usuario_atual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """Dependência que protege endpoints: exige um token JWT válido."""
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise erro
    username = payload.get("sub")
    if not username:
        raise erro
    usuario = db.scalar(select(Usuario).where(Usuario.username == username))
    if usuario is None:
        raise erro
    return usuario
