from numpy import allclose, atleast_1d, float64
from numpy.typing import ArrayLike, NDArray


class ArrayInfinita:
    def __init__(self, data: ArrayLike):
        self.data = atleast_1d(data)

    def __getitem__(self, index) -> NDArray[float64]:
        tamanho = len(self.data)
        index = atleast_1d(index).clip(max=tamanho - 1).astype(int)
        return self.data[index]

    def __eq__(self, other):
        return allclose(self.data, other.data)
