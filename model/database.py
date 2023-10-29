from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db(db):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import model

    db.create_all()

    segurado = model.Segurado(
        cpf=12345678900, sexo="M", dataNascimento=date(1990, 1, 1)
    )

    produtos = [
        model.Produto(
            produtoId=1,
            nome="Peculio por morte",
            descricao="Protege financeiramente a sua família em caso de morte por qualquer causa.",
        ),
        model.Produto(
            produtoId=2,
            nome="Outro peculio por morte",
            descricao="Garante uma indenização em caso de invalidez.",
        ),
    ]

    tabuas = [
        model.Tabua(tabuaId=1, nome="AT-2000", tipo="Morte"),
        model.Tabua(tabuaId=2, nome="BREMS MT M", tipo="Morte"),
        model.Tabua(tabuaId=3, nome="BREMS MT F", tipo="Morte"),
    ]

    produto_tabua = [
        model.ProdutoTabua(produtoId=1, sexo="M", tabuaId=1),
        model.ProdutoTabua(produtoId=1, sexo="F", tabuaId=1),
        model.ProdutoTabua(produtoId=2, sexo="M", tabuaId=2),
        model.ProdutoTabua(produtoId=2, sexo="F", tabuaId=3),
    ]

    juros = [
        model.Juros(jurosId=1, juros=0.02),
        model.Juros(jurosId=2, juros=0.04),
        model.Juros(jurosId=3, juros=0.06),
    ]

    produto_prazo = [
        model.ProdutoPrazo(produtoId=1, prazo=10, jurosId=1),
        model.ProdutoPrazo(produtoId=1, prazo=20, jurosId=2),
        model.ProdutoPrazo(produtoId=1, prazo=30, jurosId=3),
        model.ProdutoPrazo(produtoId=2, prazo=15, jurosId=1),
        model.ProdutoPrazo(produtoId=2, prazo=30, jurosId=3),
    ]

    matricula = [
        model.Matricula(
            matriculaId=1,
            cpfSegurado=12345678900,
            produtoId=1,
            dataAssinatura=date(2020, 1, 1),
            prazoCobertura=10,
            prazoPagamento=10,
            segurado=segurado,
        ),
        model.Matricula(
            matriculaId=2,
            cpfSegurado=12345678900,
            produtoId=2,
            dataAssinatura=date(2020, 1, 1),
            prazoCobertura=15,
            prazoPagamento=15,
            segurado=segurado,
        ),
    ]

    # db.session.add(segurado)
    # db.session.commit()
    db.session.add_all(produtos)
    db.session.commit()
    db.session.add_all(tabuas)
    db.session.commit()
    db.session.add_all(produto_tabua)
    db.session.commit()
    db.session.add_all(juros)
    db.session.commit()
    db.session.add_all(produto_prazo)
    db.session.commit()
    db.session.add_all(matricula)
    db.session.commit()
