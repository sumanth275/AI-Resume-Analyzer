/* ==========================================================================
   RESULT & SCORE GAUGE ANIMATION CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Animate Hero Score Gauge & Number Count-Up
    const scoreElement = document.getElementById('animated-score');
    const gaugeFill = document.getElementById('gaugeFill');

    if (scoreElement) {
        const targetValue = parseFloat(scoreElement.getAttribute('data-target')) || 0;
        const circumference = 477.52; // 2 * PI * 76
        const duration = 1200; // ms
        const steps = 50;
        const increment = targetValue / steps;
        const stepTime = duration / steps;
        let currentValue = 0;

        // Apply SVG gauge fill & stroke color based on targetValue score
        if (gaugeFill) {
            const strokeDashoffset = circumference - (circumference * targetValue / 100);
            
            if (targetValue >= 75) {
                gaugeFill.style.stroke = '#10b981'; // Green
            } else if (targetValue >= 50) {
                gaugeFill.style.stroke = '#f59e0b'; // Orange
            } else {
                gaugeFill.style.stroke = '#ef4444'; // Red
            }

            // Animate stroke dashoffset after DOM render
            setTimeout(() => {
                gaugeFill.style.transition = `stroke-dashoffset ${duration}ms cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease`;
                gaugeFill.style.strokeDashoffset = strokeDashoffset;
            }, 60);
        }

        // Animated number count-up
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            scoreElement.textContent = currentValue.toFixed(1) + '%';
        }, stepTime);
    }

    // 2. Animate Horizontal Progress Bars across Cards & Job Suitability Ranking
    const progressBars = document.querySelectorAll('.animate-progress');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('data-width') || bar.style.width || '0%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
            bar.style.width = targetWidth;
        }, 120);
    });
});
