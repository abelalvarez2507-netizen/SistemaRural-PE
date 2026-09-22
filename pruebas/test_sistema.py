import os
import tempfile

import pytest

from modelos.cita import Cita
from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from servicios.fabrica import FabricaEntidades
from servicios.repositorio import RepositorioSalud
from servicios.seguridad import SeguridadDatos
from servicios.sistema_salud import SistemaSalud


def crear_sistema_temporal(carpeta):
    ruta = os.path.join(carpeta, "salud_prueba.db")
    repositorio = RepositorioSalud(ruta)
    sistema = SistemaSalud(repositorio)
    return sistema, repositorio


def crear_paciente(codigo="P001", dni="12345678"):
    return Paciente(codigo, dni, "Paciente Demo", 30)


def crear_profesional(codigo="PS001", dni="87654321"):
    return PersonalSalud(
        codigo,
        dni,
        "Profesional Demo",
        40,
        "Medicina General"
    )


def test_registro_y_busqueda_de_paciente_por_codigo():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()

        sistema.registrar_paciente(paciente)
        resultados = sistema.buscar_paciente_por_codigo("p001")

        assert len(resultados) == 1
        assert resultados[0].codigo == "P001"

        repositorio.cerrar()


def test_busqueda_de_paciente_por_dni_protegido():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()

        sistema.registrar_paciente(paciente)
        resultados = sistema.buscar_paciente_por_dni("12345678")

        assert len(resultados) == 1
        assert resultados[0].codigo == "P001"

        repositorio.cerrar()


def test_busqueda_de_paciente_por_dni_despues_de_recargar():
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "salud_prueba.db")

        repositorio_1 = RepositorioSalud(ruta)
        sistema_1 = SistemaSalud(repositorio_1)
        sistema_1.registrar_paciente(crear_paciente())
        repositorio_1.cerrar()

        repositorio_2 = RepositorioSalud(ruta)
        sistema_2 = SistemaSalud(repositorio_2)

        resultados = sistema_2.buscar_paciente_por_dni("12345678")

        assert len(resultados) == 1
        assert resultados[0].codigo == "P001"
        assert resultados[0].dni == "********"

        repositorio_2.cerrar()


def test_busqueda_de_profesional_por_dni_protegido():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        profesional = crear_profesional()

        sistema.registrar_personal(profesional)
        resultados = sistema.buscar_personal_por_dni("87654321")

        assert len(resultados) == 1
        assert resultados[0].codigo_profesional == "PS001"

        repositorio.cerrar()


def test_dni_no_se_muestra_en_texto_plano():
    paciente = crear_paciente()
    profesional = crear_profesional()

    assert "12345678" not in paciente.mostrar_informacion()
    assert "87654321" not in profesional.mostrar_informacion()
    assert "********" in paciente.mostrar_informacion()
    assert "********" in profesional.mostrar_informacion()


def test_seguridad_datos_verifica_valor_correcto():
    sal, resumen = SeguridadDatos.proteger("12345678")

    assert SeguridadDatos.verificar(
        "12345678",
        sal,
        resumen
    )

    assert not SeguridadDatos.verificar(
        "87654321",
        sal,
        resumen
    )


def test_rechaza_edad_fuera_de_rango():
    with pytest.raises(ValueError):
        Paciente("P001", "12345678", "Paciente Demo", 121)


def test_rechaza_dni_con_longitud_incorrecta():
    with pytest.raises(ValueError):
        Paciente("P001", "123", "Paciente Demo", 30)


def test_registro_de_cita_con_entidades_existentes():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()
        profesional = crear_profesional()

        sistema.registrar_paciente(paciente)
        sistema.registrar_personal(profesional)

        cita = Cita(
            "C001",
            paciente,
            profesional,
            "15/09/2026",
            "Consulta general"
        )

        sistema.registrar_cita(cita)

        assert len(sistema.obtener_citas()) == 1
        assert sistema.obtener_citas()[0].estado == "Pendiente"

        repositorio.cerrar()


def test_no_registra_cita_con_paciente_inexistente():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()
        profesional = crear_profesional()
        sistema.registrar_personal(profesional)

        cita = Cita(
            "C001",
            paciente,
            profesional,
            "15/09/2026",
            "Consulta general"
        )

        with pytest.raises(ValueError, match="paciente no está registrado"):
            sistema.registrar_cita(cita)

        repositorio.cerrar()


def test_filtra_citas_pendientes():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()
        profesional = crear_profesional()
        sistema.registrar_paciente(paciente)
        sistema.registrar_personal(profesional)

        cita_1 = FabricaEntidades.crear_cita(
            "C001",
            paciente,
            profesional,
            "15/09/2026",
            "Consulta general"
        )
        cita_2 = FabricaEntidades.crear_cita(
            "C002",
            paciente,
            profesional,
            "16/09/2026",
            "Control",
            "Atendida"
        )

        sistema.registrar_cita(cita_1)
        sistema.registrar_cita(cita_2)

        pendientes = sistema.obtener_citas_pendientes()

        assert [cita.codigo for cita in pendientes] == ["C001"]

        repositorio.cerrar()


