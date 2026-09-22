class Reportes:

    def __init__(self, sistema):
        self.sistema = sistema

    # ==========================================
    # REPORTE DE PACIENTES
    # ==========================================

    def reporte_pacientes(self):

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        nombres = list(
            map(
                lambda paciente:
                    paciente.nombre,
                pacientes
            )
        )

        edades = list(
            map(
                lambda paciente:
                    paciente.edad,
                pacientes
            )
        )

        return {
            "total_pacientes": len(pacientes),
            "nombres": nombres,
            "edades": edades
        }

    # ==========================================
    # REPORTE DE PROFESIONALES
    # ==========================================

    def reporte_profesionales(self):

        profesionales = (
            self.sistema.obtener_personal()
        )

        especialidades = list(
            map(
                lambda profesional:
                    profesional.especialidad,
                profesionales
            )
        )

        return {
            "total_profesionales":
                len(profesionales),

            "especialidades":
                especialidades
        }

    # ==========================================
    # REPORTE DE CITAS
    # ==========================================

    def reporte_citas(self):

        citas = (
            self.sistema.obtener_citas()
        )

        pendientes = list(
            filter(
                lambda cita:
                    cita.estado == "Pendiente",
                citas
            )
        )

        atendidas = list(
            filter(
                lambda cita:
                    cita.estado == "Atendida",
                citas
            )
        )

        reprogramadas = list(
            filter(
                lambda cita:
                    cita.estado == "Reprogramar",
                citas
            )
        )

        return {
            "total_citas": len(citas),
            "pendientes": len(pendientes),
            "atendidas": len(atendidas),
            "reprogramadas": len(reprogramadas)
        }

    # ==========================================
    # REPORTE DE ATENCIONES
    # ==========================================

    def reporte_atenciones(self):

        atenciones = (
            self.sistema.obtener_atenciones()
        )

        diagnosticos = list(
            map(
                lambda atencion:
                    atencion.diagnostico,
                atenciones
            )
        )

        pendientes = list(
            filter(
                lambda atencion:
                    atencion.estado == "Pendiente",
                atenciones
            )
        )

        en_proceso = list(
            filter(
                lambda atencion:
                    atencion.estado == "En proceso",
                atenciones
            )
        )

        finalizadas = list(
            filter(
                lambda atencion:
                    atencion.estado == "Finalizada",
                atenciones
            )
        )

        return {
            "total_atenciones":
                len(atenciones),

            "diagnosticos":
                diagnosticos,

            "pendientes":
                len(pendientes),

            "en_proceso":
                len(en_proceso),

            "finalizadas":
                len(finalizadas)
        }

    # ==========================================
    # REPORTE GENERAL
    # ==========================================

    def reporte_general(self):

        pacientes = (
            self.sistema.obtener_pacientes()
        )

        profesionales = (
            self.sistema.obtener_personal()
        )

        citas = (
            self.sistema.obtener_citas()
        )

        atenciones = (
            self.sistema.obtener_atenciones()
        )

        return {
            "pacientes": len(pacientes),
            "profesionales": len(profesionales),
            "citas": len(citas),
            "atenciones": len(atenciones)
        }