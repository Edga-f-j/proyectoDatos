# gestion_asignaciones.py
from datos_iniciales import salones, cursos, profesores, bloques_de_tiempo, verificar_disponibilidad

# Aquí puedes agregar funciones avanzadas, como la función `asignar_salon`
def asignar_salon(curso_id, bloque):
    curso = next((c for c in cursos if c["id"] == curso_id), None)
    if curso:
        for salon in salones:
            if all(req in salon["equipos"] for req in curso["requerimientos"]) and verificar_disponibilidad(salon["id"], bloque):
                salon["disponibilidad"][bloque] = curso_id
                print(f"Curso {curso_id} asignado al salón {salon['id']} en el bloque {bloque}.")
                return
        print(f"No hay salones disponibles para el curso {curso_id} en el bloque {bloque}.")
    else:
        print(f"Curso {curso_id} no encontrado.")



# Pruebas de asignación
asignar_salon(1, "07:00-09:00")  # Curso Matemáticas Básicas
asignar_salon(2, "09:00-11:00")  # Curso Introducción a la Computación
asignar_salon(3, "11:00-13:00")  # Curso Historia Universal

# Intento de asignación a un bloque ocupado
asignar_salon(2, "07:00-09:00")  # Curso Introducción a la Computación en el mismo bloque que Matemáticas

# Verificación de disponibilidad actualizada
print(salones)