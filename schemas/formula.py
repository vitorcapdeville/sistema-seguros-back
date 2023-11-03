from pydantic import BaseModel


class FormulaSchema(BaseModel):
    """Representa o nome da fórmula associada a um produto."""

    formula: str = "peculio"
