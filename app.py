from datetime import date

import tabatu as tb
from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import database_exists

from model.database import db, init_db
from model.produto import Produto
from model.queries import (
    pegar_formula,
    pegar_juros,
    pegar_prazos,
    pegar_prazos_renda,
    pegar_taxas,
)
from model.segurado import Matricula, Segurado
from schemas import (
    ClienteSchema,
    ErrorSchema,
    FormulaSchema,
    ListagemPrazosRendaSchema,
    ListagemPrazosSchema,
    ListagemProdutosSchema,
    ProdutoBuscaSchema,
    ResultadoSimulacaoSchema,
    SimulacaoAposentadoriaSchema,
    SimulacaoPeculioSchema,
    apresenta_cliente,
    apresenta_prazos,
    apresenta_prazos_renda,
    apresenta_produtos,
)
from src.produtos.aposentadoria import aposentadoria_capitalizado
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
    produtos = db.session.execute(db.select(Produto)).scalars()

    if not produtos:
        return {"produtos": []}, 200
    else:
        return apresenta_produtos(produtos), 200


@app.get(
    "/prazos",
    tags=[prazos_tag],
    responses={"200": ListagemPrazosSchema, "404": ErrorSchema},
)
def get_prazos(query: ProdutoBuscaSchema):
    prazos = pegar_prazos(db, query.produto_id)
    if not prazos:
        return [], 200
    else:
        return apresenta_prazos(prazos), 200


@app.get(
    "/prazos_renda",
    tags=[prazos_tag],
    responses={"200": ListagemPrazosRendaSchema, "404": ErrorSchema},
)
def get_prazos_renda(query: ProdutoBuscaSchema):
    prazos = pegar_prazos_renda(db, query.produto_id)
    if not prazos:
        return [], 200
    return apresenta_prazos_renda(prazos), 200


@app.get(
    "/formula",
    tags=[prazos_tag],
    responses={"200": FormulaSchema, "404": ErrorSchema},
)
def get_formula(query: ProdutoBuscaSchema):
    formula = pegar_formula(db, query.produto_id)
    if not formula:
        return {
            "mesage": f"Formula nao encontrada para produto {query.produto_id}"
        }, 400
    return FormulaSchema(formula=formula).model_dump(), 200


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
        prazo=form.prazo,
        prazoRenda=form.prazo_renda,
        prazoCertoRenda=form.prazo_certo_renda,
    )
    try:
        db.session.add(cliente)
        db.session.commit()
        return apresenta_cliente(form), 200

    except IntegrityError as e:
        print(e)
        error_msg = "Cliente já existe na base."
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo cliente."
        print(e)
        return {"mesage": error_msg}, 400


@app.get(
    "/simular/peculio",
    tags=[prazos_tag],
    responses={"200": ResultadoSimulacaoSchema, "404": ErrorSchema},
)
def get_simulacao_peculio(query: SimulacaoPeculioSchema):
    try:
        juros = pegar_juros(db, query.produto_id, query.prazo)
        taxa = pegar_taxas(db, query.produto_id, query.sexo, "Sinistro")
        taxa_dpi = pegar_taxas(db, query.produto_id, query.sexo, "DPI")
        tabua_sinistro = tb.Tabua(taxa)
        tabua_pagamento = tabua_sinistro

        if len(taxa_dpi) > 0:
            tabua_dpi = tb.Tabua(taxa_dpi)
            tabua_pagamento = tb.TabuaMDT(tabua_sinistro, tabua_dpi)

        produto = peculio_capitalizado_fluxo(
            tabua_beneficio=tabua_sinistro,
            tabua_pagamento=tabua_pagamento,
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
        return {"mesage": f"Não foi possível realizar a simulação. \n {e}"}, 400

    return (
        ResultadoSimulacaoSchema(premio=produto.premio_comercial(0)).model_dump(),
        200,
    )


@app.get(
    "/simular/aposentadoria",
    tags=[prazos_tag],
    responses={"200": ResultadoSimulacaoSchema, "404": ErrorSchema},
)
def get_simulacao_aposentadoria(query: SimulacaoAposentadoriaSchema):
    try:
        juros = pegar_juros(db, query.produto_id, query.prazo)
        taxa_acumulacao = pegar_taxas(db, query.produto_id, query.sexo, "Acumulacao")
        taxa_concessao = pegar_taxas(db, query.produto_id, query.sexo, "Concessao")
        produto = aposentadoria_capitalizado(
            tabua_acumulacao=tb.Tabua(taxa_acumulacao),
            tabua_concessao=tb.Tabua(taxa_concessao),
            juros=tb.JurosConstante(juros),
            data_assinatura=date.today(),
            data_nascimento_segurado=query.data_nascimento,
            prazo_cobertura=query.prazo,
            prazo_pagamento=query.prazo,
            prazo_renda=query.prazo_renda,
            prazo_certo_renda=query.prazo_certo_renda,
            beneficio=2000,
            percentual_beneficio=[1.0],
        )
    except Exception as e:
        return {"mesage": e}, 400

    return (
        ResultadoSimulacaoSchema(premio=produto.premio_comercial(0)).model_dump(),
        200,
    )
