// The burger: on a narrow screen the nav folds behind one button. Without this
// script the button never shows and the nav simply wraps, so the page works
// before it runs (progressive enhancement). The admin does not load it.
const burger = document.querySelector(".chrome-burger");
const menu = document.getElementById("chrome-menu");

if (burger && menu) {
  document.documentElement.classList.add("menu-ready");
  const open = (yes) => {
    menu.classList.toggle("open", yes);
    burger.setAttribute("aria-expanded", String(yes));
  };
  burger.addEventListener("click", () => open(burger.getAttribute("aria-expanded") !== "true"));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.classList.contains("open")) {
      open(false);
      burger.focus();
    }
  });
}
