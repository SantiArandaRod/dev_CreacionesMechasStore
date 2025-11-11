function updateClock() {
  const now = new Date();

  // Formato de hora y minutos
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  const timeString = `${hours}:${minutes}:${seconds}`;

  // Formato de fecha (día de la semana, día, mes y año)
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const dateString = now.toLocaleDateString('es-ES', options);

  document.getElementById('clock-time').textContent = timeString;
  document.getElementById('clock-date').textContent = dateString;
}

// Actualiza cada segundo
setInterval(updateClock, 1000);
updateClock();
