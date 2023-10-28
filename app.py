from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from sqlalchemy_utils import database_exists

from model import Produto, db
from model.database import init_db
from schemas import ErrorSchema, ListagemProdutosSchema
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
produto_tag = Tag(
    name="Produto", description="Adição, visualização e remoção de produtos à base"
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
