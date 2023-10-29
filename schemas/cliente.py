from datetime import date
from pydantic import BaseModel


class ClienteSchema(BaseModel):
    """Define a visualização de uma matrícula."""

    cpf: int = 00000000000
    sexo: str = "M"
    data_nascimento: date = date(1990, 10, 29)
    produto_id: int = 0
    data_assinatura: date = date(2023, 10, 29)
    prazo: int = 0


def apresenta_cliente(cliente: ClienteSchema):
    """Retorna uma representação de um cliente."""
    return {
        "cpf": cliente.cpf,
        "sexo": cliente.sexo,
        "data_nascimento": cliente.data_nascimento,
        "produto_id": cliente.produto_id,
        "data_assinatura": cliente.data_assinatura,
        "prazo": cliente.prazo,
    }
