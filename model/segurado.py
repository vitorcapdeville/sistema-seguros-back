from datetime import date

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.database import db
from model.produto import ProdutoPrazo


class Segurado(db.Model):
    __tablename__ = "segurado"
    cpf: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    sexo: Mapped[str] = mapped_column(String(1))
    dataNascimento: Mapped[date]

    matricula: Mapped[list["Matricula"]] = relationship(
        back_populates="segurado", cascade="all, delete-orphan"
    )


class Matricula(db.Model):
    __tablename__ = "matricula"
    id: Mapped[int] = mapped_column(primary_key=True)
    cpfSegurado: Mapped[int] = mapped_column(ForeignKey("segurado.cpf"))
    produtoId: Mapped[int] = mapped_column(ForeignKey("produto.id"))
    dataAssinatura: Mapped[date]
    prazo: Mapped[int] = mapped_column()
    prazoRenda: Mapped[int] = mapped_column(nullable=True)
    prazoCertoRenda: Mapped[int] = mapped_column(nullable=True)
    beneficio: Mapped[float] = mapped_column()

    segurado: Mapped["Segurado"] = relationship(back_populates="matricula")

    __table_args__ = (
        ForeignKeyConstraint(
            [produtoId, prazo],
            [
                ProdutoPrazo.produtoId,
                ProdutoPrazo.prazo,
            ],
        ),
    )
