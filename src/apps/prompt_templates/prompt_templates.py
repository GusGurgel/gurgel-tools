from datetime import datetime, timezone
from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, col, select

from apps.engine import get_session

SessionDep = Annotated[Session, Depends(get_session)]

# --- MODELS ---


class PromptTemplateBase(SQLModel):
    name: str
    description: Optional[str] = None
    content: str


class PromptTemplate(PromptTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_copied_at: Optional[datetime] = None


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


# --- ROUTER REGISTRATION ---


def prompt_templates(app: FastAPI):

    @app.get("/api/prompt-templates", response_model=List[PromptTemplate])
    def get_prompt_templates(session: SessionDep):
        # Use sqlmodel's `col()` to prevent type checker errors (Mypy/Pylance)
        statement = select(PromptTemplate).order_by(
            col(PromptTemplate.last_copied_at).desc().nulls_last(),
            col(PromptTemplate.created_at).desc(),
        )
        return session.exec(statement).all()

    @app.get("/api/prompt-templates/{template_id}", response_model=PromptTemplate)
    def get_prompt_template(template_id: int, session: SessionDep):
        template = session.get(PromptTemplate, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template

    @app.post(
        "/api/prompt-templates",
        response_model=PromptTemplate,
        status_code=status.HTTP_201_CREATED,
    )
    def create_prompt_template(template_in: PromptTemplateCreate, session: SessionDep):
        new_template = PromptTemplate.model_validate(template_in)
        session.add(new_template)
        session.commit()
        session.refresh(new_template)
        return new_template

    @app.put("/api/prompt-templates/{template_id}", response_model=PromptTemplate)
    def update_prompt_template(
        template_id: int, template_in: PromptTemplateUpdate, session: SessionDep
    ):
        template = session.get(PromptTemplate, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        update_data = template_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)

        template.updated_at = datetime.now(timezone.utc)
        session.add(template)
        session.commit()
        session.refresh(template)
        return template

    @app.delete(
        "/api/prompt-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT
    )
    def delete_prompt_template(template_id: int, session: SessionDep):
        template = session.get(PromptTemplate, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        session.delete(template)
        session.commit()

    @app.patch(
        "/api/prompt-templates/{template_id}/copied", response_model=PromptTemplate
    )
    def mark_template_copied(template_id: int, session: SessionDep):
        template = session.get(PromptTemplate, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        template.last_copied_at = datetime.now(timezone.utc)
        session.add(template)
        session.commit()
        session.refresh(template)
        return template
