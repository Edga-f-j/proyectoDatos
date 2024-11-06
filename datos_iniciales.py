# Ejemplo de estructura de datos en Python

# Datos predefinidos para profesores y horarios
profesores = [
    {"id": 1, "nombre": "Juan Pérez", "rol": "Docente"},
    {"id": 2, "nombre": "María Gómez", "rol": "Supervisión"},
    {"id": 3, "nombre": "Carlos Ruiz", "rol": "Seguimiento"},
    # Agrega más profesores según sea necesario
]

# Ejemplo de bloques de tiempo predefinidos (formato de 24 horas)
bloques_de_tiempo = [
    {"inicio": "07:00", "fin": "09:00"},
    {"inicio": "09:00", "fin": "11:00"},
    {"inicio": "11:00", "fin": "13:00"},
    # Añade los bloques hasta cubrir el horario de 7:00 a 22:00
]

# Ejemplo de salones
salones = [
    {"id": 101, "capacidad": 30, "equipos": ["Computadora", "Proyector"], "disponibilidad": {}},
    {"id": 102, "capacidad": 25, "equipos": ["Computadora"], "disponibilidad": {}},
    {"id": 103, "capacidad": 40, "equipos": ["Computadora", "Proyector", "Pizarra"], "disponibilidad": {}},
    # Más salones pueden añadirse aquí
]

# Ejemplo de cursos
cursos = [
    {"id": 1, "nombre": "Matemáticas Básicas", "duracion": 2, "requerimientos": ["Pizarra"]},
    {"id": 2, "nombre": "Introducción a la Computación", "duracion": 3, "requerimientos": ["Computadora", "Proyector"]},
    {"id": 3, "nombre": "Historia Universal", "duracion": 1, "requerimientos": ["Pizarra"]},
    # Más cursos se pueden agregar según la simulación
]

# Función para verificar la disponibilidad de un salón para un bloque de tiempo
def verificar_disponibilidad(salon_id, bloque):
    for salon in salones:
        if salon["id"] == salon_id:
            return bloque not in salon["disponibilidad"]

# Función para asignar un salón a un curso en un bloque de tiempo específico
def asignar_salon_a_curso(salon_id, curso_id, bloque):
    if verificar_disponibilidad(salon_id, bloque):
        for salon in salones:
            if salon["id"] == salon_id:
                salon["disponibilidad"][bloque] = curso_id
                print(f"Curso {curso_id} asignado al salón {salon_id} en el bloque {bloque}.")
    else:
        print(f"El salón {salon_id} no está disponible en el bloque {bloque}.")

# Ejemplo de asignación de un curso a un salón en un bloque de tiempo
asignar_salon_a_curso(101, 1, "07:00-09:00")
