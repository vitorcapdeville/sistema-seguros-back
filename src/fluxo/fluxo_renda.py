from dataclasses import dataclass
from typing import Union

from numpy import arange, array
from tabatu.premissas import PremissasRenda
from tabatu.typing import JurosInterface, TabuaInterface

from src.array_infinita import ArrayInfinita
from src.fluxo.fluxo_interface import (
    FluxoData,
    FluxoInterface,
    valida_tabua_prazo_idade,
)
from src.idades_prazos import IdadesPrazosAposentadoria


@dataclass(frozen=True)
class FluxoRenda(FluxoInterface):
    """Calculo do VPA dos benefícios futuros de uma cobertura de renda via fluxo.

    Args:
        idades_prazos (IdadesPrazosAposentadoria): Idades e prazos de pagamento.
        premissas_atuariais (PremissasRenda): Premissas atuariais.
        percentual_beneficio (ArrayInfinita): Percentual do benefício na mesma periodicidade das premissas.
        postecipada (bool): Indica se a renda é postecipada.
    """

    premissas_atuariais: PremissasRenda
    idades_prazos: IdadesPrazosAposentadoria
    percentual_beneficio: ArrayInfinita
    postecipada: bool

    def __post_init__(self):
        valida_tabua_prazo_idade(
            self.premissas_atuariais.tabua_concessao,
            self.idades_prazos.prazo_renda,
            self.idades_prazos.idade_ingresso_beneficiario,
        )

    def gerar_fluxo(self, tempo_atual: int) -> FluxoData:
        """Gera o fluxo futuro de probabilidades (tempo a tempo).

        Args:
            tempo_atual (int): Tempo atual, na periodicidade das premissas atuariais.

        Returns:
            FluxoData: Fluxo futuro de probabilidades.
        """
        return fluxo_renda(
            tempo_atual=tempo_atual,
            idade_ingresso=self.idades_prazos.idade_ingresso_segurado,
            prazo_cobertura=self.idades_prazos.prazo_cobertura,
            prazo_renda=self.idades_prazos.prazo_renda,
            prazo_certo_renda=self.idades_prazos.prazo_certo_renda,
            tabua=self.premissas_atuariais.tabua,
            tabua_concessao=self.premissas_atuariais.tabua_concessao,
            juros=self.premissas_atuariais.juros,
            percentual_beneficio=self.percentual_beneficio,
            postecipada=self.postecipada,
        )


def fluxo_renda(
    tempo_atual: int,
    idade_ingresso: list[int],
    prazo_cobertura: int,
    prazo_renda: Union[int, float],
    prazo_certo_renda: int,
    tabua: TabuaInterface,
    tabua_concessao: TabuaInterface,
    juros: JurosInterface,
    percentual_beneficio: ArrayInfinita,
    postecipada: bool,
) -> FluxoData:
    if prazo_cobertura + prazo_renda <= tempo_atual:
        return FluxoData(
            tempos=array([0.0]),
            probabilidade=array([0.0]),
            valor=array([0.0]),
            desconto=array([0.0]),
        )

    tempo_ate_renda = max(prazo_cobertura - tempo_atual, 0)
    tempo_ja_decorrido_da_renda = max(tempo_atual - prazo_cobertura, 0)
    prazo_renda_efetivo = min(
        tabua_concessao.tempo_futuro_maximo(idade_ingresso) - prazo_cobertura,
        prazo_renda,
    )
    prazo_maximo_pagamento_renda = prazo_renda_efetivo + postecipada
    tempo_restante_renda = max(
        prazo_maximo_pagamento_renda - tempo_ja_decorrido_da_renda, 1
    )
    tempo_pagamento_renda = arange(start=postecipada, stop=tempo_restante_renda).astype(
        int
    )
    tempos_futuros = tempo_pagamento_renda + tempo_ate_renda
    idade_atual = [idade + tempo_atual for idade in idade_ingresso]

    probabilidade_chegar_vivo_na_renda = tabua.tpx(x=idade_atual, t=[tempo_ate_renda])
    probabilidade_sobreviver_renda = tabua_concessao.tpx(
        x=[idade + tempo_ate_renda for idade in idade_atual], t=tempo_pagamento_renda
    )
    eh_prazo_certo = (
        tempo_pagamento_renda + tempo_ja_decorrido_da_renda
        < prazo_certo_renda + postecipada
    )
    probabilidade_sobreviver_renda[eh_prazo_certo] = 1
    probabilidade = probabilidade_chegar_vivo_na_renda * probabilidade_sobreviver_renda
    valor = percentual_beneficio[
        (tempo_pagamento_renda - int(postecipada) + tempo_ja_decorrido_da_renda).astype(
            int
        )
    ]
    desconto = juros.taxa_desconto(tempos_futuros)
    return FluxoData(
        tempos=tempos_futuros,
        probabilidade=probabilidade,
        valor=valor,
        desconto=desconto,
    )
