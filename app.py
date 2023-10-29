from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import database_exists

from model import Produto, ProdutoPrazo, db
from model.database import init_db
from model.segurado import Matricula
from model.segurado import Segurado
from schemas import (
    ErrorSchema,
    ListagemPrazosSchema,
    ListagemProdutosSchema,
    ProdutoBuscaSchema,
)
from schemas.cliente import ClienteSchema, apresenta_cliente
from schemas.prazo import apresenta_prazos
from schemas.produto import apresenta_produtos

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
    produto_nome = query.nome
    query = (
        db.select(ProdutoPrazo)
        .join(ProdutoPrazo.produto)
        .where(Produto.nome == produto_nome)
    )
    prazos = db.session.execute(query).scalars()
    if not prazos:
        # se não há produtos cadastrados
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
