from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Categoria, Tarefa
from ..schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate
from ..security import usuario_atual

router = APIRouter(prefix="/categorias", tags=["Categorias"])


def _buscar_ou_404(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")
    return categoria


def _garantir_nome_unico(db: Session, nome: str, ignorar_id: int | None = None):
    existente = db.scalar(select(Categoria).where(Categoria.nome == nome))
    if existente and existente.id != ignorar_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma categoria com esse nome")


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).order_by(Categoria.nome)).all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def consultar(categoria_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, categoria_id)


@router.post(
    "",
    dependencies=[Depends(usuario_atual)],
    response_model=CategoriaOut,
    status_code=status.HTTP_201_CREATED,
)
def criar(dados: CategoriaCreate, db: Session = Depends(get_db)):
    _garantir_nome_unico(db, dados.nome)
    categoria = Categoria(nome=dados.nome)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.patch(
    "/{categoria_id}",
    dependencies=[Depends(usuario_atual)],
    response_model=CategoriaOut,
)
def atualizar(categoria_id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria = _buscar_ou_404(db, categoria_id)
    if dados.nome is not None:
        _garantir_nome_unico(db, dados.nome, ignorar_id=categoria_id)
        categoria.nome = dados.nome
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete(
    "/{categoria_id}",
    dependencies=[Depends(usuario_atual)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir(categoria_id: int, db: Session = Depends(get_db)):
    categoria = _buscar_ou_404(db, categoria_id)
    em_uso = db.scalar(select(Tarefa.id).where(Tarefa.categoria_id == categoria_id).limit(1))
    if em_uso is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Categoria possui tarefas associadas. Remova ou mova as tarefas antes.",
        )
    db.delete(categoria)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
