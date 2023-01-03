const btn = document.querySelector("button.mobile-menu-button");
const menu = document.querySelector(".mobile-menu");

btn.addEventListener("click", () => {
	menu.classList.toggle("hidden");
});

function toggleMenu() {
	if (window.matchMedia('(min-width: 768px)').matches && !menu.classList.contains('hidden')) {
	  menu.classList.toggle("hidden");
	}
  }
  
  // Run the toggleMenu function whenever the window is resized
  window.addEventListener('resize', toggleMenu);