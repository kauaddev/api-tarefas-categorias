from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------- Categoria ----------
class CategoriaCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=80, examples=["Estudos"])


class CategoriaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("nome")
    @classmethod
    def nome_nao_nulo(cls, v):
        if v is None:
            raise ValueError("nome não pode ser nulo")
        return v


class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str


# ---------- Tarefa ----------
class TarefaCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=120, examples=["Entregar trabalho de APIs"])
    descricao: str | None = Field(default=None, max_length=1000)
    concluida: bool = False
    categoria_id: int | None = None


class TarefaUpdate(BaseModel):
    """Todos os campos são opcionais: é isso que justifica o uso de PATCH."""
    titulo: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=1000)
    concluida: bool | None = None
    categoria_id: int | None = None

    @field_validator("titulo", "concluida")
    @classmethod
    def campos_obrigatorios_nao_nulos(cls, v):
        if v is None:
            raise ValueError("campo não pode ser nulo")
        return v


class TarefaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    descricao: str | None
    concluida: bool
    criada_em: datetime
    categoria_id: int | None


# ---------- Usuário / Autenticação ----------
class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    senha: str = Field(min_length=8, max_length=72)

    @field_validator("senha")
    @classmethod
    def senha_cabe_no_bcrypt(cls, v):
        # O bcrypt só considera os primeiros 72 BYTES da senha
        if len(v.encode("utf-8")) > 72:
            raise ValueError("senha muito longa (máximo de 72 bytes)")
        return v


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
