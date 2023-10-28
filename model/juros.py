from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from model.database import db


class Juros(db.Model):
    __tablename__ = "juros"
    jurosId: Mapped[int] = mapped_column(primary_key=True)
    juros: Mapped[float]
