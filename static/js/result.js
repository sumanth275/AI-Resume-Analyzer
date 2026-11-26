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

    console.log('Resume analysis result page loaded.');
});

// Interactive Filter for Tech Hub Jobs (Bangalore & Hyderabad)
function filterHubJobs(city) {
    const cards = document.querySelectorAll('.hub-job-card');
    const tabs = document.querySelectorAll('.hub-tab-btn');

    tabs.forEach(t => {
        t.classList.remove('active', 'btn-primary');
        t.classList.add('btn-outline-secondary');
    });

    const activeTab = document.getElementById('hub-tab-' + city);
    if (activeTab) {
        activeTab.classList.add('active', 'btn-primary');
        activeTab.classList.remove('btn-outline-secondary');
    }

    cards.forEach(card => {
        const cardCity = (card.getAttribute('data-city') || '').toLowerCase();
        if (city === 'all') {
            card.style.display = 'flex';
        } else if (city === 'bangalore') {
            if (cardCity.includes('bangalore') || cardCity.includes('bengaluru')) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        } else if (city === 'hyderabad') {
            if (cardCity.includes('hyderabad')) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        }
    });
}

// Switch Custom Analysis View Tabs
function switchAnalysisTab(tabName) {
    const tabs = document.querySelectorAll('.analysis-tab-btn');
    const panes = document.querySelectorAll('.analysis-pane');

    tabs.forEach(t => {
        t.classList.remove('active', 'btn-primary');
        t.classList.add('btn-outline-secondary');
    });
    panes.forEach(p => {
        p.style.display = 'none';
    });

    const activeBtn = document.getElementById('btn-tab-' + tabName);
    const activePane = document.getElementById('pane-' + tabName);
    if (activeBtn) {
        activeBtn.classList.add('active', 'btn-primary');
        activeBtn.classList.remove('btn-outline-secondary');
    }
    if (activePane) {
        activePane.style.display = 'block';
    }
}

// Copy JSON to Clipboard
function copyAnalysisJson() {
    const codeEl = document.getElementById('raw-analysis-json');
    if (!codeEl) return;
    navigator.clipboard.writeText(codeEl.textContent.trim()).then(function () {
        const copyBtn = document.getElementById('copy-json-btn');
        if (copyBtn) {
            const originalHtml = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fa-solid fa-check text-success"></i> Copied!';
            setTimeout(function () {
                copyBtn.innerHTML = originalHtml;
            }, 2500);
        }
    }).catch(function (err) {
        console.error('Failed to copy JSON: ', err);
    });
}

// Download JSON file
function downloadAnalysisJson() {
    const codeEl = document.getElementById('raw-analysis-json');
    if (!codeEl) return;
    const blob = new Blob([codeEl.textContent.trim()], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resume_analysis_data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
