from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, select

from apps.engine import get_session


# Classe base com campos comuns
class ItemBase(SQLModel):
    nome: str
    preco: float
    descricao: str | None = None


# Tabela do banco de dados
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# Schema para criação (payload de entrada)
class ItemCreate(ItemBase):
    pass


SessionDep = Annotated[Session, Depends(get_session)]


def example(app: FastAPI):
    @app.post(
        "example/items/", response_model=Item, status_code=status.HTTP_201_CREATED
    )
    def create_item(item: ItemCreate, session: SessionDep):
        db_item = Item.model_validate(item)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    @app.get("/example/items/", response_model=list[Item])
    def read_items(
        session: SessionDep,
    ):  # 2. Use a anotação aqui, sem valor padrão (sem o sinal de "=")
        items = session.exec(select(Item)).all()
        return items

    @app.get("/example/items/{item_id}", response_model=Item)
    def read_item(item_id: int, session: SessionDep):
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return item
