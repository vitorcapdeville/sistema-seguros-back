from pydantic import BaseModel

from model.produto import Produto


class ProdutoSchema(BaseModel):
    """Define como um produto será retornado"""

    nome: str = "Pecúlio por Morte"
    descricao: str = (
        "Protege financeiramente a sua família em caso de morte por qualquer causa."
    )
    detalhes: list[str] = ["Detalhe 1", "Detalhe 2", "Detalhe 3"]


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
                "nome": produto.nome,
                "descricao": produto.descricao,
            }
        )

    return ListagemProdutosSchema(produtos=result).model_dump()
