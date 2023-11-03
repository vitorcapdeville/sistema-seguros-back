from dataclasses import dataclass
from datetime import date
from typing import Union

from tabatu.periodicidade import Periodicidade
from tabatu.premissas import Premissas

from src.calculadora_vpa import CalculadoraVPAPagamento
from src.idades_prazos import IdadesPrazosPagamento


@dataclass(frozen=True)
class Pagamento:
    """Classe abstrata que representa o pagamento associado a uma cobertura de seguro.

    Realiza uma adptação entre as calculadoras de VPA e os contratos (usualmente capitalizados).
    Fornece também alguns métodos para auxiliar nas alterações permitadas pelos contratos.

    Args:
        calculadora_vpa (CalculadoraVPAPagamento): Calculadora do VPA da cobertura. Usualmente uma das classes de
            fluxo ou comutação de pagamento.
    """

    calculadora_vpa: CalculadoraVPAPagamento

    @property
    def idades_prazos(self) -> IdadesPrazosPagamento:
        return self.calculadora_vpa.idades_prazos

    @property
    def premissas_atuariais(self) -> Premissas:
        return self.calculadora_vpa.premissas_atuariais

    @property
    def data_assinatura(self) -> date:
        return self.idades_prazos.data_assinatura

    @property
    def prazo_pagamento(self) -> Union[int, float]:
        return self.idades_prazos.prazo_pagamento

    @property
    def periodicidade(self) -> Periodicidade:
        return self.premissas_atuariais.periodicidade

    @property
    def periodicidade_pagamento(self) -> Periodicidade:
        return self.calculadora_vpa.periodicidade_pagamento

    @property
    def parcelamento(self) -> int:
        return int(
            self.periodicidade_pagamento.quantidade_periodos_1_periodicidade(
                self.periodicidade
            )
        )

    def vpa(self, tempo_decorrido: int) -> float:
        """Cálculo do valor presente atuarial das obrigações futuras.

        Args:
            tempo_decorrido (int): Tempo decorrido desde o início da cobertura, na periodicdade da cobertura.

        Returns:
            float: Valor presente das obrigações futuras em tempo_decorrido.
        """
        if tempo_decorrido < 0:
            raise ValueError("O tempo_decorrido deve ser positivo")
        return self.calculadora_vpa.calcular_vpa(tempo_atual=tempo_decorrido)
