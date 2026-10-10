```javascript
document.addEventListener('DOMContentLoaded', function () {
    // 1. Resume Match Score and Circular Gauge
    const scoreElement = document.getElementById('animated-score');
    const gaugeFill = document.getElementById('gaugeFill');

    if (scoreElement) {
        const rawScore = scoreElement.getAttribute('data-target');
        const targetValue = Number.parseFloat(rawScore);

        if (rawScore !== null && Number.isFinite(targetValue)) {
            const score = Math.max(0, Math.min(100, targetValue));

            // Display the actual score immediately
            scoreElement.textContent = score.toFixed(1) + '%';

            const circumference = 477.52;

            if (gaugeFill) {
                // Set circle color according to score
                if (score >= 75) {
                    gaugeFill.style.stroke = '#10b981';
                } else if (score >= 50) {
                    gaugeFill.style.stroke = '#f59e0b';
                } else {
                    gaugeFill.style.stroke = '#ef4444';
                }

                // Animate the circular gauge
                const offset =
                    circumference - (circumference * score / 100);

                gaugeFill.style.strokeDasharray = circumference;
                gaugeFill.style.strokeDashoffset = circumference;

                requestAnimationFrame(function () {
                    gaugeFill.style.transition =
                        'stroke-dashoffset 1.2s ease, stroke 0.3s ease';
                    gaugeFill.style.strokeDashoffset = offset;
                });
            }
        } else {
            console.error('Invalid resume match score:', rawScore);
            scoreElement.textContent = '—';
        }
    }

    // 2. Animate Horizontal Progress Bars
    const progressBars = document.querySelectorAll('.animate-progress');

    progressBars.forEach(function (bar) {
        const targetWidth =
            bar.getAttribute('data-width') ||
            bar.style.width ||
            '0%';

        bar.style.width = '0%';

        setTimeout(function () {
            bar.style.transition = 'width 1s ease';
            bar.style.width = targetWidth;
        }, 120);
    });

    // 3. Animate Skill and Metric Progress Bars
    const metricFills = document.querySelectorAll('.metric-progress-fill');

    metricFills.forEach(function (fill) {
        const targetWidth = fill.style.width || '0%';

        fill.style.width = '0%';

        setTimeout(function () {
            fill.style.transition = 'width 1s ease';
            fill.style.width = targetWidth;
        }, 150);
    });

    // 4. Toggle All Job Matches
    const toggleBtn = document.getElementById('toggleAllJobsBtn');
    const container = document.getElementById('allJobsContainer');
    const toggleText = document.getElementById('toggleText');
    const toggleIcon = document.getElementById('toggleIcon');

    if (toggleBtn && container) {
        toggleBtn.addEventListener('click', function () {
            const isHidden =
                window.getComputedStyle(container).display === 'none';

            if (isHidden) {
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

    // 5. Debug Information
    console.log('Resume analysis result page loaded.');

    if (scoreElement) {
        console.log(
            'Resume match score:',
            scoreElement.textContent
        );
    }
});
```