/* ==========================================================================
   UPLOAD & MATCH SCANNER CONTROLLER
   ========================================================================== */

function toggleResumeSource(source) {
    const existingPanel = document.getElementById('existing-resume-select');
    const newPanel = document.getElementById('new-resume-upload');

    if (source === 'existing') {
        if (existingPanel) existingPanel.style.display = 'block';
        if (newPanel) newPanel.style.display = 'none';
    } else {
        if (existingPanel) existingPanel.style.display = 'none';
        if (newPanel) newPanel.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume_file');
    const fileDetails = document.getElementById('file-details');
    const fileNameDisplay = document.getElementById('file-name-display');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const matchForm = document.getElementById('match-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const loadingSpinner = document.getElementById('loading-spinner');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files.length > 0) {
                handleFileSelect(fileInput.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        if (file) {
            if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
                alert('Please select a valid PDF file.');
                return;
            }
            if (fileNameDisplay) fileNameDisplay.textContent = file.name;
            if (dropZone) dropZone.style.display = 'none';
            if (fileDetails) fileDetails.style.display = 'flex';
        }
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (fileInput) fileInput.value = '';
            if (dropZone) dropZone.style.display = 'block';
            if (fileDetails) fileDetails.style.display = 'none';
        });
    }

    if (matchForm) {
        matchForm.addEventListener('submit', (e) => {
            const radioNew = document.getElementById('radio-new');
            if (radioNew && radioNew.checked && (!fileInput.files || fileInput.files.length === 0)) {
                e.preventDefault();
                alert('Please upload a PDF resume file.');
                return;
            }

            if (submitBtn && btnText && loadingSpinner) {
                submitBtn.disabled = true;
                btnText.textContent = 'ANALYZING RESUME & MATCHING...';
                loadingSpinner.style.display = 'inline-block';
            }
        });
    }
});
