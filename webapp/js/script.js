// Smooth scroll para la sección de servicios
document.querySelector('.cta-button').addEventListener('click', function() {
  document.querySelector('.services').scrollIntoView({ behavior: 'smooth' });
});
