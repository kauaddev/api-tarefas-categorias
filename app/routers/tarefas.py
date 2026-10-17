from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Categoria, Tarefa
from ..schemas import TarefaCreate, TarefaOut, TarefaUpdate
from ..security import usuario_atual

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


def _buscar_ou_404(db: Session, tarefa_id: int) -> Tarefa:
    tarefa = db.get(Tarefa, tarefa_id)
    if tarefa is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarefa não encontrada")
    return tarefa


def _validar_categoria(db: Session, categoria_id: int | None):
    if categoria_id is not None and db.get(Categoria, categoria_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "categoria_id informado não existe")


@router.get("", response_model=list[TarefaOut])
def listar(
    concluida: bool | None = Query(default=None, description="Filtra por status"),
    categoria_id: int | None = Query(default=None, description="Filtra por categoria"),
    busca: str | None = Query(default=None, min_length=1, description="Texto no título"),
    db: Session = Depends(get_db),
):
    consulta = select(Tarefa).order_by(Tarefa.id)
    if concluida is not None:
        consulta = consulta.where(Tarefa.concluida == concluida)
    if categoria_id is not None:
        consulta = consulta.where(Tarefa.categoria_id == categoria_id)
    if busca:
        consulta = consulta.where(Tarefa.titulo.ilike(f"%{busca}%"))
    return db.scalars(consulta).all()


@router.get("/{tarefa_id}", response_model=TarefaOut)
def consultar(tarefa_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, tarefa_id)


@router.post(
    "",
    dependencies=[Depends(usuario_atual)],
    response_model=TarefaOut,
    status_code=status.HTTP_201_CREATED,
)
def criar(dados: TarefaCreate, db: Session = Depends(get_db)):
    _validar_categoria(db, dados.categoria_id)
    tarefa = Tarefa(**dados.model_dump())
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.patch(
    "/{tarefa_id}",
    dependencies=[Depends(usuario_atual)],
    response_model=TarefaOut,
)
def atualizar(tarefa_id: int, dados: TarefaUpdate, db: Session = Depends(get_db)):
    tarefa = _buscar_ou_404(db, tarefa_id)
    alteracoes = dados.model_dump(exclude_unset=True)  # só o que o cliente enviou
    if "categoria_id" in alteracoes:
        _validar_categoria(db, alteracoes["categoria_id"])
    for campo, valor in alteracoes.items():
        setattr(tarefa, campo, valor)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.delete(
    "/{tarefa_id}",
    dependencies=[Depends(usuario_atual)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = _buscar_ou_404(db, tarefa_id)
    db.delete(tarefa)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
