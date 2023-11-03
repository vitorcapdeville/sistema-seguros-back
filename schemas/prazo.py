from pydantic import RootModel
from pydantic import BaseModel

from model.produto import ProdutoPrazo, ProdutoPrazoRenda


class ListagemPrazosSchema(RootModel):
    """Representa as possíveis combinações de prazos de um produto."""

    root: list[int] = [10, 20, 30]


def apresenta_prazos(prazos: list[ProdutoPrazo]) -> ListagemPrazosSchema:
    """Apresenta os prazos de pagamento e de cobertura de um produto."""
    result = [prazo.prazo for prazo in prazos]
    return ListagemPrazosSchema(root=result).model_dump()


class PrazoRendaSchema(BaseModel):
    """Representa o prazo de renda e prazo certo de renda de um produto."""

    prazo_renda: int = 10
    prazo_certo_renda: int = 10


class ListagemPrazosRendaSchema(RootModel):
    """Representa os possíveis prazos de renda e prazos certo de renda de um produto."""

    root: list[PrazoRendaSchema] = [PrazoRendaSchema()]


def apresenta_prazos_renda(
    prazos_renda: list[ProdutoPrazoRenda],
) -> ListagemPrazosRendaSchema:
    root = [
        PrazoRendaSchema(prazo_renda=prazo.prazo, prazo_certo_renda=prazo.prazoCerto)
        for prazo in prazos_renda
    ]
    return ListagemPrazosRendaSchema(root=root).model_dump()
