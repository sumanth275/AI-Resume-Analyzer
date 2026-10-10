```javascript
/* ==========================================================================
   RESULT & SCORE GAUGE ANIMATION CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Animate Hero Score Gauge & Number Count-Up
    const scoreElement = document.getElementById('animated-score');
    const gaugeFill = document.getElementById('gaugeFill');

    if (scoreElement) {
        const targetValue = parseFloat(
            scoreElement.getAttribute('data-target')
        ) || 0;

        const circumference = 477.52;
        const duration = 1200;
        const steps = 50;
        const increment = targetValue / steps;
        const stepTime = duration / steps;
        let currentValue = 0;

        if (gaugeFill) {
            const strokeDashoffset =
                circumference - (circumference * targetValue / 100);

            if (targetValue >= 75) {
                gaugeFill.style.stroke = '#10b981';
            } else if (targetValue >= 50) {
                gaugeFill.style.stroke = '#f59e0b';
            } else {
                gaugeFill.style.stroke = '#ef4444';
            }

            setTimeout(() => {
                gaugeFill.style.transition =
                    `stroke-dashoffset ${duration}ms cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease`;
                gaugeFill.style.strokeDashoffset = strokeDashoffset;
            }, 60);
        }

        const timer = setInterval(() => {
            currentValue += increment;

            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }

            scoreElement.textContent = currentValue.toFixed(1) + '%';
        }, stepTime);
    }

    // 2. Animate horizontal progress bars
    const progressBars = document.querySelectorAll('.animate-progress');

    progressBars.forEach(bar => {
        const targetWidth =
            bar.getAttribute('data-width') || bar.style.width || '0%';

        bar.style.width = '0%';

        setTimeout(() => {
            bar.style.transition =
                'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
            bar.style.width = targetWidth;
        }, 120);
    });

    // 3. Animate metric progress bars
    const metricFills = document.querySelectorAll('.metric-progress-fill');

    metricFills.forEach(fill => {
        const targetWidth = fill.style.width;

        fill.style.width = '0%';

        setTimeout(() => {
            fill.style.transition = 'width 1s ease';
            fill.style.width = targetWidth;
        }, 150);
    });

    // 4. Toggle all job matches
    const toggleBtn = document.getElementById('toggleAllJobsBtn');
    const container = document.getElementById('allJobsContainer');
    const toggleText = document.getElementById('toggleText');
    const toggleIcon = document.getElementById('toggleIcon');

    if (toggleBtn && container) {
        toggleBtn.addEventListener('click', () => {
            if (
                container.style.display === 'none' ||
                !container.style.display
            ) {
                container.style.display = 'block';

                if (toggleText) {
                    toggleText.textContent = 'Hide 20 Job Matches';
                }

                if (toggleIcon) {
                    toggleIcon.className = 'fa-solid fa-eye-slash';
                }
            } else {
                container.style.display = 'none';

                if (toggleText) {
                    toggleText.textContent = 'View All 20 Job Matches';
                }

                if (toggleIcon) {
                    toggleIcon.className = 'fa-solid fa-eye';
                }
            }
        });
    }
});
```