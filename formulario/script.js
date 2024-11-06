// script.js



// Crear celdas de horario con identificadores únicos para cada hora de cada día
const days = ["monday", "tuesday", "wednesday", "thursday", "friday"];
const startHour = 7;
const endHour = 22;

days.forEach(day => {
    const dayColumn = document.getElementById(day);
    for (let hour = startHour; hour < endHour; hour++) {
        const cell = document.createElement("div");
        cell.className = "time-slot";
        cell.id = `${day}-${hour}:00`;
        cell.textContent = `${hour}:00 - ${hour + 1}:00`;
        dayColumn.appendChild(cell);
    }
});




function showSection(sectionId) {
    // Oculta todas las secciones
    const sections = document.querySelectorAll('.tab-content');
    sections.forEach(section => section.style.display = 'none');
    
    // Muestra solo la sección seleccionada
    document.getElementById(sectionId).style.display = 'block';
}

function agregar() {
    const day = document.getElementById('day').value.toLowerCase();
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
    const classInfo = "Clase"; // Esto es solo un ejemplo.

    // Diccionario para traducir el día de español a inglés
    const dayTranslations = {
        "lunes": "monday",
        "martes": "tuesday",
        "miércoles": "wednesday",
        "jueves": "thursday",
        "viernes": "friday"
    };

    // Convertir el día en español al identificador en inglés
    const dayInEnglish = dayTranslations[day];

    // Convertir horas a formato numérico para iterar en el rango
    const startHour = parseInt(startTime.split(":")[0]);
    const endHour = parseInt(endTime.split(":")[0]);

    // Iterar a través de las horas seleccionadas y actualizar las celdas correspondientes
    for (let hour = startHour; hour < endHour; hour++) {
        const cellId = `${dayInEnglish}-${hour}:00`;
        const cell = document.getElementById(cellId);
        if (cell) {
            cell.textContent = classInfo;
            cell.classList.add("scheduled");
        }
    }
}



// Función auxiliar para convertir horas a minutos
function convertTimeToMinutes(time) {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
}




