from datetime import date
from pydantic import BaseModel


class InputSimulacaoSchema(BaseModel):
    """Representa os dados que fazem parte do input do usuário para a simulação
    de um produto."""

    sexo: str = "M"
    data_nascimento: date = date(1990, 1, 1)
    prazo: int = 10
    produto_id: int = 1


class ResultadoSimulacaoSchema(BaseModel):
    """Representa os dados que fazem parte do output da simulação."""

    premio: float = 0.0
