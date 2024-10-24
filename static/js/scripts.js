// static/js/scripts.js

// Ejemplo: Resaltar una tarjeta de producto al hacer clic
document.addEventListener('DOMContentLoaded', () => {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        card.addEventListener('click', () => {
            card.classList.toggle('highlight');
        });
    });
});

function updateSubtotal(itemId, itemPrice) {
    const quantityInput = document.querySelector(`input[name="quantity_${itemId}"]`);
    const quantity = parseInt(quantityInput.value) || 0;
    const subtotalElement = document.querySelector(`#subtotal_${itemId}`);
    const subtotal = itemPrice * quantity;
    subtotalElement.textContent = `$${subtotal.toFixed(2)}`;

    updateTotal();
}

function updateTotal() {
    let total = 0;
    const subtotals = document.querySelectorAll('[id^="subtotal_"]');
    subtotals.forEach(subtotal => {
        const value = parseFloat(subtotal.textContent.replace('$', ''));
        total += value;
    });
    document.querySelector('#totalAmount').textContent = `$${total.toFixed(2)}`;
}


// Seleccionar el botón del menú hamburguesa y el contenedor de enlaces
const menuToggle = document.getElementById('menu-toggle');
const navLinks = document.getElementById('nav-links');

// Añadir un evento al menú hamburguesa para alternar la visibilidad de los enlaces
menuToggle.addEventListener('click', function() {
    // Si los enlaces están ocultos, mostrarlos; si están visibles, ocultarlos
    if (navLinks.style.display === 'block') {
        navLinks.style.display = 'none';
    } else {
        navLinks.style.display = 'block';
    }
});

// INICIO DE JS PARA BARRA DE BUSQUEDA
document.addEventListener("DOMContentLoaded", function () {
  // Obtener el ícono y el formulario
  const searchIcon = document.getElementById('show-search-form');
  const searchForm = document.getElementById('search-form');

  // Asegurarse de que el formulario esté oculto inicialmente
  searchForm.style.display = "none";

  // Evento de clic para mostrar el formulario
  searchIcon.addEventListener('click', function (e) {
      e.preventDefault(); // Evitar que el enlace recargue la página
      if (searchForm.style.display === "none") {
          searchForm.style.display = "flex"; // Mostrar el formulario
      } else {
          searchForm.style.display = "none"; // Ocultar el formulario si ya está visible
      }
  });
});

document.addEventListener("DOMContentLoaded", function() {
  // Detectar cuando la pantalla es menor a 768px
  function roundNumbers() {
      if (window.innerWidth <= 768) {
          // Seleccionar solo las celdas de precios y subtotales
          const priceCells = document.querySelectorAll("td.text-right");

          priceCells.forEach(function(cell) {
              // Asegurarse de que el valor contenga números (ignorar las celdas de "Acciones" u otras no numéricas)
              let value = cell.textContent.trim();
              if (value.startsWith('$')) {
                  // Convertir a número, redondear hacia arriba y actualizar
                  let numericValue = parseFloat(value.replace('$', ''));
                  let roundedValue = Math.ceil(numericValue); // Redondear hacia arriba
                  cell.textContent = `$${roundedValue}`; // Actualizar el contenido de la celda
              }
          });
      }
  }

  // Ejecutar cuando la página se carga y también cuando la ventana cambia de tamaño
  window.addEventListener('resize', roundNumbers);
  roundNumbers(); // Llamar a la función cuando la página cargue
});


// Ejemplo: Mostrar una alerta cuando se carga la página de clientes
document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname === '/mis_clientes') {
      console.log('Página de clientes cargada');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname === '/mi_blog') {
      console.log('Página de blog cargada');
  }
});
// fin de pagina de clientes

// scripts para el blog

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname === '/mi_blog') {
      console.log('Página de blog cargada');
  }
});

function mostrarArticulo(index) {
  const articulo = articulos[index];

  document.getElementById('articulo-titulo').innerText = articulo.titulo;
  document.getElementById('articulo-imagen').src = `/static/images/mi_blog/${articulo.imagen}`;
  
  const contenidoDiv = document.getElementById('articulo-contenido');
  contenidoDiv.innerHTML = '';
  articulo.contenido.forEach(parrafo => {
      const p = document.createElement('p');
      p.innerText = parrafo;
      contenidoDiv.appendChild(p);
  });

  document.getElementById('articulo-completo').style.display = 'block';
}

