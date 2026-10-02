document.addEventListener('DOMContentLoaded', function() {
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
        // Trigger file browser when clicking drop zone
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });

        // Dragover styling
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, function(e) {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function(e) {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });

        // Handle File Drop
        dropZone.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelection(files[0]);
            }
        });

        // Handle File Input Change
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                handleFileSelection(fileInput.files[0]);
            }
        });

        // Remove File
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                fileInput.value = '';
                fileDetails.style.display = 'none';
                dropZone.style.display = 'block';
            });
        }
    }

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('Please select a valid PDF document (.pdf)');
            fileInput.value = '';
            return;
        }
        
        // 16MB file size check
        if (file.size > 16 * 1024 * 1024) {
            alert('File size exceeds the 16MB limit. Please choose a smaller file.');
            fileInput.value = '';
            return;
        }

        fileNameDisplay.textContent = file.name + ' (' + (file.size / (1024 * 1024)).toFixed(2) + ' MB)';
        dropZone.style.display = 'none';
        fileDetails.style.display = 'flex';
    }

    // Form Submit Loading State
    if (matchForm) {
        matchForm.addEventListener('submit', function(e) {
            const jobDesc = document.getElementById('job_description').value.trim();
            if (!jobDesc) {
                alert('Please enter or paste the target job description.');
                e.preventDefault();
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                if (btnText) btnText.textContent = 'ANALYZING RESUME & MATCHING...';
                if (loadingSpinner) loadingSpinner.style.display = 'inline-block';
            }
        });
    }
});

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
