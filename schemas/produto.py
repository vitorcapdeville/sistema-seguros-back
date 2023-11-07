from pydantic import BaseModel, RootModel


class ProdutoSchema(BaseModel):
    """Define como um produto será retornado"""

    id: int = 1
    nome: str = "Pecúlio por Morte"
    descricao: str = (
        "Protege financeiramente a sua família em caso de morte por qualquer causa."
    )


class ListagemProdutosSchema(RootModel):
    """Define como uma listagem de produtos será retornada."""

    root: list[ProdutoSchema]


class ProdutoBuscaSchema(BaseModel):
    """Define como deve ser a estrutura que representa a busca, que será
    feita apenas com base no nome do produto.
    """

    produto_id: int = 1


class PrazoRendaSchema(BaseModel):
    """Define como deve ser a estrutura que representa um prazo de renda de um produto específico."""

    prazo: int = 1
    prazo_certo: int = 1


class BeneficioSchema(BaseModel):
    """Define como deve ser a estrutura que representa um benefício de um produto específico."""

    beneficio_minimo: int = 1
    beneficio_maximo: int = 10


class ParametrosProdutoSchema(BaseModel):
    """Define como deve ser a estrutura que representa os parâmetros de um produto específico."""

    prazos: list[int] = [1, 2, 3]
    prazos_renda: list[PrazoRendaSchema] = [PrazoRendaSchema()]
    beneficio: BeneficioSchema = BeneficioSchema()
