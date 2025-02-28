document.addEventListener('DOMContentLoaded', function() {
    // Health Tips interaction
    document.querySelectorAll('.health-tip-card').forEach(card => {
        card.addEventListener('click', function() {
            const content = this.querySelector('.tip-content');
            content.classList.toggle('line-clamp-3');
            content.classList.toggle('line-clamp-none');
        });
    });

    // Recent Activity time formatting
    document.querySelectorAll('.activity-time').forEach(timeElement => {
        const date = new Date(timeElement.dataset.time);
        timeElement.textContent = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    });
});