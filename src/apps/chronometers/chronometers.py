from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Relationship, Session, SQLModel, select

from apps.engine import get_session

SessionDep = Annotated[Session, Depends(get_session)]

# --- MODELS ---


class ChronoGroup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    icon: str
    icon_color: str = Field(default="#0172ad")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    chronometers: list["Chronometer"] = Relationship(
        back_populates="group", cascade_delete=True
    )


class Chronometer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    icon: str
    icon_color: str = Field(default="#0172ad")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    group_id: int = Field(foreign_key="chronogroup.id")
    group: ChronoGroup | None = Relationship(back_populates="chronometers")

    accumulated_seconds: int = Field(default=0)
    is_running: bool = Field(default=False)
    last_started_at: datetime | None = Field(default=None)
    last_elapsed_seconds: int = Field(default=0)


# --- SCHEMAS (For input validation) ---


class ChronoGroupCreate(BaseModel):
    name: str
    icon: str
    icon_color: str


class ChronometerCreate(BaseModel):
    name: str
    icon: str
    icon_color: str
    group_id: int


class UpdateTimeSchema(BaseModel):
    total_seconds: int


# --- HELPER FUNCTIONS ---


def _stop_running_chronometers(session: Session, except_id: int | None = None):
    """Stops all running chronometers globally, calculating their elapsed time."""
    query = select(Chronometer).where(Chronometer.is_running == True)
    if except_id is not None:
        query = query.where(Chronometer.id != except_id)

    running_chronos = session.exec(query).all()
    now = datetime.now(UTC)

    for chrono in running_chronos:
        if chrono.last_started_at:
            start_time = (
                chrono.last_started_at.replace(tzinfo=UTC)
                if chrono.last_started_at.tzinfo is None
                else chrono.last_started_at
            )
            elapsed = int((now - start_time).total_seconds())
            chrono.accumulated_seconds += elapsed
            chrono.last_elapsed_seconds = elapsed

        chrono.is_running = False
        # Removido: chrono.last_started_at = None (Para manter a data visível no frontend)
        session.add(chrono)

    session.commit()


# --- MAIN APP REGISTRATION ---


def chronometers(app: FastAPI):

    # -- ChronoGroup CRUD --

    @app.get("/api/chrono-groups", response_model=list[ChronoGroup])
    def get_chrono_groups(session: SessionDep):
        return session.exec(select(ChronoGroup)).all()

    @app.post("/api/chrono-groups", response_model=ChronoGroup)
    def create_chrono_group(group_in: ChronoGroupCreate, session: SessionDep):
        group = ChronoGroup(
            name=group_in.name, icon=group_in.icon, icon_color=group_in.icon_color
        )
        session.add(group)
        session.commit()
        session.refresh(group)
        return group

    @app.delete("/api/chrono-groups/{id}")
    def delete_chrono_group(id: int, session: SessionDep):
        group = session.get(ChronoGroup, id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        session.delete(group)
        session.commit()
        return {"ok": True}

    # -- Chronometer CRUD & Actions --

    @app.get("/api/chronometers", response_model=list[Chronometer])
    def get_chronometers(session: SessionDep):
        return session.exec(select(Chronometer)).all()

    @app.post("/api/chronometers", response_model=Chronometer)
    def create_chronometer(chrono_in: ChronometerCreate, session: SessionDep):
        if not session.get(ChronoGroup, chrono_in.group_id):
            raise HTTPException(status_code=404, detail="Group not found")

        chrono = Chronometer(
            name=chrono_in.name,
            icon=chrono_in.icon,
            icon_color=chrono_in.icon_color,
            group_id=chrono_in.group_id,
        )
        session.add(chrono)
        session.commit()
        session.refresh(chrono)
        return chrono

    @app.delete("/api/chronometers/{id}")
    def delete_chronometer(id: int, session: SessionDep):
        chrono = session.get(Chronometer, id)
        if not chrono:
            raise HTTPException(status_code=404, detail="Chronometer not found")
        session.delete(chrono)
        session.commit()
        return {"ok": True}

    @app.post("/api/chronometers/{id}/start", response_model=Chronometer)
    def start_chronometer(id: int, session: SessionDep):
        chrono = session.get(Chronometer, id)
        if not chrono:
            raise HTTPException(status_code=404, detail="Chronometer not found")

        if chrono.is_running:
            return chrono

        # Somente 1 cronômetro rodando globalmente
        _stop_running_chronometers(session, except_id=id)

        chrono.is_running = True
        chrono.last_started_at = datetime.now(UTC)
        session.add(chrono)
        session.commit()
        session.refresh(chrono)
        return chrono

    @app.post("/api/chronometers/{id}/stop", response_model=Chronometer)
    def stop_chronometer(id: int, session: SessionDep):
        chrono = session.get(Chronometer, id)
        if not chrono:
            raise HTTPException(status_code=404, detail="Chronometer not found")

        if not chrono.is_running:
            return chrono

        now = datetime.now(UTC)
        if chrono.last_started_at:
            start_time = (
                chrono.last_started_at.replace(tzinfo=UTC)
                if chrono.last_started_at.tzinfo is None
                else chrono.last_started_at
            )
            elapsed = int((now - start_time).total_seconds())
            chrono.accumulated_seconds += elapsed
            chrono.last_elapsed_seconds = elapsed

        chrono.is_running = False
        # Removido: chrono.last_started_at = None (Para manter a data visível no frontend)
        session.add(chrono)
        session.commit()
        session.refresh(chrono)
        return chrono

    @app.patch("/api/chronometers/{id}/update_time", response_model=Chronometer)
    def update_time(id: int, payload: UpdateTimeSchema, session: SessionDep):
        chrono = session.get(Chronometer, id)
        if not chrono:
            raise HTTPException(status_code=404, detail="Chronometer not found")

        chrono.accumulated_seconds = payload.total_seconds
        session.add(chrono)
        session.commit()
        session.refresh(chrono)
        return chrono
