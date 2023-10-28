from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from model.database import Base


class ProdutoTabua(Base):
    __tablename__ = "produtotabua"
    produtoId: Mapped[int] = mapped_column(
        ForeignKey("produto.produtoId"), primary_key=True
    )
    sexo: Mapped[str] = mapped_column(String(1), primary_key=True)
    tabuaId: Mapped[int] = mapped_column(ForeignKey("tabua.tabuaId"))
