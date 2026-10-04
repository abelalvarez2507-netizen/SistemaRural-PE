from modelos.paciente import Paciente
from modelos.personal_salud import PersonalSalud
from modelos.personal_enfermeria import PersonalEnfermeria
from modelos.cita import Cita
from modelos.atencion_medica import AtencionMedica


class FabricaEntidades:
    """
    Factory responsable de centralizar la creación
    de objetos principales del sistema.
    """

    @staticmethod
    def crear_paciente(
        codigo,
        dni,
        nombre,
        edad
    ):
        return Paciente(
            codigo,
            dni,
            nombre,
            edad
        )

    @staticmethod
    def crear_paciente_desde_datos_protegidos(
        codigo,
        dni_hash,
        dni_salt,
        nombre,
        edad
    ):
        return Paciente.desde_datos_protegidos(
            codigo,
            dni_hash,
            dni_salt,
            nombre,
            edad
        )

    @staticmethod
    def crear_personal(
        codigo_profesional,
        dni,
        nombre,
        edad,
        especialidad
    ):
        clase = (
            PersonalEnfermeria
            if "enfermer" in str(especialidad).casefold()
            else PersonalSalud
        )
        return clase(
            codigo_profesional,
            dni,
            nombre,
            edad,
            especialidad
        )

    @staticmethod
    def crear_personal_desde_datos_protegidos(
        codigo_profesional,
        dni_hash,
        dni_salt,
        nombre,
        edad,
        especialidad
    ):
        clase = (
            PersonalEnfermeria
            if "enfermer" in str(especialidad).casefold()
            else PersonalSalud
        )
        return clase.desde_datos_protegidos(
            codigo_profesional,
            dni_hash,
            dni_salt,
            nombre,
            edad,
            especialidad
        )

    @staticmethod
    def crear_cita(
        codigo,
        paciente,
        profesional,
        fecha,
        motivo,
        estado="Pendiente",
        hora="09:00",
    ):
        return Cita(
            codigo,
            paciente,
            profesional,
            fecha,
            motivo,
            estado,
            hora,
        )

    @staticmethod
    def crear_atencion(
        codigo,
        cita,
        diagnostico,
        estado="Pendiente",
        recetas=None,
    ):
        return AtencionMedica(
            codigo,
            cita,
            diagnostico,
            estado,
            recetas,
        )
