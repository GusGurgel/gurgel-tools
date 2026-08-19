from datetime import datetime, timezone
from typing import Annotated, cast

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Relationship, Session, SQLModel, col, func, select

from apps.engine import get_session

# Exact dependency injection pattern requested
SessionDep = Annotated[Session, Depends(get_session)]

# ==========================================
# DATABASE MODELS & SCHEMAS
# ==========================================


class SnippetGroupBase(SQLModel):
    name: str


class SnippetGroup(SnippetGroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # Revertido para timezone.utc para compatibilidade com Python < 3.11
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_copied_at: datetime | None = Field(default=None)

    # type: ignore adicionado porque a tipagem do Relationship no SQLModel resulta em 'Any' para o Pyright
    snippets: list["Snippet"] = Relationship(
        back_populates="group", cascade_delete=True
    )  # type: ignore


class SnippetGroupCreate(SnippetGroupBase):
    pass


class SnippetBase(SQLModel):
    name: str
    content: str
    group_id: int = Field(foreign_key="snippetgroup.id")


class Snippet(SnippetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # type: ignore pelo mesmo motivo da relação acima
    group: SnippetGroup | None = Relationship(back_populates="snippets")  # type: ignore


class SnippetCreate(SnippetBase):
    pass


class SnippetUpdate(SQLModel):
    content: str


# Response schemas
class SnippetRead(SnippetBase):
    id: int


class SnippetGroupRead(SnippetGroupBase):
    id: int
    created_at: datetime
    last_copied_at: datetime | None


class SnippetGroupReadWithSnippets(SnippetGroupRead):
    snippets: list[SnippetRead] = []


# ==========================================
# ROUTING REGISTRATION
# ==========================================


def snippets(app: FastAPI):

    # --- Snippet Groups CRUD ---

    @app.post("/api/snippet-groups", response_model=SnippetGroupRead)
    def create_snippet_group(group: SnippetGroupCreate, session: SessionDep):
        db_group = SnippetGroup.model_validate(group)
        session.add(db_group)
        session.commit()
        session.refresh(db_group)
        return db_group

    @app.get("/api/snippet-groups", response_model=list[SnippetGroupReadWithSnippets])
    def list_snippet_groups(session: SessionDep):
        stmt = select(SnippetGroup).order_by(
            func.coalesce(SnippetGroup.last_copied_at, SnippetGroup.created_at).desc()
        )
        return session.exec(stmt).all()

    @app.delete(
        "/api/snippet-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT
    )
    def delete_snippet_group(group_id: int, session: SessionDep):
        group = session.get(SnippetGroup, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        session.delete(group)
        session.commit()

    # --- Snippets CRUD ---

    @app.post("/api/snippets", response_model=SnippetRead)
    def create_snippet(snippet: SnippetCreate, session: SessionDep):
        group = session.get(SnippetGroup, snippet.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        db_snippet = Snippet.model_validate(snippet)
        session.add(db_snippet)
        session.commit()
        session.refresh(db_snippet)
        return db_snippet

    @app.patch("/api/snippets/{snippet_id}", response_model=SnippetRead)
    def update_snippet(
        snippet_id: int, snippet_update: SnippetUpdate, session: SessionDep
    ):
        db_snippet = session.get(Snippet, snippet_id)
        if not db_snippet:
            raise HTTPException(status_code=404, detail="Snippet not found")
        db_snippet.content = snippet_update.content
        session.add(db_snippet)
        session.commit()
        session.refresh(db_snippet)
        return db_snippet

    @app.delete("/api/snippets/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_snippet(snippet_id: int, session: SessionDep):
        snippet = session.get(Snippet, snippet_id)
        if not snippet:
            raise HTTPException(status_code=404, detail="Snippet not found")
        session.delete(snippet)
        session.commit()

    # --- Specialized Actions & Search ---

    @app.post("/api/snippets/{snippet_id}/copy", status_code=status.HTTP_200_OK)
    def register_copy_action(snippet_id: int, session: SessionDep):
        snippet = session.get(Snippet, snippet_id)
        if not snippet or not snippet.group:
            raise HTTPException(status_code=404, detail="Snippet or Group not found")

        # Substituído para timezone.utc
        snippet.group.last_copied_at = datetime.now(timezone.utc)
        session.add(snippet.group)
        session.commit()
        return {"status": "success"}

    @app.get("/api/search", response_model=list[SnippetGroupReadWithSnippets])
    def search_snippets(
        session: SessionDep,
        # Removido Query() para evitar aviso de função no parâmetro default
        q: str = "",
        type: str = "snippet",
    ):
        if type == "group":
            stmt_group = select(SnippetGroup).where(col(SnippetGroup.name).icontains(q))
            stmt_group = stmt_group.order_by(
                func.coalesce(
                    SnippetGroup.last_copied_at, SnippetGroup.created_at
                ).desc()
            )
            return session.exec(stmt_group).all()
        else:
            stmt_snippet = select(Snippet).where(col(Snippet.name).icontains(q))
            matching_snippets = session.exec(stmt_snippet).all()

            group_map: dict[int, SnippetGroupReadWithSnippets] = {}
            for s in matching_snippets:
                # Removido 's.group_id is None' porque group_id é puramente 'int'
                if not s.group or s.group.id is None:
                    continue

                if s.group_id not in group_map:
                    group_map[s.group_id] = SnippetGroupReadWithSnippets(
                        id=s.group.id,
                        name=s.group.name,
                        created_at=s.group.created_at,
                        last_copied_at=s.group.last_copied_at,
                        snippets=[],
                    )

                snippet_read = SnippetRead(
                    id=cast(int, s.id),
                    name=s.name,
                    content=s.content,
                    group_id=s.group_id,
                )
                group_map[s.group_id].snippets.append(snippet_read)

            sorted_groups = sorted(
                group_map.values(),
                key=lambda g: g.last_copied_at if g.last_copied_at else g.created_at,
                reverse=True,
            )
            return sorted_groups

    # Assinala que as funções foram referenciadas para o linter não reclamar de escopo local inativo
    _ = (
        create_snippet_group,
        list_snippet_groups,
        delete_snippet_group,
        create_snippet,
        update_snippet,
        delete_snippet,
        register_copy_action,
        search_snippets,
    )
