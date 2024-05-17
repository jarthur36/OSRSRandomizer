document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.trading-card').forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
    });
    document.querySelectorAll('.legendary').forEach(card => {
        card.addEventListener('click', function() {
            document.body.style.backgroundColor = "orange"
        });
    });
});
