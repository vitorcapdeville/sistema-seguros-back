from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.database import db


class Tabua(db.Model):
    __tablename__ = "tabua"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    tipo: Mapped[str] = mapped_column(String(50))

    taxa: Mapped[list["Taxa"]] = relationship(
        back_populates="tabua", cascade="all, delete-orphan"
    )


class Taxa(db.Model):
    __tablename__ = "taxa"
    tabuaId: Mapped[int] = mapped_column(ForeignKey("tabua.id"), primary_key=True)
    idade: Mapped[int] = mapped_column(primary_key=True)
    taxa: Mapped[float] = mapped_column()

    tabua: Mapped["Tabua"] = relationship(back_populates="taxa")
