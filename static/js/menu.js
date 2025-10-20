  const menuContainer = document.querySelector('.menu-container');
  const menuButton = document.getElementById('menuButton');

  menuButton.addEventListener('click', () => {
    menuContainer.classList.toggle('active');
  });
