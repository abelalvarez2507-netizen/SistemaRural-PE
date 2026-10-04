"""Pruebas del desplazamiento con mouse y touchpad (no abren ventanas)."""

from interfaz.navegacion import comando_barra, desplazar_por_evento


class _Tcl:
    def __init__(self, sistema):
        self.sistema = sistema

    def call(self, *_argumentos):
        return self.sistema


class _Raiz:
    def __init__(self, sistema):
        self.tk = _Tcl(sistema)


class _Lienzo:
    """Lienzo falso: contenido de 2000 px en una vista de 600 px."""

    def __init__(self, total=2000, vista=600, paso="1", sistema="win32"):
        self.total, self.vista, self.paso, self.arriba = total, vista, paso, 0
        self._raiz = _Raiz(sistema)

    def _root(self):
        return self._raiz

    def cget(self, _opcion):
        return self.paso

    def winfo_height(self):
        return self.vista

    def yview(self, *argumentos):
        if argumentos:
            return self.yview_scroll(int(argumentos[1]), argumentos[2])
        return (
            self.arriba / self.total,
            (self.arriba + self.vista) / self.total,
        )

    def yview_scroll(self, cantidad, _unidad):
        paso = float(self.paso) or self.vista / 10
        maximo = max(0, self.total - self.vista)
        self.arriba = max(0, min(maximo, self.arriba + int(cantidad * paso)))


class _Evento:
    def __init__(self, delta=0, num=None):
        self.delta, self.num = delta, num


def _mover(lienzo, *eventos):
    for evento in eventos:
        desplazar_por_evento(lienzo, evento)
    return lienzo.arriba


def test_rueda_de_mouse_baja_20_pixeles_por_clic():
    assert _mover(_Lienzo(), _Evento(-120)) == 20


def test_touchpad_con_deltas_pequenos_si_se_desplaza():
    assert _mover(_Lienzo(), *[_Evento(-30)] * 10) == 120


def test_touchpad_acumula_movimientos_diminutos():
    lienzo = _Lienzo()
    assert _mover(lienzo, _Evento(-2)) == 0
    assert _mover(lienzo, _Evento(-2), _Evento(-2)) == 2


def test_limites_no_se_pasan():
    assert desplazar_por_evento(_Lienzo(), _Evento(120)) is False
    final = _Lienzo()
    final.arriba = 1400
    assert desplazar_por_evento(final, _Evento(-120)) is False
    assert desplazar_por_evento(_Lienzo(total=500), _Evento(-120)) is False


def test_botones_de_linux_y_eventos_ajenos():
    assert _mover(_Lienzo(), _Evento(0, 5)) == 20
    assert desplazar_por_evento(_Lienzo(), _Evento(0, 1)) is None


def test_mac_usa_unidades_pequenas():
    assert _mover(_Lienzo(sistema="aqua"), _Evento(-3)) == 24


def test_flechas_de_la_barra_respetan_el_tamano_de_paso():
    llamadas = []

    class _Y:
        def yview(self, *argumentos):
            llamadas.append(argumentos)

    comando_barra(_Y())("scroll", "1", "units")
    comando_barra(_Y())("scroll", "1", "pages")
    assert llamadas == [("scroll", 20, "units"), ("scroll", "1", "pages")]
