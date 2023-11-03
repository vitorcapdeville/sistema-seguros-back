from dataclasses import dataclass
from typing import Union

from numpy import arange, array
from tabatu.premissas import Premissas
from tabatu.typing import JurosInterface, TabuaInterface

from src.array_infinita import ArrayInfinita
from src.fluxo.fluxo_interface import FluxoData, FluxoInterface
from src.idades_prazos import IdadesPrazos


def fluxo_peculio(
    tempo_atual: int,
    tabua: TabuaInterface,
    juros: JurosInterface,
    idade_ingresso_segurado: list[int],
    prazo_cobertura: Union[int, float],
    percentual_beneficio: ArrayInfinita,
    imediato: bool,
) -> FluxoData:
    if prazo_cobertura <= tempo_atual:
        return FluxoData(
            tempos=array([0.0]),
            probabilidade=array([0.0]),
            valor=array([0.0]),
            desconto=array([0.0]),
        )
    idade_atual = [idade + tempo_atual for idade in idade_ingresso_segurado]
    prazo_cobertura_efetivo = min(
        tabua.tempo_futuro_maximo(idade_ingresso_segurado), prazo_cobertura
    )
    limite = max(prazo_cobertura_efetivo - tempo_atual, 1)
    tempos = arange(start=0, stop=limite).astype(int)
    probabilidade = tabua.t_qx(x=idade_atual, t=tempos)
    valor = percentual_beneficio[(tempos + tempo_atual).astype(int)]
    desconto = juros.taxa_desconto(tempos + (0.5 if imediato else 1))
    return FluxoData(tempos + 1, probabilidade, valor, desconto)


@dataclass(frozen=True)
class FluxoPeculio(FluxoInterface):
    """Cálculo do VPA dos benefícios futuros de uma cobertura de pecúlio via fluxo.

    Args:
        idades_prazos (IdadesPrazos): Idades e prazos de pagamento.
        premissas_atuariais (Premissas): Premissas atuariais.
        percentual_beneficio (ArrayInfinita): Percentual do benefício na mesma periodicidade das premissas.
        imediato (bool): Indica se o benefício é imediato.
    """

    premissas_atuariais: Premissas
    idades_prazos: IdadesPrazos
    percentual_beneficio: ArrayInfinita
    imediato: bool

    def gerar_fluxo(self, tempo_atual: int) -> FluxoData:
        """Gera o fluxo futuro de probabilidades (tempo a tempo).

        Args:
            tempo_atual (int): Tempo atual, na periodicidade das premissas atuariais.

        Returns:
            FluxoData: Fluxo futuro de probabilidades.
        """
        return fluxo_peculio(
            tempo_atual=tempo_atual,
            tabua=self.premissas_atuariais.tabua,
            juros=self.premissas_atuariais.juros,
            idade_ingresso_segurado=self.idades_prazos.idade_ingresso_segurado,
            prazo_cobertura=self.idades_prazos.prazo_cobertura,
            percentual_beneficio=self.percentual_beneficio,
            imediato=self.imediato,
        )
