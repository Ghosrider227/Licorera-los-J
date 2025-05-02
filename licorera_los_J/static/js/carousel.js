document.addEventListener("DOMContentLoaded", function () {
    const items = document.querySelectorAll(".carousel-item");
    let currentIndex = 0;

    function showNextItem() {
        const currentItem = items[currentIndex];
        currentItem.classList.remove("active");

        currentIndex = (currentIndex + 1) % items.length;

        const nextItem = items[currentIndex];
        nextItem.classList.add("active");
    }

    // Cambiar cada 5 segundos
    setInterval(showNextItem, 5000);
});