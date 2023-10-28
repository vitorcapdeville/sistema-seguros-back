from datetime import date
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from model.database import db


class Segurado(db.Model):
    __tablename__ = "segurado"
    cpf: Mapped[int] = mapped_column(primary_key=True)
    sexo: Mapped[str] = mapped_column(String(1))
    dataNascimento: Mapped[date]
