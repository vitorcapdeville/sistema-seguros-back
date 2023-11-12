from datetime import date
from typing import Optional
from pydantic import BaseModel


class ClienteSchema(BaseModel):
    """Define a visualização de uma matrícula."""

    cpf: int = 00000000000
    nome: str = "Jose da Silva"
    email: str = "jsilva@email.com"
    sexo: str = "M"
    data_nascimento: date = date(1990, 10, 29)
    produto_id: int = 1
    data_assinatura: date = date(2023, 10, 29)
    prazo: int = 10
    beneficio: int = 10000
    prazo_renda: Optional[int] = None
    prazo_certo_renda: Optional[int] = None
