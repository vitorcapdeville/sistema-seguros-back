from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from src.idades_prazos import IdadesPrazos
from src.idades_prazos import IdadesPrazosPagamento
from tabatu.premissas import Premissas
from tabatu.periodicidade import Periodicidade


@dataclass(frozen=True)
class CalculadoraVPA(ABC):
    idades_prazos: IdadesPrazos
    premissas_atuariais: Premissas

    @abstractmethod
    def calcular_vpa(self, tempo_atual: int) -> float:
        raise NotImplementedError


@dataclass(frozen=True)
class CalculadoraVPAPagamento(ABC):
    idades_prazos: IdadesPrazosPagamento
    premissas_atuariais: Premissas
    periodicidade_pagamento: Periodicidade

    @abstractmethod
    def calcular_vpa(self, tempo_atual: int) -> float:
        raise NotImplementedError
