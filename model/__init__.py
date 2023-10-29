from model.database import db
from model.juros import Juros
from model.segurado import Matricula
from model.produto import Produto, ProdutoPrazo, ProdutoTabua
from model.segurado import Segurado
from model.tabua import Tabua

__all__ = [
    "Produto",
    "Juros",
    "Matricula",
    "ProdutoPrazo",
    "ProdutoTabua",
    "Segurado",
    "Tabua",
    "db",
]
