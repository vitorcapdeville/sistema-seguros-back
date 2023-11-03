from dataclasses import dataclass
from datetime import date
from typing import Union

from tabatu.periodicidade import Periodicidade

from src.calculadora_vpa import CalculadoraVPA


@dataclass(frozen=True)
class Cobertura:
    """Cobertura de seguro.

    Fornece uma adptação entre a classe que realiza o cálculo do VPA e os produtos (usualmente capitalizados).
    Além de calcular o VPA, também fornece métodos para alterar a cobertura, conforme as alterações permitidas
    nos contratos capitalizados.

    Args:
        calculadora_vpa (CalculadoraVPA): Calculadora do VPA da cobertura. Usualmente uma das classes de fluxo ou
            comutação.
    """

    calculadora_vpa: CalculadoraVPA

    @property
    def idades_prazos(self):
        return self.calculadora_vpa.idades_prazos

    @property
    def premissas_atuariais(self):
        return self.calculadora_vpa.premissas_atuariais

    @property
    def data_assinatura(self) -> date:
        return self.idades_prazos.data_assinatura

    @property
    def prazo_cobertura(self) -> Union[int, float]:
        return self.idades_prazos.prazo_cobertura

    @property
    def prazo_cobertura_efetivo(self) -> int:
        prazo = self.idades_prazos.prazo_cobertura
        idade = self.idades_prazos.idade_ingresso_segurado
        tabua = self.premissas_atuariais.tabua
        return int(min(tabua.tempo_futuro_maximo(idade), prazo))

    @property
    def periodicidade(self) -> Periodicidade:
        return self.premissas_atuariais.periodicidade

    def vpa(self, tempo_decorrido: int) -> float:
        """Cálculo do valor presente atuarial das obrigações futuras.

        Args:
            tempo_decorrido (int): Tempo decorrido desde o início da cobertura,
                na periodicdade da cobertura.

        Returns:
            float: Valor presente das obrigações futuras em tempo_decorrido.
        """
        if tempo_decorrido < 0:
            raise ValueError("O tempo_decorrido deve ser positivo")
        return self.calculadora_vpa.calcular_vpa(tempo_decorrido)
