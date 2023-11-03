from datetime import date
import tabatu as tb
from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import database_exists

from model import (
    Juros,
    Matricula,
    Produto,
    ProdutoPrazo,
    ProdutoTabua,
    Segurado,
    Tabua,
    Taxa,
    db,
)
from model.database import init_db
from schemas import (
    ErrorSchema,
    InputSimulacaoSchema,
    ListagemPrazosSchema,
    ListagemProdutosSchema,
    ProdutoBuscaSchema,
    ResultadoSimulacaoSchema,
    ClienteSchema,
    apresenta_cliente,
    apresenta_prazos,
    apresenta_produtos,
)

from src.produtos.peculio import peculio_capitalizado_fluxo

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
# initialize the app with the extension
db.init_app(app)

# db.engine.url
with app.app_context():
    if not database_exists(db.engine.url):
        print("Inicializando o banco de dados.")
        init_db(db)

# definindo tags
home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc",
)
produto_tag = Tag(name="Produto", description="Consulta de produtos.")
prazos_tag = Tag(
    name="Prazos",
    description="Consulta de prazos de pagamento e de cobertura de produtos.",
)
contratar_tag = Tag(
    name="Contratar",
    description="Realiza o cadastro de um novo cliente.",
)


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")


@app.get(
    "/produtos",
    tags=[produto_tag],
    responses={"200": ListagemProdutosSchema, "404": ErrorSchema},
)
def get_produtos():
    """Faz a busca por todos os Produto cadastrados

    Retorna uma representação da listagem de produtos.
    """
    # fazendo a busca
    produtos = db.session.execute(db.select(Produto)).scalars()

    if not produtos:
        # se não há produtos cadastrados
        return {"produtos": []}, 200
    else:
        return apresenta_produtos(produtos), 200


@app.get(
    "/prazos",
    tags=[prazos_tag],
    responses={"200": ListagemPrazosSchema, "404": ErrorSchema},
)
def get_prazos(query: ProdutoBuscaSchema):
    query = (
        db.select(ProdutoPrazo)
        .join(ProdutoPrazo.produto)
        .where(Produto.produtoId == query.produto_id)
    )
    prazos = db.session.execute(query).scalars()
    if not prazos:
        return {"prazos": []}, 200
    else:
        return apresenta_prazos(prazos), 200


@app.post(
    "/contratar",
    tags=[contratar_tag],
    responses={"200": ClienteSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def add_cliente(form: ClienteSchema):
    """Adiciona um novo cliente à base de dados

    Retorna as informações do cliente adicionado.
    """
    segurado = db.session.query(Segurado).filter_by(cpf=form.cpf).first()
    if not segurado:
        segurado = Segurado(
            cpf=form.cpf,
            sexo=form.sexo,
            dataNascimento=form.data_nascimento,
        )
        db.session.add(segurado)

    cliente = Matricula(
        cpfSegurado=form.cpf,
        produtoId=form.produto_id,
        dataAssinatura=form.data_assinatura,
        prazoPagamento=form.prazo,
        prazoCobertura=form.prazo,
    )
    try:
        db.session.add(cliente)
        db.session.commit()
        return apresenta_cliente(form), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Cliente já existe na base."
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo cliente."
        print(e)
        return {"mesage": error_msg}, 400


@app.get(
    "/simular",
    tags=[prazos_tag],
    responses={"200": ResultadoSimulacaoSchema, "404": ErrorSchema},
)
def get_simulacao(query: InputSimulacaoSchema):
    query_juros = (
        db.select(Juros.juros)
        .join(Juros.produtoPrazos)
        .where(ProdutoPrazo.produtoId == query.produto_id)
        .where(ProdutoPrazo.prazo == query.prazo)
    )

    query_taxa = (
        db.select(Taxa.taxa)
        .join(Tabua, Taxa.tabuaId == Tabua.id)
        .join(ProdutoTabua, ProdutoTabua.tabuaId == Tabua.id)
        .where(ProdutoTabua.produtoId == query.produto_id)
        .where(ProdutoTabua.sexo == query.sexo)
    )

    try:
        juros = db.session.execute(query_juros).scalars().one()
        taxa = db.session.execute(query_taxa).scalars().all()
        produto = peculio_capitalizado_fluxo(
            tabua_beneficio=tb.Tabua(taxa),
            tabua_pagamento=tb.Tabua(taxa),
            juros=tb.JurosConstante(juros),
            data_assinatura=date.today(),
            data_nascimento_segurado=query.data_nascimento,
            prazo_cobertura=query.prazo,
            prazo_pagamento=query.prazo,
            beneficio=1000000,
            percentual_beneficio=[1.0],
        )
    except Exception as e:
        print(e)
        return {"mesage": "Não foi possível realizar a simulação."}, 400
    return (
        ResultadoSimulacaoSchema(premio=produto.premio_comercial(0)).model_dump(),
        200,
    )
