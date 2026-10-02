document.addEventListener('DOMContentLoaded', function() {
    const scoreElement = document.getElementById('animated-score');
    if (!scoreElement) return;

    const targetScore = parseFloat(scoreElement.getAttribute('data-target')) || 0;
    let currentScore = 0;
    const duration = 1200; // ms
    const stepTime = 15;
    const steps = duration / stepTime;
    const increment = targetScore / steps;

    const timer = setInterval(function() {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(timer);
        }
        scoreElement.textContent = Math.round(currentScore) + '%';
    }, stepTime);
});
