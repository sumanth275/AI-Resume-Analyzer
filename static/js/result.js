/* ==========================================================================
   RESULT & SCORE GAUGE ANIMATION CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const scoreElement = document.getElementById('animated-score');
    if (scoreElement) {
        const targetValue = parseFloat(scoreElement.getAttribute('data-target')) || 0;
        let currentValue = 0;
        const duration = 1200; // ms
        const steps = 40;
        const increment = targetValue / steps;
        const stepTime = duration / steps;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            scoreElement.textContent = currentValue.toFixed(1) + '%';
        }, stepTime);
    }
});
