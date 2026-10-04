"""Medicamento indicado por un profesional durante una atención."""

from servicios.validaciones import texto_requerido


class MedicamentoRecetado:
    def __init__(self, medicamento, dias, cada_cuanto):
        self._medicamento = texto_requerido(medicamento, "El medicamento", 120)
        try:
            dias = int(str(dias).strip())
        except (TypeError, ValueError):
            raise ValueError("Los días del tratamiento deben ser un número entero.") from None
        if dias <= 0:
            raise ValueError("Los días del tratamiento deben ser mayores que cero.")
        self._dias = dias
        self._cada_cuanto = texto_requerido(cada_cuanto, "La frecuencia", 100)

    @property
    def medicamento(self):
        return self._medicamento

    @property
    def dias(self):
        return self._dias

    @property
    def cada_cuanto(self):
        return self._cada_cuanto

    def mostrar_informacion(self):
        return f"{self.medicamento} · {self.dias} días · {self.cada_cuanto}"
