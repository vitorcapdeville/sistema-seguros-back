from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class SimulacaoSchema(BaseModel):
    """Representa os dados para uma simulação genérica."""

    sexo: str = "M"
    data_nascimento: date = date(1990, 1, 1)
    prazo: int = 10
    produto_id: int = 1
    prazo_renda: Optional[int] = None
    prazo_certo_renda: Optional[int] = None


class SimulacaoPeculioSchema(BaseModel):
    """Representa os dados que fazem parte do input do usuário para a simulação
    de um produto do tipo peculio."""

    sexo: str = "M"
    data_nascimento: date = date(1990, 1, 1)
    prazo: int = 10
    produto_id: int = 1


class SimulacaoAposentadoriaSchema(BaseModel):
    """Representa os dados que fazem parte do input do usuário para a simulação
    de um produto do tipo aposentadoria."""

    sexo: str = "M"
    data_nascimento: date = date(1990, 1, 1)
    prazo: int = 10
    prazo_renda: int = 10
    prazo_certo_renda: int = 0
    produto_id: int = 1


class ResultadoSimulacaoSchema(BaseModel):
    """Representa os dados que fazem parte do output da simulação."""

    premio: float = 0.0
