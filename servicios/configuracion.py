class Configuracion:
    """Singleton: garantiza una única instancia de configuración."""
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.nombre_sistema = "SistemaRural-PE"
        return cls._instancia

    @classmethod
    def obtener_instancia(cls):
        return cls()
