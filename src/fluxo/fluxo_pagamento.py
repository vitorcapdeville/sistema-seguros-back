from dataclasses import dataclass, field
from typing import Iterable, Union

from numpy import ndarray, vectorize
from tabatu.periodicidade import Periodicidade
from tabatu.premissas import Premissas

from src.array_infinita import ArrayInfinita
from src.calculadora_vpa import CalculadoraVPAPagamento
from src.fluxo.fluxo_interface import FluxoData, valida_tabua_prazo_idade
from src.fluxo.fluxo_renda import fluxo_renda
from src.idades_prazos import IdadesPrazosPagamento


@dataclass(frozen=True)
class FluxoPagamento(CalculadoraVPAPagamento):
    """Calculo do VPA dos pagamentos futuros via fluxo.

    Args:
        idades_prazos (IdadesPrazosPagamento): Idades e prazos de pagamento.
        premissas_atuariais (Premissas): Premissas atuariais.
    """

    idades_prazos: IdadesPrazosPagamento
    premissas_atuariais: Premissas
    periodicidade_pagamento: Periodicidade = field(init=False)

    def __post_init__(self):
        object.__setattr__(
            self,
            "periodicidade_pagamento",
            self.premissas_atuariais.tabua.periodicidade,
        )
        if self.premissas_atuariais.periodicidade != self.idades_prazos.periodicidade:
            raise ValueError(
                "periodicidade das premissas_atuariais e idades_prazos devem ser iguais"
            )

        valida_tabua_prazo_idade(
            self.premissas_atuariais.tabua,
            self.idades_prazos.prazo_pagamento,
            self.idades_prazos.idade_ingresso_segurado,
        )

    def gerar_fluxo(self, tempo_atual: int) -> FluxoData:
        """Gera o fluxo futuro de probabilidades (tempo a tempo).

        Args:
            tempo_atual (int): Tempo atual, na periodicidade das premissas atuariais.

        Returns:
            FluxoData: Fluxo futuro de probabilidades.
        """
        idade_ingresso_segurado = self.idades_prazos.idade_ingresso_segurado
        return fluxo_renda(
            tempo_atual=tempo_atual,
            idade_ingresso=idade_ingresso_segurado,
            prazo_cobertura=0,
            prazo_renda=self.idades_prazos.prazo_pagamento,
            prazo_certo_renda=0,
            tabua=self.premissas_atuariais.tabua,
            tabua_concessao=self.premissas_atuariais.tabua,
            juros=self.premissas_atuariais.juros,
            percentual_beneficio=ArrayInfinita([1.0]),
            postecipada=False,
        )

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
