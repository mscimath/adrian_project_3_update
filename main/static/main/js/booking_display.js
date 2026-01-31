document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".service-card");

    cards.forEach(card => {
        const btn = card.querySelector(".book-btn");
        if (!btn) return;

        card.addEventListener("mouseenter", () => {
            btn.style.opacity = "1";
            btn.style.pointerEvents = "auto";
            btn.style.transform = "translateY(0)";
        });

        card.addEventListener("mouseleave", () => {
            btn.style.opacity = "0";
            btn.style.pointerEvents = "none";
            btn.style.transform = "translateY(10px)";
        });
    });
});