from datetime import date
from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from model.database import Base
from model.produto_prazo import ProdutoPrazo


class Matricula(Base):
    __tablename__ = "matricula"
    matriculaId: Mapped[int] = mapped_column(primary_key=True)
    cpfSegurado: Mapped[int] = mapped_column(ForeignKey("segurado.cpf"))
    produtoId: Mapped[int] = mapped_column(ForeignKey("produto.produtoId"))
    dataAssinatura: Mapped[date]
    dataInicioVigencia: Mapped[date]
    prazoPagamento: Mapped[int] = mapped_column()
    prazoCobertura: Mapped[int] = mapped_column()

    __table_args__ = (
        ForeignKeyConstraint(
            [produtoId, prazoPagamento, prazoCobertura],
            [
                ProdutoPrazo.produtoId,
                ProdutoPrazo.prazoPagamento,
                ProdutoPrazo.prazoCobertura,
            ],
        ),
    )
