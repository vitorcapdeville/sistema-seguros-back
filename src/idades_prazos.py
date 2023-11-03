from dataclasses import dataclass, field
from datetime import date
from typing import Union

from dateutil.relativedelta import relativedelta
from numpy import isinf
from tabatu.periodicidade import Periodicidade


def calcula_idade(
    data_origem: date,
    data_calculo: date,
    periodicidade: Periodicidade = Periodicidade.MENSAL,
) -> int:
    """Calcula a idade em qualquer periodicidade igual ou superior a mensal a partir de duas datas.
    A quantidade de dias em cada mês, bimestre, trimestre etc não é constante, e portanto, conversões
    entre mes e dias não seriam precisas."""
    if periodicidade < Periodicidade.MENSAL:
        raise ValueError("Periodicidade deve ser mensal ou maior.")
    qntd_periodos_1_ano = periodicidade.quantidade_periodos_1_ano()
    tempo_decorrido = relativedelta(data_calculo, data_origem)
    return int(
        tempo_decorrido.years * qntd_periodos_1_ano
        + tempo_decorrido.months // (12 / qntd_periodos_1_ano)
    )


@dataclass(frozen=True)
class IdadesPrazos:
    """Idades e prazos de uma cobertura.

    Args:
        data_assinatura (ddate): Data de assinatura da cobertura.
        data_nascimento_segurado (list[date]): Data de nascimento do segurado.
        prazo_cobertura (Union[int, float]): Prazo da cobertura.
        periodicidade (Periodicidade): Periodicidade da idade e do prazo.
    """

    data_assinatura: date
    data_nascimento_segurado: list[date]
    prazo_cobertura: Union[int, float]
    periodicidade: Periodicidade

    def __post_init__(self):
        if not isinf(self.prazo_cobertura):
            object.__setattr__(self, "prazo_cobertura", int(self.prazo_cobertura))

        if any([idade < 0 for idade in self.idade_ingresso_segurado]):
            raise ValueError("idade_ingresso_segurado deve ser positiva")

        if self.prazo_cobertura < 0:
            raise ValueError("prazo_cobertura não pode ser negativo.")

    @property
    def idade_ingresso_segurado(self) -> list[int]:
        return [
            calcula_idade(data_nascimento, self.data_assinatura, self.periodicidade)
            for data_nascimento in self.data_nascimento_segurado
        ]


@dataclass(frozen=True)
class IdadesPrazosPeculio(IdadesPrazos):
    def __post_init__(self):
        super().__post_init__()
        if self.prazo_cobertura <= 0:
            raise ValueError("prazo_cobertura deve ser maior que zero")


@dataclass(frozen=True)
class IdadesPrazosRenda(IdadesPrazos):
    """Idades e prazos de uma cobertura de renda.

    Permite a conversão entre diferentes periodicidades.

    Args:
        data_assinatura (date): Data de assinatura da cobertura.
        data_nascimento_segurado (list[date]): Data de nascimento do segurado.
        data_nascimento_beneficiario (list[date]): Data de nascimento dos beneficiários.
        prazo_cobertura (Union[int, float]): Prazo da cobertura, na periodicidade da tábua.
        prazo_renda (Union[int, float]): Prazo da renda, na periodicidade da tábua.
        prazo_certo_renda (int): Prazo certo da renda, na periodicidade da tábua.
    """

    data_nascimento_beneficiario: list[date]
    prazo_renda: Union[int, float]
    prazo_certo_renda: int

    def __post_init__(self):
        super().__post_init__()

        if not isinf(self.prazo_renda):
            object.__setattr__(self, "prazo_renda", int(self.prazo_renda))
        object.__setattr__(self, "prazo_certo_renda", int(self.prazo_certo_renda))

        if any([idade < 0 for idade in self.idade_ingresso_beneficiario]):
            raise ValueError("idade_ingresso_beneficiario deve ser positiva")

        if self.prazo_renda <= 0:
            raise ValueError(f"Prazo da renda deve ser maior que zero.")

        if self.prazo_certo_renda < 0:
            raise ValueError("Prazo de renda certa não pode ser negativo.")

        if self.prazo_renda < self.prazo_certo_renda:
            raise ValueError("prazo_renda deve englobar o prazo_certo_renda.")

    @property
    def idade_ingresso_beneficiario(self) -> list[int]:
        return [
            calcula_idade(data_nascimento, self.data_assinatura, self.periodicidade)
            for data_nascimento in self.data_nascimento_beneficiario
        ]


@dataclass(frozen=True)
class IdadesPrazosAposentadoria(IdadesPrazosRenda):
    prazo_cobertura: int
    data_nascimento_beneficiario: list[date] = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        if isinf(self.prazo_cobertura):
            raise ValueError(f"O prazo de cobertura não pode ser vitalício.")

    @property
    def idade_ingresso_beneficiario(self) -> list[int]:
        return self.idade_ingresso_segurado


@dataclass(frozen=True)
class IdadesPrazosPagamento:
    """Idades e prazos associados a um pagamento.

    Permite a conversão entre diferentes periodicidades.

    Args:
        data_assinatura (ddate): Data de assinatura da cobertura.
        data_nascimento_segurado (ndarray[date]): Data de nascimento do segurado.
        prazo_pagamento (Union[int, float]): Prazo de pagammento.
        periodicidade (Periodicidade): Periodicidade da idade e do prazo.
    """

    data_assinatura: date
    data_nascimento_segurado: list[date]
    prazo_pagamento: Union[int, float]
    periodicidade: Periodicidade

    def __post_init__(self):
        if not isinf(self.prazo_pagamento):
            object.__setattr__(self, "prazo_pagamento", int(self.prazo_pagamento))

        if any([idade < 0 for idade in self.idade_ingresso_segurado]):
            raise ValueError("idade_ingresso_segurado deve ser positiva")

        if self.prazo_pagamento < 0:
            raise ValueError("O prazo de pagamento deve ser positivo.")

    @property
    def idade_ingresso_segurado(self) -> list[int]:
        return [
            calcula_idade(data_nascimento, self.data_assinatura, self.periodicidade)
            for data_nascimento in self.data_nascimento_segurado
        ]
