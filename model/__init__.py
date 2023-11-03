from model.database import db
from model.produto import Produto, ProdutoPrazo, ProdutoTabua, Juros
from model.segurado import Matricula, Segurado
from model.tabua import Tabua, Taxa

__all__ = [
    "Produto",
    "Juros",
    "Matricula",
    "ProdutoPrazo",
    "ProdutoTabua",
    "Segurado",
    "Tabua",
    "Taxa",
    "db",
]