def test_actualizar_estado_de_cita():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()
        profesional = crear_profesional()
        sistema.registrar_paciente(paciente)
        sistema.registrar_personal(profesional)

        cita = Cita(
            "C001",
            paciente,
            profesional,
            "15/09/2026",
            "Consulta general"
        )
        sistema.registrar_cita(cita)

        sistema.actualizar_estado_cita("C001", "Atendida")

        assert sistema.obtener_citas()[0].estado == "Atendida"

        repositorio.cerrar()


def test_factory_crea_entidades():
    paciente = FabricaEntidades.crear_paciente(
        "P100",
        "11112222",
        "Paciente Factory",
        25
    )
    profesional = FabricaEntidades.crear_personal(
        "PS100",
        "22221111",
        "Profesional Factory",
        45,
        "Enfermería"
    )
    cita = FabricaEntidades.crear_cita(
        "C100",
        paciente,
        profesional,
        "20/09/2026",
        "Control"
    )

    assert paciente.codigo == "P100"
    assert profesional.codigo_profesional == "PS100"
    assert cita.paciente is paciente
    assert cita.profesional is profesional


def test_rechaza_nombre_con_numeros():
    with pytest.raises(ValueError, match="nombre"):
        Paciente("P001", "12345678", "Paciente 123", 30)


def test_normaliza_fecha_iso_a_formato_visible():
    paciente = crear_paciente()
    profesional = crear_profesional()

    cita = Cita(
        "C001",
        paciente,
        profesional,
        "2026-09-20",
        "Control"
    )

    assert cita.fecha == "20/09/2026"


def test_rechaza_fecha_invalida():
    paciente = crear_paciente()
    profesional = crear_profesional()

    with pytest.raises(ValueError, match="fecha"):
        Cita(
            "C001",
            paciente,
            profesional,
            "31/02/2026",
            "Control"
        )


def test_rechaza_cita_con_profesional_invalido():
    paciente = crear_paciente()

    with pytest.raises(ValueError, match="profesional"):
        Cita(
            "C001",
            paciente,
            object(),
            "20/09/2026",
            "Control"
        )


def test_no_permite_codigo_de_paciente_duplicado():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        sistema.registrar_paciente(crear_paciente("P001", "12345678"))

        with pytest.raises(ValueError, match="código"):
            sistema.registrar_paciente(
                crear_paciente("P001", "11112222")
            )

        repositorio.cerrar()


def test_no_permite_dni_de_paciente_duplicado_despues_de_recargar():
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "salud_prueba.db")
        repositorio_1 = RepositorioSalud(ruta)
        sistema_1 = SistemaSalud(repositorio_1)
        sistema_1.registrar_paciente(crear_paciente())
        repositorio_1.cerrar()

        repositorio_2 = RepositorioSalud(ruta)
        sistema_2 = SistemaSalud(repositorio_2)

        with pytest.raises(ValueError, match="DNI"):
            sistema_2.registrar_paciente(
                crear_paciente("P002", "12345678")
            )

        repositorio_2.cerrar()


def test_no_permite_codigo_de_profesional_duplicado():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        sistema.registrar_personal(crear_profesional("PS001", "87654321"))

        with pytest.raises(ValueError, match="código"):
            sistema.registrar_personal(
                crear_profesional("PS001", "22223333")
            )

        repositorio.cerrar()


def test_no_permite_atencion_duplicada_para_la_misma_cita():
    from modelos.atencion_medica import AtencionMedica

    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()
        profesional = crear_profesional()
        sistema.registrar_paciente(paciente)
        sistema.registrar_personal(profesional)

        cita = Cita(
            "C001",
            paciente,
            profesional,
            "20/09/2026",
            "Control"
        )
        sistema.registrar_cita(cita)

        sistema.registrar_atencion(
            AtencionMedica("A001", cita, "Diagnóstico de prueba")
        )

        with pytest.raises(ValueError, match="atención médica"):
            sistema.registrar_atencion(
                AtencionMedica("A002", cita, "Otro diagnóstico de prueba")
            )

        repositorio.cerrar()


