from dataclasses import dataclass

from tabatu.periodicidade import periodicidade2meses

from src.cobertura import Cobertura
from src.pagamento import Pagamento


@dataclass(frozen=True)
class Capitalizado:
    """Contrato estruturado no regime de capitalização.

    O prêmio se mantém constante durante o prazo de pagamento e usualmente fornece a possibilidade de
    resgate da reserva de benefícios a conceder.

    Args:
        cobertura (Cobertura): Cobertura do contrato, define o VPA das obrigações da seguradora.
        pagamento (Pagamento): Pagamento do contrato, define o VPA das obrigações do segurado.
        beneficio (float): Valor do benefício inicial.
        data_inicio_vigencia (date or None): Data de início de vigência do contrato. Caso não seja fornecido,
            será considerada a data de assinatura da cobertura.
    """

    cobertura: Cobertura
    pagamento: Pagamento
    beneficio: float
    carregamento: float = 0.0

    def __post_init__(self):
        if self.cobertura.periodicidade != self.pagamento.periodicidade:
            raise ValueError(
                "A periodicidade da cobertura deve ser igual a periodicidade do pagamento."
            )
        if self.cobertura.prazo_cobertura < self.pagamento.prazo_pagamento:
            raise ValueError(
                "O prazo de cobertura deve ser maior ou igual ao prazo de pagamento."
            )
        if self.beneficio <= 0:
            raise ValueError("O benefício inicial deve ser > 0.")
        if self.cobertura.data_assinatura != self.pagamento.data_assinatura:
            raise ValueError(
                "A data de assinatura da cobertura deve ser igual a do pagamento."
            )

    @property
    def parcelamento(self) -> int:
        """Parcelamento do pagamento."""
        return self.pagamento.parcelamento

    @property
    def taxa_pura(self) -> float:
        """Taxa pura do contrato."""
        vpa_cobertura = self.cobertura.vpa(0)
        vpa_pagamento = self.pagamento.vpa(0)
        parcelamento = self.parcelamento
        if vpa_pagamento == 0:
            return 0.0
        return vpa_cobertura / (vpa_pagamento * parcelamento)

    def premio_puro(self, tempo_decorrido_meses: int) -> float:
        """Valor do prêmio puro do contrato.

        Args:
            tempo_decorrido_meses (int): Tempo decorrido em meses desde a data de
                assinatura.

        Returns:
            float: valor do prêmio puro para os tempos/datas de cálculo.
        """
        if tempo_decorrido_meses < 0:
            raise ValueError("tempo_decorrido deve ser >= 0.")

        if not self.esta_pagando(tempo_decorrido_meses):
            return 0.0

        return self.taxa_pura * self.beneficio

    def premio_comercial(self, tempo_decorrido_meses: int) -> float:
        return self.premio_puro(tempo_decorrido_meses) / (1 - self.carregamento)

    def esta_pagando(self, tempo_decorrido_meses: int) -> bool:
        prazo_meses = periodicidade2meses(
            self.pagamento.prazo_pagamento, self.pagamento.periodicidade
        ).item()
        return tempo_decorrido_meses < prazo_meses

    def esta_coberto(self, tempo_decorrido_meses: int) -> bool:
        prazo_meses = periodicidade2meses(
            self.cobertura.prazo_cobertura, self.cobertura.periodicidade
        ).item()
        return tempo_decorrido_meses <= prazo_meses
