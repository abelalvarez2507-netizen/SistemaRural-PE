import os
import tempfile

from servicios.fabrica import FabricaEntidades
from servicios.gestor_bd import GestorBaseDatos


def test_singleton_misma_instancia():
    gestor_1 = GestorBaseDatos()
    gestor_2 = GestorBaseDatos()

    assert gestor_1 is gestor_2


def test_singleton_misma_conexion_para_la_misma_bd():
    gestor = GestorBaseDatos()

    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "prueba.db")

        conexion_1 = gestor.conectar(ruta)
        conexion_2 = gestor.conectar(ruta)

        assert conexion_1 is conexion_2

        gestor.cerrar(ruta)


def test_factory_crea_paciente():
    paciente = FabricaEntidades.crear_paciente(
        "P001",
        "12345678",
        "Juan Perez",
        35
    )

    assert paciente.codigo == "P001"
    assert paciente.nombre == "Juan Perez"
    assert paciente.edad == 35