function cerrarArticulo() {
  document.getElementById('articulo-completo').style.display = 'none';
}

// fin de blog


// JS PARA EL CAROUSEL - INICIO

// Seleccionamos todo dentro de conteudo__geral para evitar afectar otros elementos
const conteudoGeral = document.querySelector(".conteudo__geral");
const container = conteudoGeral.querySelector(".container");
const containerCarrossel = container.querySelector(".container-carrossel");
const carrossel = container.querySelector(".carrossel");
const carrosselItems = carrossel.querySelectorAll(".carrossel-item");

// Variables que gestionan el estado del carrusel
let isMouseDown = false;
let currentMousePos = 0;
let lastMousePos = 0;
let lastMoveTo = 0;
let moveTo = 0;

// Función que crea el carrusel
const createCarrossel = () => {
  const carrosselProps = onResize();
  const length = carrosselItems.length; // Número de items en el carrusel
  const degrees = 360 / length; // Ángulo entre cada item
  const gap = 20; // Espacio entre items
  const tz = distanceZ(carrosselProps.w, length, gap); // Calculamos la distancia Z

  const height = calculateHeight(tz); // Altura del contenedor basado en la distancia Z

  // Ajustamos el tamaño del contenedor según el cálculo
  container.style.width = tz * 2 + gap * length + "px";
  container.style.height = height + "px";

  // Establecemos la rotación y posición Z para cada item del carrusel
  carrosselItems.forEach((item, i) => {
    const degreesByItem = degrees * i + "deg";
    item.style.setProperty("--rotatey", degreesByItem);
    item.style.setProperty("--tz", tz + "px");
  });
};

// Función para suavizar la animación de rotación
const lerp = (a, b, n) => {
  return n * (a - b) + b;
};

// Calcula la distancia Z para el carrusel
const distanceZ = (widthElement, length, gap) => {
  return widthElement / 2 / Math.tan(Math.PI / length) + gap;
};

// Calcula la altura del contenedor del carrusel basado en la distancia Z
const calculateHeight = (z) => {
  const t = Math.atan((90 * Math.PI) / 180 / 2);
  return t * 2 * z;
};

// Detecta la posición X del mouse o toque
const getPosX = (x) => {
  currentMousePos = x;
  moveTo = currentMousePos < lastMousePos ? moveTo - 2 : moveTo + 2;
  lastMousePos = currentMousePos;
};

// Actualiza el carrusel en cada frame de animación
const update = () => {
  lastMoveTo = lerp(moveTo, lastMoveTo, 0.05);
  carrossel.style.setProperty("--rotatey", lastMoveTo + "deg");
  requestAnimationFrame(update);
};

// Ajusta el carrusel cuando cambia el tamaño de la ventana
const onResize = () => {
  const boundingCarrossel = containerCarrossel.getBoundingClientRect();
  return {
    w: boundingCarrossel.width,
    h: boundingCarrossel.height
  };
};

// Inicializa los eventos del carrusel para el mouse y touch
const initEvents = () => {
  // Eventos de mouse
  carrossel.addEventListener("mousedown", () => {
    isMouseDown = true;
    carrossel.style.cursor = "grabbing";
  });

  carrossel.addEventListener("mouseup", () => {
    isMouseDown = false;
    carrossel.style.cursor = "grab";
  });

  conteudoGeral.addEventListener("mouseleave", () => {
    isMouseDown = false;
  });

  carrossel.addEventListener("mousemove", (e) => {
    if (isMouseDown) getPosX(e.clientX);
  });

  // Eventos de touch (pantallas táctiles)
  carrossel.addEventListener("touchstart", () => {
    isMouseDown = true;
    carrossel.style.cursor = "grabbing";
  });

  carrossel.addEventListener("touchend", () => {
    isMouseDown = false;
    carrossel.style.cursor = "grab";
  });

  conteudoGeral.addEventListener("touchmove", (e) => {
    if (isMouseDown) getPosX(e.touches[0].clientX);
  });

  // Llamamos a las funciones necesarias para actualizar y crear el carrusel
  window.addEventListener("resize", createCarrossel);
  update();
  createCarrossel();
};

// Iniciamos los eventos cuando la página esté lista
initEvents();


// JS PARA EL CAROUSEL - FIN