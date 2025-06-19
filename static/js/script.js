document.addEventListener("DOMContentLoaded", function () {
    initializeTaskWheel();
});

function initializeTaskWheel() {
    const petals = document.querySelectorAll(".task-petal");
    const wheel = document.querySelector(".wheel");
    const radius = 200;
    const centerX = wheel.offsetWidth / 2;
    const centerY = wheel.offsetHeight / 2;
    const count = petals.length;

    petals.forEach((petal, i) => {
        const angle = (2 * Math.PI * i) / count;
        const x = centerX + radius * Math.cos(angle) - petal.offsetWidth / 2;
        const y = centerY + radius * Math.sin(angle) - petal.offsetHeight / 2;

        petal.style.left = `${x}px`;
        petal.style.top = `${y}px`;
    });
}
