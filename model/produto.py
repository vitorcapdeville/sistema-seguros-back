from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.database import db


class Produto(db.Model):
    __tablename__ = "produto"
    produtoId: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    descricao: Mapped[str] = mapped_column(String(100))
    formulaId: Mapped[int] = mapped_column(ForeignKey("formula.formulaId"))

    produtoPrazos: Mapped[list["ProdutoPrazo"]] = relationship(
        back_populates="produto", cascade="all, delete-orphan"
    )
    produtoPrazosRenda: Mapped[list["ProdutoPrazoRenda"]] = relationship(
        back_populates="produto", cascade="all, delete-orphan"
    )
    formula: Mapped["Formula"] = relationship(back_populates="produto")


class ProdutoPrazo(db.Model):
    __tablename__ = "produtoprazo"
    produtoId: Mapped[int] = mapped_column(
        ForeignKey("produto.produtoId"), primary_key=True
    )
    prazo: Mapped[int] = mapped_column(primary_key=True)
    jurosId: Mapped[int] = mapped_column(ForeignKey("juros.jurosId"))

    produto: Mapped["Produto"] = relationship(back_populates="produtoPrazos")
    juros: Mapped["Juros"] = relationship()


class ProdutoTabua(db.Model):
    __tablename__ = "produtotabua"
    produtoId: Mapped[int] = mapped_column(
        ForeignKey("produto.produtoId"), primary_key=True
    )
    sexo: Mapped[str] = mapped_column(String(1), primary_key=True)
    tabuaId: Mapped[int] = mapped_column(ForeignKey("tabua.id"))


class Juros(db.Model):
    __tablename__ = "juros"
    jurosId: Mapped[int] = mapped_column(primary_key=True)
    juros: Mapped[float] = mapped_column()

    produtoPrazos: Mapped[list["ProdutoPrazo"]] = relationship(
        back_populates="juros", cascade="all, delete-orphan"
    )


class ProdutoPrazoRenda(db.Model):
    __tablename__ = "produtoprazorenda"
    produtoId: Mapped[int] = mapped_column(
        ForeignKey("produto.produtoId"), primary_key=True
    )
    prazo: Mapped[int] = mapped_column(primary_key=True)
    prazoCerto: Mapped[int] = mapped_column(primary_key=True)

    produto: Mapped["Produto"] = relationship(back_populates="produtoPrazosRenda")


class Formula(db.Model):
    __tablename__ = "formula"
    formulaId: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))

    produto: Mapped[list["Produto"]] = relationship(back_populates="formula")