def test_migracion_elimina_dni_en_texto_plano():
    import sqlite3

    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "legado.db")

        conexion = sqlite3.connect(ruta)
        conexion.execute(
            """
            CREATE TABLE pacientes (
                codigo TEXT PRIMARY KEY,
                dni TEXT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE personal (
                codigo_profesional TEXT PRIMARY KEY,
                dni TEXT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                especialidad TEXT NOT NULL
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE citas (
                codigo TEXT PRIMARY KEY,
                paciente_codigo TEXT NOT NULL,
                profesional_codigo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                motivo TEXT NOT NULL,
                estado TEXT NOT NULL
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE atenciones (
                codigo TEXT PRIMARY KEY,
                cita_codigo TEXT NOT NULL,
                diagnostico TEXT NOT NULL,
                estado TEXT NOT NULL
            )
            """
        )
        conexion.execute(
            "INSERT INTO pacientes VALUES (?, ?, ?, ?)",
            ("P001", "12345678", "Paciente Demo", 30),
        )
        conexion.execute(
            "INSERT INTO personal VALUES (?, ?, ?, ?, ?)",
            ("PS001", "87654321", "Profesional Demo", 40, "Medicina General"),
        )
        conexion.commit()
        conexion.close()

        repositorio = RepositorioSalud(ruta)
        conexion = sqlite3.connect(ruta)

        dni_paciente = conexion.execute(
            "SELECT dni, dni_hash, dni_salt FROM pacientes WHERE codigo = 'P001'"
        ).fetchone()
        dni_profesional = conexion.execute(
            "SELECT dni, dni_hash, dni_salt FROM personal WHERE codigo_profesional = 'PS001'"
        ).fetchone()

        assert dni_paciente[0] is None
        assert dni_paciente[1]
        assert dni_paciente[2]
        assert dni_profesional[0] is None
        assert dni_profesional[1]
        assert dni_profesional[2]

        conexion.close()
        repositorio.cerrar()


def test_busqueda_de_profesional_por_dni_despues_de_recargar():
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "salud_prueba.db")

        repositorio_1 = RepositorioSalud(ruta)
        sistema_1 = SistemaSalud(repositorio_1)
        sistema_1.registrar_personal(crear_profesional())
        repositorio_1.cerrar()

        repositorio_2 = RepositorioSalud(ruta)
        sistema_2 = SistemaSalud(repositorio_2)

        resultados = sistema_2.buscar_personal_por_dni("87654321")

        assert len(resultados) == 1
        assert resultados[0].codigo_profesional == "PS001"
        assert resultados[0].dni == "********"

        repositorio_2.cerrar()


def test_no_permite_dni_de_profesional_duplicado():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        sistema.registrar_personal(crear_profesional("PS001", "87654321"))

        with pytest.raises(ValueError, match="DNI"):
            sistema.registrar_personal(
                crear_profesional("PS002", "87654321")
            )

        repositorio.cerrar()


def test_rechaza_estado_de_cita_invalido():
    paciente = crear_paciente()
    profesional = crear_profesional()

    with pytest.raises(ValueError, match="Estado inválido"):
        Cita(
            "C001",
            paciente,
            profesional,
            "20/09/2026",
            "Control",
            "Cancelada"
        )


def test_rechaza_estado_de_atencion_invalido():
    from modelos.atencion_medica import AtencionMedica

    paciente = crear_paciente()
    profesional = crear_profesional()
    cita = Cita(
        "C001",
        paciente,
        profesional,
        "20/09/2026",
        "Control"
    )

    with pytest.raises(ValueError, match="Estado inválido"):
        AtencionMedica(
            "A001",
            cita,
            "Diagnóstico de prueba",
            "Cancelada"
        )


def test_no_registra_atencion_con_cita_inexistente():
    from modelos.atencion_medica import AtencionMedica

    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        paciente = crear_paciente()
        profesional = crear_profesional()
        cita = Cita(
            "C001",
            paciente,
            profesional,
            "20/09/2026",
            "Control"
        )
        atencion = AtencionMedica(
            "A001",
            cita,
            "Diagnóstico de prueba"
        )

        with pytest.raises(ValueError, match="cita no está registrada"):
            sistema.registrar_atencion(atencion)

        repositorio.cerrar()


def test_cambio_de_estado_de_cita_se_persiste():
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "salud_prueba.db")
        repositorio_1 = RepositorioSalud(ruta)
        sistema_1 = SistemaSalud(repositorio_1)
        paciente = crear_paciente()
        profesional = crear_profesional()
        sistema_1.registrar_paciente(paciente)
        sistema_1.registrar_personal(profesional)
        sistema_1.registrar_cita(
            Cita(
                "C001",
                paciente,
                profesional,
                "20/09/2026",
                "Control"
            )
        )
        sistema_1.actualizar_estado_cita("C001", "Atendida")
        repositorio_1.cerrar()

        repositorio_2 = RepositorioSalud(ruta)
        sistema_2 = SistemaSalud(repositorio_2)

        assert sistema_2.obtener_citas()[0].estado == "Atendida"
        repositorio_2.cerrar()


def test_obtener_nombres_pacientes_usa_map():
    with tempfile.TemporaryDirectory() as carpeta:
        sistema, repositorio = crear_sistema_temporal(carpeta)
        sistema.registrar_paciente(crear_paciente())

        assert sistema.obtener_nombres_pacientes() == ["Paciente Demo"]
        repositorio.cerrar()
