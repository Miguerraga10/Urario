import copy
from Clases.Materia import Materia
from Clases.Grupo import Grupo
from Clases.Clase import Clase

def dict_to_materia(d):
    # d comes from DB or JSON
    grupos = []
    for g in d.get('grupos', []):
        horarios = []
        for h in g.get('horarios', []):
            horarios.append(Clase(
                nombre=h.get('materia', d.get('nombre')),
                dia=h.get('dia'),
                hora_inicio=h.get('hora_inicio', h.get('inicio')),
                hora_fin=h.get('hora_fin', h.get('fin')),
                lugar=h.get('lugar')
            ))
        grupos.append(Grupo(
            grupo=g.get('grupo'),
            horarios=horarios,
            creditos=g.get('creditos', d.get('creditos', 0)),
            cupos=g.get('cupos', 0),
            profesor=g.get('profesor'),
            duracion=g.get('duracion'),
            jornada=g.get('jornada')
        ))

    m = Materia(
        nombre=d.get('nombre'),
        codigo=d.get('codigo', ''),
        tipologia=d.get('tipologia', ''),
        creditos=d.get('creditos', 0),
        facultad=d.get('facultad', ''),
        carrera=d.get('carrera', ''),
        fechaExtraccion=d.get('fechaExtraccion', ''),
        cuposDisponibles=d.get('cuposDisponibles', 0),
        grupos=grupos,
        obligatoria=d.get('obligatoria', False)
    )
    return m

def materia_to_dict(m):
    return {
        'nombre': m.nombre,
        'codigo': getattr(m, 'codigo', ''),
        'tipologia': getattr(m, 'tipologia', ''),
        'creditos': getattr(m, 'creditos', 0),
        'facultad': getattr(m, 'facultad', ''),
        'carrera': getattr(m, 'carrera', ''),
        'fechaExtraccion': getattr(m, 'fechaExtraccion', ''),
        'cuposDisponibles': getattr(m, 'cuposDisponibles', 0),
        'grupos': [
            {
                'grupo': g.grupo,
                'cupos': getattr(g, 'cupos', 0),
                'profesor': getattr(g, 'profesor', None),
                'duracion': getattr(g, 'duracion', None),
                'jornada': getattr(g, 'jornada', None),
                'horarios': [
                    {
                        'inicio': h.hora_inicio,
                        'fin': h.hora_fin,
                        'dia': h.dia,
                        'lugar': h.lugar,
                        'materia': h.nombre
                    } for h in g.horarios
                ],
                'creditos': getattr(g, 'creditos', 0)
            } for g in getattr(m, 'grupos', [])
        ],
        'obligatoria': getattr(m, 'obligatoria', False)
    }
