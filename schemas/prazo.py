from pydantic import RootModel

from model.produto import ProdutoPrazo


class ListagemPrazosSchema(RootModel):
    """Representa as possíveis combinações de prazos de um produto."""

    root: list[int] = [10, 20, 30]


def apresenta_prazos(prazos: list[ProdutoPrazo]) -> ListagemPrazosSchema:
    """Apresenta os prazos de pagamento e de cobertura de um produto."""
    result = [prazo.prazo for prazo in prazos]
    return ListagemPrazosSchema(root=result).model_dump()
