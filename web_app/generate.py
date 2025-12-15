import os
# Indicar modo headless para evitar importaciones GUI cuando se cargue M10horariosplus
os.environ['HEADLESS'] = '1'
import M10horariosplus as mh
from . import convert

class MessageBoxStub:
    def showerror(self, title, msg):
        raise RuntimeError(msg)
    def showwarning(self, title, msg):
        raise RuntimeError(msg)

def generate_schedule(materias_dicts, intervalos):
    """Genera horario sin abrir ventanas GUI. Devuelve dict con resultado o error."""
    # Monkeypatch para evitar ventanas
    mh.mostrar_horario_qt = lambda *args, **kwargs: None
    mh.messagebox = MessageBoxStub()

    materias = [convert.dict_to_materia(d) for d in materias_dicts]
    try:
        horario = mh.generar_horarios(
            materias,
            mincreditos=intervalos.get('min_creditos', 1),
            maxcreditos=intervalos.get('max_creditos', float('inf')),
            minmaterias=intervalos.get('min_materias', 1),
            maxmaterias=intervalos.get('max_materias', float('inf')),
            hora_inicio=intervalos.get('min_horas', '08:00'),
            hora_fin=intervalos.get('max_horas', '20:00'),
            usar_cupos=intervalos.get('usar_cupos', False),
            maxdias=intervalos.get('max_dias', 7),
            usar_virtuales=intervalos.get('usar_virtuales', True),
            horas_libres=intervalos.get('horas_libres', [])
        )
    except RuntimeError as e:
        return {'success': False, 'error': str(e)}

    if horario is None:
        return {'success': False, 'error': 'No se encontró un horario viable.'}

    # Serializar horario mínimo: días -> horas
    resultado = {
        'success': True,
        'horario': horario.dias,
        'materias_seleccionadas': [(g.horarios[0].nombre, g.grupo) for g in horario.grupos]
    }
    return resultado
