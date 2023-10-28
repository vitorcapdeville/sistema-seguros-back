from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from model.database import db


class Produto(db.Model):
    __tablename__ = "produto"
    produtoId: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    descricao: Mapped[str] = mapped_column(String(100))
