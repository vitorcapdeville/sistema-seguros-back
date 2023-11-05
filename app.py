from datetime import date

import tabatu as tb
from flask import redirect, url_for
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy_utils import database_exists

from model.database import db, init_db
from model.produto import Produto
from model.queries import (
    pegar_formula,
    pegar_juros,
    pegar_parametros_produto,
    pegar_taxas,
)
from model.segurado import Matricula, Segurado
from schemas.cliente import ClienteSchema
from schemas.error import ErrorSchema
from schemas.produto import (
    ListagemProdutosSchema,
    ParametrosProdutoSchema,
    PrazoRendaSchema,
    ProdutoBuscaSchema,
)
from schemas.simulacao import (
    ResultadoSimulacaoSchema,
    SimulacaoAposentadoriaSchema,
    SimulacaoPeculioSchema,
    SimulacaoSchema,
)
from src.produtos.aposentadoria import aposentadoria_capitalizado
from src.produtos.peculio import peculio_capitalizado_fluxo

info = Info(title="Sistema Seguros", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)

with app.app_context():
    if not database_exists(db.engine.url):
        print("Inicializando o banco de dados.")
        init_db(db)

home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc",
)
produto_tag = Tag(
    name="Produto",
    description="Consulta produtos disponíveis e informações adicionais sobre eles.",
)
simular_tag = Tag(
    name="Simular",
    description="Realiza simulações para potenciais novos clientes.",
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
    """Faz a busca por todos os produto cadastrados.

    Retorna uma representação da listagem de produtos.
    """
    produtos = db.session.execute(db.select(Produto)).scalars()

    result = []
    for produto in produtos:
        result.append(
            {
                "id": produto.produtoId,
                "nome": produto.nome,
                "descricao": produto.descricao,
            }
        )

    return ListagemProdutosSchema(result).model_dump(), 200


@app.get(
    "/produtos/<int:produto_id>",
    tags=[produto_tag],
    responses={"200": ParametrosProdutoSchema, "404": ErrorSchema},
)
def get_parametros_produto(path: ProdutoBuscaSchema):
    """Faz a busca pelos parâmetros de um produto específico.

    Retorna os prazos e os prazos de renda e renda certa disponíveis para contratação
    e a fórmula utilizada para simulação.
    """
    try:
        prazos, prazos_renda = pegar_parametros_produto(db, path.produto_id)
    except NoResultFound:
        return (
            ErrorSchema(
                mesage=f"Produto {path.produto_id} não encontrado."
            ).model_dump(),
            404,
        )

    prazos = [prazo.prazo for prazo in prazos]
    prazos_renda = [
        PrazoRendaSchema(prazo=prazo.prazo, prazo_certo=prazo.prazoCerto)
        for prazo in prazos_renda
    ]

    return (
        ParametrosProdutoSchema(prazos=prazos, prazos_renda=prazos_renda).model_dump(),
        200,
    )


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
        beneficio=form.beneficio,
    )
    try:
        db.session.add(cliente)
        db.session.commit()
        return form.model_dump(), 200

    except IntegrityError:
        return ErrorSchema(message="Cliente já existe na base.").model_dump(), 409

    except Exception as e:
        return ErrorSchema(message=e).model_dump(), 400


@app.get(
    "/simular",
    tags=[simular_tag],
    responses={
        "200": ResultadoSimulacaoSchema,
        "302": {"description": "Redirecianado para a rota de simulação adequada."},
        "404": ErrorSchema,
    },
)
def get_simulacao(query: SimulacaoSchema):
    """Faz a simulação de um produto genérico.

    Essa rota recebe um produto e um conjunto de parâmetros e redireciona para a rota
    adequada para simulação do produto. Os parâmetros podem conter valores que não
    serão utilizados.
    """
    try:
        formula = pegar_formula(db, query.produto_id)
    except NoResultFound:
        return (
            ErrorSchema(
                mesage=f"Produto {query.produto_id} não encontrado."
            ).model_dump(),
            404,
        )
    return redirect(url_for(f"get_simulacao_{formula.nome}", **query.model_dump()))


@app.get(
    "/simular/peculio",
    tags=[simular_tag],
    responses={"200": ResultadoSimulacaoSchema, "400": ErrorSchema, "404": ErrorSchema},
)
def get_simulacao_peculio(query: SimulacaoPeculioSchema):
    """Faz a simulação de um produto do tipo pecúlio.

    Retorna o valor do prêmio comercial para o produto e os parâmetros informados."""
    try:
        juros = pegar_juros(db, query.produto_id, query.prazo)
        taxa = pegar_taxas(db, query.produto_id, query.sexo, "Sinistro")
        taxa_dpi = pegar_taxas(db, query.produto_id, query.sexo, "DPI")
    except NoResultFound:
        return (
            ErrorSchema(
                mesage=f"Produto {query.produto_id} não encontrado."
            ).model_dump(),
            404,
        )

    try:
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
            beneficio=query.beneficio,
            percentual_beneficio=[1.0],
        )

    except Exception as e:
        return ErrorSchema(message=e).model_dump(), 400

    return (
        ResultadoSimulacaoSchema(premio=produto.premio_comercial(0)).model_dump(),
        200,
    )


@app.get(
    "/simular/aposentadoria",
    tags=[simular_tag],
    responses={"200": ResultadoSimulacaoSchema, "400": ErrorSchema, "404": ErrorSchema},
)
def get_simulacao_aposentadoria(query: SimulacaoAposentadoriaSchema):
    """Faz a simulação de um produto do tipo aposentadoria.

    Retorna o valor do prêmio comercial para o produto e os parâmetros informados."""
    try:
        juros = pegar_juros(db, query.produto_id, query.prazo)
        taxa_acumulacao = pegar_taxas(db, query.produto_id, query.sexo, "Acumulacao")
        taxa_concessao = pegar_taxas(db, query.produto_id, query.sexo, "Concessao")
    except NoResultFound:
        return (
            ErrorSchema(
                mesage=f"Produto {query.produto_id} não encontrado."
            ).model_dump(),
            404,
        )

    try:
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
            beneficio=query.beneficio,
            percentual_beneficio=[1.0],
        )
    except Exception as e:
        return ErrorSchema(message=e).model_dump(), 400

    return (
        ResultadoSimulacaoSchema(premio=produto.premio_comercial(0)).model_dump(),
        200,
    )
