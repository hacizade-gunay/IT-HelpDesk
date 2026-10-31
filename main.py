import os
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Ticket

# --- Database ---------------------------------------------------------------
# Default: SQLite (quraşdırma tələb etmir). SQL Server üçün mühit dəyişəni:
# DATABASE_URL="mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Schemas (input validation) --------------------------------------------
class Status(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Category(str, Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    ACCOUNT = "Account"
    OTHER = "Other"


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5, max_length=2000)
    category: Category
    priority: Priority = Priority.MEDIUM


class StatusUpdate(BaseModel):
    status: Status


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime


# --- App --------------------------------------------------------------------
app = FastAPI(title="IT Help Desk API")

app.add_middleware(  # frontend-in başqa portdan sorğu göndərə bilməsi üçün
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(
        title=data.title.strip(),
        description=data.description.strip(),
        category=data.category.value,
        priority=data.priority.value,
        status=Status.NEW.value,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    category: Optional[Category] = None,
    status: Optional[Status] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)
    if category:
        query = query.filter(Ticket.category == category.value)
    if status:
        query = query.filter(Ticket.status == status.value)
    return query.order_by(Ticket.created_at.desc()).all()


# Diqqət: /tickets/stats, /tickets/{ticket_id}-dən ƏVVƏL yazılmalıdır
@app.get("/tickets/stats")
def ticket_stats(db: Session = Depends(get_db)):
    rows = db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    by_status = {s.value: 0 for s in Status}
    by_status.update({status: count for status, count in rows})
    return {"total": sum(by_status.values()), "by_status": by_status}


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Müraciət tapılmadı")
    return ticket


@app.patch("/tickets/{ticket_id}/status", response_model=TicketOut)
def update_status(ticket_id: int, data: StatusUpdate, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Müraciət tapılmadı")
    ticket.status = data.status.value
    db.commit()
    db.refresh(ticket)
    return ticket
