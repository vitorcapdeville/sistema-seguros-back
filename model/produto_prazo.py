from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from model.database import db


class ProdutoPrazo(db.Model):
    __tablename__ = "produtoprazo"
    produtoId: Mapped[int] = mapped_column(
        ForeignKey("produto.produtoId"), primary_key=True
    )
    prazoPagamento: Mapped[int] = mapped_column(primary_key=True)
    prazoCobertura: Mapped[int] = mapped_column(primary_key=True)
    jurosId: Mapped[int] = mapped_column(ForeignKey("juros.jurosId"))
