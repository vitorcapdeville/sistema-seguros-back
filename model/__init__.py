from model.database import db
from model.produto import (
    Produto,
    ProdutoPrazo,
    ProdutoTabua,
    Juros,
    ProdutoPrazoRenda,
    Formula,
    TipoTabua,
)
from model.segurado import Matricula, Segurado
from model.tabua import Tabua, Taxa

__all__ = [
    "Produto",
    "Juros",
    "Matricula",
    "ProdutoPrazo",
    "ProdutoPrazoRenda",
    "ProdutoTabua",
    "TipoTabua",
    "Formula",
    "Segurado",
    "Tabua",
    "Taxa",
    "db",
]
