document.addEventListener("DOMContentLoaded", () => {
    const posts = document.querySelectorAll(".blog-post-card");
    const links = document.querySelectorAll(".blog-title-link");

    const linkMap={};
    links.forEach(link => {
        linkMap[link.dataset.postId] = link;
    });

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.dataset.postId;

                    links.forEach(l => l.classList.remove("active"));

                    if (linkMap[id]) {
                        linkMap[id].classList.add("active");
                    }
                }
            });
        },
        {
            root: document.querySelector(".blog-posts"),
            threshold: 0.4
        }
    );

    posts.forEach(post => observer.observe(post));
});