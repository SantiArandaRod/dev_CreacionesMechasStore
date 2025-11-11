    const menuContainer = document.querySelector('.menu-container');
    const menuButton = document.getElementById('menuButton');
    const salirButton = document.querySelector('.menu-item:last-child');

    menuButton.addEventListener('click', () => {
      menuContainer.classList.toggle('active');
    });

    salirButton.addEventListener('click', () => {
      menuContainer.classList.remove('active');
    });
