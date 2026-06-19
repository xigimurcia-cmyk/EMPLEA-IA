// Función para mostrar u ocultar la contraseña
function mostrarContrasena(id) {
  const input = document.getElementById(id); // busca el campo por su id
  if (input.type === "password") {           // si está oculto
    input.type = "text";                     // lo muestra
  } else {                                   // si está visible
    input.type = "password";                 // lo oculta
  }
}

// Función para el menú hamburguesa (☰)
// Se usa en todas las pantallas con header móvil
function toggleMenu() {
  const menu = document.getElementById('menu-principal');
  menu.classList.toggle('active');
}