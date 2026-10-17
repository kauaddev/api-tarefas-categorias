from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def _agora_utc() -> datetime:
    """Data/hora atual em UTC (sem fuso, como o SQLite armazena)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    # 1 categoria -> N tarefas
    tarefas: Mapped[list["Tarefa"]] = relationship(back_populates="categoria")


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    concluida: Mapped[bool] = mapped_column(Boolean, default=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=_agora_utc)
    categoria_id: Mapped[int | None] = mapped_column(
        ForeignKey("categorias.id"), nullable=True
    )

    categoria: Mapped["Categoria | None"] = relationship(back_populates="tarefas")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora_utc)
