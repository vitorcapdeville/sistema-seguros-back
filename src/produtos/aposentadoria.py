from datetime import date
from typing import Union

from src.array_infinita import ArrayInfinita
from src.capitalizado import Capitalizado
from src.cobertura import Cobertura
from src.pagamento import Pagamento
from src.fluxo.fluxo_pagamento import FluxoPagamento
from src.fluxo.fluxo_renda import FluxoRenda
from src.idades_prazos import IdadesPrazosAposentadoria
from src.idades_prazos import IdadesPrazosPagamento
from tabatu.typing import JurosInterface
from tabatu.premissas import Premissas
from tabatu.premissas import PremissasRenda
from tabatu import Tabua


def aposentadoria_capitalizado(
    tabua_acumulacao: Tabua,
    tabua_concessao: Tabua,
    juros: JurosInterface,
    data_assinatura: date,
    data_nascimento_segurado: date,
    prazo_cobertura: int,
    prazo_pagamento: int,
    prazo_renda: Union[int, float],
    prazo_certo_renda: int = 0,
    beneficio: float = 1.0,
    percentual_beneficio: Union[float, list[float]] = 1.0,
) -> Capitalizado:
    """Cria um contrato capitalizado de aposentadoria.

    Esse tipo de contrato assume que existe um periodo de diferimento, prazo_cobertura, e que
    caso o segurado sobreviva a este período, ele receberá uma renda por um prazo prazo_renda enquanto
    estiver vivo e opcionalmente pode possuir um prazo_certo_renda, o período em que a renda vai ser
    paga mesmo que o beneficiário faleça.

    Args:
        tabua_acumulacao (Tabua): Tábua que descreve as probabilidades de
            sobrevivência no período de acumulação, isto é, antes do segurado atingir
            a idade de aposentadoria.
        tabua_concessao (Tabua): Tábua que descreve as probabilidades de sobrevivência
            no período de concessão, isto é, após o segurado ter atingido a idade de aposentadoria.
        juros (Juros): Juros do produto
        data_assinatura (date): Data de assinatura do contrato. Usado para calcular a idade
            de ingresso (caso idade_ingresso_segurado) nao tenha sido fornecida.
        data_inicio_vigencia (date or None): Data de início de vigencia do contrato.
        data_nascimento_segurado (date): Data de nascimento do segurado.
        prazo_cobertura (int): Prazo de cobertura na mesma periodicidade que as tábuas.
        prazo_pagamento (int): Prazo de pagamento na mesma periodicidade que as tábuas.
        prazo_renda (int ou float): Prazo de renda na mesma periodicidade que as tábuas. Deve englobar
            o prazo_certo_renda.
        prazo_certo_renda (int, optional): Prazo pelo qual a renda será paga independente da sobrevivência
            do beneficiário.
        beneficio (float, optional): Valor do benefício no momento da contratação.
        percentual_beneficio (float ou list[float], optional): Percentual de benefício que será pago em cada período.
            Deve respeitar a periodicidade da tábua. Se as tábaus são anuais, então deve ser um array com o
            percentual do benefício que será pago em cada ano. Se as tábuas são mensais, então deverá
            conter o percentual de benefício que será pago em cada mês.

    Returns:
        AposentadoriaCapitalizado: Contrato capitalizado de aposentadoria.
    """
    if tabua_acumulacao.numero_vidas != 1:
        raise ValueError("Tabua de acumulação deve ter apenas uma vida.")
    if tabua_acumulacao.numero_decrementos != 1:
        raise ValueError("Tabua de acumulação deve ter apenas um decremento.")
    if tabua_concessao.numero_vidas != 1:
        raise ValueError("Tabua de concessão deve ter apenas uma vida.")
    if tabua_concessao.numero_decrementos != 1:
        raise ValueError("Tabua de concessão deve ter apenas um decremento.")
    premissas_atuariais = PremissasRenda(
        tabua=tabua_acumulacao,
        tabua_concessao=tabua_concessao,
        juros=juros,
    )
    idades_prazos = IdadesPrazosAposentadoria(
        data_assinatura=data_assinatura,
        data_nascimento_segurado=[data_nascimento_segurado]
        * len(tabua_acumulacao.tabuas),
        prazo_cobertura=prazo_cobertura,
        prazo_renda=prazo_renda,
        prazo_certo_renda=prazo_certo_renda,
        periodicidade=tabua_acumulacao.periodicidade,
    )
    calculadora_vpa = FluxoRenda(
        premissas_atuariais=premissas_atuariais,
        idades_prazos=idades_prazos,
        percentual_beneficio=ArrayInfinita(percentual_beneficio),
        postecipada=False,
    )
    cobertura = Cobertura(calculadora_vpa=calculadora_vpa)
    premissas_pagamento = Premissas(
        tabua=tabua_acumulacao,
        juros=juros,
    )
    idades_prazos_pagamento = IdadesPrazosPagamento(
        data_assinatura=data_assinatura,
        data_nascimento_segurado=[data_nascimento_segurado]
        * len(tabua_acumulacao.tabuas),
        prazo_pagamento=prazo_pagamento,
        periodicidade=tabua_acumulacao.periodicidade,
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
