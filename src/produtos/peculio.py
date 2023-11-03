from datetime import date
from typing import Optional, Union

from tabatu.premissas import Premissas
from tabatu.typing import JurosInterface, TabuaInterface

from src.array_infinita import ArrayInfinita
from src.capitalizado import Capitalizado
from src.cobertura import Cobertura
from src.fluxo.fluxo_pagamento import FluxoPagamento
from src.fluxo.fluxo_peculio import FluxoPeculio
from src.idades_prazos import IdadesPrazosPagamento, IdadesPrazosPeculio
from src.pagamento import Pagamento


def peculio_capitalizado_fluxo(
    tabua_beneficio: TabuaInterface,
    tabua_pagamento: TabuaInterface,
    juros: JurosInterface,
    data_assinatura: date,
    data_nascimento_segurado: date,
    prazo_cobertura: Union[int, float],
    prazo_pagamento: Union[int, float],
    beneficio: float = 1.0,
    percentual_beneficio: Union[float, list[float]] = 1.0,
    imediato: bool = False,
) -> Capitalizado:
    """Cria um contrato capitalizado de pecúlio via fluxo.

    Esse tipo de contrato assume que o benefício será pago de uma única vez no final do período
    de ocorrência do sinistro. É permitido realizar saldamento, prolongamento e alteração de benefício durante
    o prazo de pagamento.
    Tanto o vpa dos benefícios quanto o vpa dos pagamentos é calculado via fluxo.

    Args:
        tabua_beneficio (TabuaInterface): Tabua que descreve o pagamento de benefícios.
        tabua_pagamento (TabuaInterface): Tabua que descreve o pagamento de contribuições.
        juros (JurosInterface): Juros do produto.
        data_assinatura (date): Data de assinatura do contrato. Usado para calcular a idade
            de ingresso (caso idade_ingresso_segurado) nao tenha sido fornecida.
        data_inicio_vigencia (date or None): Data de início de vigencia do contrato.
        data_nascimento_segurado (date): Data de nascimento do segurado.
        prazo_cobertura (int): Prazo de cobertura na mesma periodicidade que as tábuas.
        prazo_pagamento (int): Prazo de pagamento na mesma periodicidade que as tábuas.
        beneficio (float, optional): Valor do benefício no momento da contratação.
        percentual_beneficio (float ou list[float], optional): Percentual de benefício que será pago em cada período.
            Deve respeitar a periodicidade da tábua. Se as tábaus são anuais, então deve ser um array com o
            percentual do benefício que será pago em cada ano. Se as tábuas são mensais, então deverá
            conter o percentual de benefício que será pago em cada mês.
        imediato (bool, optional): Se o benefício será pago imediatamente após o sinistro (True) ou se é pago no final
            do período em que houve o sinistro (False).

    Returns:
        Capitalizado: Contrato capitalizado de pecúlio.
    """
    idades_prazos = IdadesPrazosPeculio(
        data_assinatura=data_assinatura,
        data_nascimento_segurado=[data_nascimento_segurado] * len(tabua_beneficio.tabuas),  # type: ignore
        prazo_cobertura=prazo_cobertura,
        periodicidade=tabua_beneficio.periodicidade,
    )
    premissas = Premissas(tabua=tabua_beneficio, juros=juros)
    calculadora_vpa = FluxoPeculio(
        premissas_atuariais=premissas,
        idades_prazos=idades_prazos,
        percentual_beneficio=ArrayInfinita(percentual_beneficio),
        imediato=imediato,
    )
    cobertura = Cobertura(calculadora_vpa=calculadora_vpa)
    premissas_pagamento = Premissas(tabua=tabua_pagamento, juros=juros)
    idades_prazos_pagamento = IdadesPrazosPagamento(
        data_assinatura=data_assinatura,
        data_nascimento_segurado=[data_nascimento_segurado] * len(tabua_pagamento.tabuas),  # type: ignore
        prazo_pagamento=prazo_pagamento,
        periodicidade=tabua_beneficio.periodicidade,
    )
    calculadora_vpa = FluxoPagamento(
        premissas_atuariais=premissas_pagamento, idades_prazos=idades_prazos_pagamento
    )
    pagamento = Pagamento(calculadora_vpa=calculadora_vpa)
    contrato = Capitalizado(
        cobertura=cobertura,
        pagamento=pagamento,
        beneficio=beneficio,
    )
    return contrato
