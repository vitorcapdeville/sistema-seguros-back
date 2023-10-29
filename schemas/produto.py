from pydantic import BaseModel

from model.produto import Produto


class ProdutoSchema(BaseModel):
    """Define como um produto será retornado"""

    id: int = 0
    nome: str = "Pecúlio por Morte"
    descricao: str = (
        "Protege financeiramente a sua família em caso de morte por qualquer causa."
    )


class ListagemProdutosSchema(BaseModel):
    """Define como uma listagem de produtos será retornada."""

    produtos: list[ProdutoSchema]


def apresenta_produtos(produtos: list[Produto]):
    """Retorna uma representação do produto seguindo o schema definido em
    ProdutoViewSchema.
    """
    result = []
    for produto in produtos:
        result.append(
            {
                "id": produto.produtoId,
                "nome": produto.nome,
                "descricao": produto.descricao,
            }
        )

    return ListagemProdutosSchema(produtos=result).model_dump()


class ProdutoBuscaSchema(BaseModel):
    """Define como deve ser a estrutura que representa a busca, que será
    feita apenas com base no nome do produto.
    """

    nome: str = "Teste"
