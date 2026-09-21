class Configuracion:
    """Intento inicial de Singleton: todavía permite crear varias instancias."""
    instancia = None

    def __init__(self):
        self.nombre_sistema = "SistemaRural-PE"

    @classmethod
    def obtener_instancia(cls):
        if cls.instancia is None:
            cls.instancia = Configuracion()
        # Error de incorporación: crear directamente Configuracion() sigue siendo posible.
        return cls.instancia
