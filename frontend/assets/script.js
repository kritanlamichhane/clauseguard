document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectedFileBadge = document.getElementById('selected-file-badge');
    const fileNameText = document.getElementById('file-name-text');
    const fileSizeText = document.getElementById('file-size-text');
    const clearFileBtn = document.getElementById('clear-file-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeSpinner = document.getElementById('analyze-spinner');
    const btnText = document.getElementById('btn-text');
    const pasteText = document.getElementById('paste-text');

    let selectedFile = null;

    if (!analyzeBtn) return;

    // Activate button when there's content
    function checkActive() {
        const hasFile = !!selectedFile;
        const hasText = pasteText && pasteText.value.trim().length > 0;
        if (hasFile || hasText) {
            analyzeBtn.disabled = false;
            analyzeBtn.classList.add('active');
        } else {
            analyzeBtn.disabled = true;
            analyzeBtn.classList.remove('active');
        }
    }

    if (pasteText) {
        pasteText.addEventListener('input', checkActive);
    }

    // File browser trigger
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') fileInput.click();
    });

    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    function handleFileSelect(file) {
        if (!file) return;
        selectedFile = file;
        fileNameText.textContent = file.name;
        fileSizeText.textContent = formatBytes(file.size);
        dropZone.style.display = 'none';
        selectedFileBadge.style.display = 'flex';
        checkActive();
    }

    function clearSelectedFile() {
        selectedFile = null;
        fileInput.value = '';
        selectedFileBadge.style.display = 'none';
        dropZone.style.display = 'flex';
        checkActive();
    }

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    clearFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearSelectedFile();
    });

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(evt => {
        dropZone.addEventListener(evt, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(evt => {
        dropZone.addEventListener(evt, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (evt === 'drop' && e.dataTransfer.files.length) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        }, false);
    });

    // Loading messages
    const loadingMessages = [
        "Uploading document...",
        "Extracting text...",
        "Segmenting clauses...",
        "Extracting entities...",
        "Classifying clauses...",
        "Scoring risks...",
        "Building report..."
    ];

    analyzeBtn.addEventListener('click', async () => {
        const pastedText = pasteText ? pasteText.value.trim() : '';

        if (!selectedFile && !pastedText) {
            alert("Please upload a file or paste contract text first.");
            return;
        }

        const formData = new FormData();
        if (selectedFile) {
            formData.append("file", selectedFile);
        } else {
            const textBlob = new Blob([pastedText], { type: 'text/plain' });
            formData.append("file", textBlob, "pasted_contract.txt");
        }

        analyzeBtn.disabled = true;
        analyzeBtn.classList.remove('active');
        analyzeSpinner.style.display = 'block';

        let msgIndex = 0;
        btnText.textContent = loadingMessages[msgIndex];

        const messageInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % loadingMessages.length;
            btnText.textContent = loadingMessages[msgIndex];
        }, 1200);

        try {
            const response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }

            const data = await response.json();
            sessionStorage.setItem("riskReport", JSON.stringify(data));
            window.location.href = "report.html";
        } catch (err) {
            console.error(err);
            alert("Analysis failed. Make sure the backend server is running on port 8000.");
            clearInterval(messageInterval);
            analyzeSpinner.style.display = 'none';
            btnText.textContent = "Analyze";
            checkActive();
        }
    });
});
