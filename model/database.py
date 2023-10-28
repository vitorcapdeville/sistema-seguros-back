from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from datetime import date

engine = create_engine("sqlite:///database/db.sqlite3")
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import model

    Base.metadata.create_all(bind=engine)

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
        model.ProdutoPrazo(
            produtoId=1, prazoPagamento=10, prazoCobertura=10, jurosId=1
        ),
        model.ProdutoPrazo(
            produtoId=1, prazoPagamento=20, prazoCobertura=20, jurosId=2
        ),
        model.ProdutoPrazo(
            produtoId=1, prazoPagamento=30, prazoCobertura=30, jurosId=3
        ),
        model.ProdutoPrazo(
            produtoId=2, prazoPagamento=15, prazoCobertura=15, jurosId=1
        ),
        model.ProdutoPrazo(
            produtoId=2, prazoPagamento=30, prazoCobertura=30, jurosId=3
        ),
    ]

    matricula = [
        model.Matricula(
            matriculaId=1,
            cpfSegurado=12345678900,
            produtoId=1,
            dataAssinatura=date(2020, 1, 1),
            dataInicioVigencia=date(2020, 2, 1),
            prazoCobertura=10,
            prazoPagamento=10,
        ),
        model.Matricula(
            matriculaId=2,
            cpfSegurado=12345678900,
            produtoId=2,
            dataAssinatura=date(2020, 1, 1),
            dataInicioVigencia=date(2020, 2, 1),
            prazoCobertura=15,
            prazoPagamento=15,
        ),
    ]

    db_session.add(segurado)
    db_session.commit()
    db_session.add_all(produtos)
    db_session.commit()
    db_session.add_all(tabuas)
    db_session.commit()
    db_session.add_all(produto_tabua)
    db_session.commit()
    db_session.add_all(juros)
    db_session.commit()
    db_session.add_all(produto_prazo)
    db_session.commit()
    db_session.add_all(matricula)
    db_session.commit()
