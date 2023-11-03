from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

from numpy import float64, isinf, int64
from numpy.typing import NDArray
from tabatu.premissas import Premissas
from tabatu.typing import TabuaInterface

from src.array_infinita import ArrayInfinita
from src.calculadora_vpa import CalculadoraVPA
from src.idades_prazos import IdadesPrazos


@dataclass
class FluxoData:
    tempos: NDArray[int64]
    probabilidade: NDArray[float64]
    valor: NDArray[float64]
    desconto: NDArray[float64]

    def vpa(self) -> float:
        return (self.probabilidade * self.valor * self.desconto).sum()


def valida_tabua_prazo_idade(
    tabua: TabuaInterface, prazo: Union[int, float], idade_ingresso: list[int]
) -> None:
    if len(idade_ingresso) == 1:
        idade_ingresso = idade_ingresso * len(tabua.tabuas)  # type: ignore
    tempo_futuro_maximo = tabua.tempo_futuro_maximo(idade_ingresso)
    if not isinf(prazo) and prazo != 0 and prazo >= tempo_futuro_maximo:
        raise ValueError("prazo deve ser infinito ou menor que o limite da tabua")


@dataclass(frozen=True)
class FluxoInterface(CalculadoraVPA, ABC):
    """Cálculo do VPA através de fluxos de probabilidade."""

    premissas_atuariais: Premissas
    idades_prazos: IdadesPrazos
    percentual_beneficio: ArrayInfinita

    def __post_init__(self):
        if self.premissas_atuariais.periodicidade != self.idades_prazos.periodicidade:
            raise ValueError(
                "periodicidade das premissas_atuariais e idades_prazos devem ser iguais"
            )

        valida_tabua_prazo_idade(
            self.premissas_atuariais.tabua,
            self.idades_prazos.prazo_cobertura,
            self.idades_prazos.idade_ingresso_segurado,
        )

    @abstractmethod
    def gerar_fluxo(self, tempo_atual: int) -> FluxoData:
        """Gera o fluxo futuro de probabilidades (tempo a tempo).

        Args:
            tempo_atual (int): Tempo atual, na periodicidade das premissas atuariais.

        Returns:
            FluxoData: Fluxo futuro de probabilidades.
        """
        raise NotImplementedError

    def calcular_vpa(self, tempo_atual: int) -> float:
        """Cálculo do valor presente atuarial das obrigações futuras via fluxo.

        Utiliza os fluxos futuros para cada um dos tempos fornecidos, e calcula o valor presente atuarial,
        em cada tempo fornecido.

        Args:
            tempo_atual (int or Iterable[int]): Tempo atual, na periodicidade das premissas atuariais.

        Returns:
            ndarray[float]: Valor presente atuarial das obrigações futuras.
        """
        return self.gerar_fluxo(tempo_atual).vpa()
