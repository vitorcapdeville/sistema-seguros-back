from pydantic import BaseModel

from model.produto import ProdutoPrazo


class Prazo(BaseModel):
    """Representa o prazo de pagamento e o prazo de cobertura para um determinado produto."""

    produto_id: int = 1
    prazo: int = 10


class ListagemPrazosSchema(BaseModel):
    """Representa as possíveis combinações de prazos de um produto."""

    prazos: list[Prazo] = [Prazo()]


def apresenta_prazos(prazos: list[ProdutoPrazo]) -> ListagemPrazosSchema:
    """Apresenta os prazos de pagamento e de cobertura de um produto."""
    result = []
    for prazo in prazos:
        result.append(
            {
                "produto_id": prazo.produtoId,
                "prazo": prazo.prazo,
            }
        )
    return ListagemPrazosSchema(prazos=result).model_dump()
