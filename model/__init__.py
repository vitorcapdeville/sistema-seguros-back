from model.produto import Produto
from model.juros import Juros
from model.matricula import Matricula
from model.produto_prazo import ProdutoPrazo
from model.produto_tabua import ProdutoTabua
from model.segurado import Segurado
from model.tabua import Tabua
from model.database import engine, init_db
from sqlalchemy_utils import database_exists

__all__ = [
    "Produto",
    "Juros",
    "Matricula",
    "ProdutoPrazo",
    "ProdutoTabua",
    "Segurado",
    "Tabua",
]

if not database_exists(engine.url):
    init_db()
