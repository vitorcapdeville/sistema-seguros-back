from model.produto import (
    Formula,
    Juros,
    Produto,
    ProdutoPrazo,
    ProdutoPrazoRenda,
    ProdutoTabua,
    TipoTabua,
)
from model.tabua import Tabua, Taxa


def pegar_juros(db, produto_id: int, prazo: int) -> float:
    query = (
        db.select(Juros.juros)
        .join(Juros.produtoPrazos)
        .where(ProdutoPrazo.produtoId == produto_id)
        .where(ProdutoPrazo.prazo == prazo)
    )
    return db.session.execute(query).scalars().one()


def pegar_taxas(db, produto_id: int, sexo: str, tipo_tabua: str) -> list[float]:
    query = (
        db.select(Taxa.taxa)
        .join(Tabua, Taxa.tabuaId == Tabua.id)
        .join(ProdutoTabua, ProdutoTabua.tabuaId == Tabua.id)
        .join(TipoTabua, TipoTabua.id == ProdutoTabua.tipoTabuaId)
        .where(ProdutoTabua.produtoId == produto_id)
        .where(ProdutoTabua.sexo == sexo)
        .where(TipoTabua.nome == tipo_tabua)
    )
    return db.session.execute(query).scalars().all()


def pegar_formula(db, produto_id):
    query = (
        db.select(Formula.nome)
        .join(Formula.produto)
        .where(Produto.produtoId == produto_id)
    )
    return db.session.execute(query).scalars().one()


def pegar_prazos_renda(db, produto_id):
    query = (
        db.select(ProdutoPrazoRenda)
        .join(ProdutoPrazoRenda.produto)
        .where(Produto.produtoId == produto_id)
    )
    return db.session.execute(query).scalars().all()


def pegar_prazos(db, produto_id):
    query = (
        db.select(ProdutoPrazo)
        .join(ProdutoPrazo.produto)
        .where(Produto.produtoId == produto_id)
    )
    return db.session.execute(query).scalars().all()