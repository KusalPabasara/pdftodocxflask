const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeBtn = document.getElementById('removeBtn');
const convertBtn = document.getElementById('convertBtn');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const message = document.getElementById('message');

let selectedFile = null;

// File upload handlers
browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
removeBtn.addEventListener('click', removeFile);
convertBtn.addEventListener('click', convertFile);

// Drag and drop handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadArea.addEventListener('click', (e) => {
    if (e.target === uploadArea || e.target.parentElement === uploadArea) {
        fileInput.click();
    }
});

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (file.type !== 'application/pdf') {
        showMessage('Please select a PDF file', 'error');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        showMessage('File size must be less than 50MB', 'error');
        return;
    }
    
    selectedFile = file;
    displayFileInfo(file);
}

function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
    convertBtn.disabled = false;
    message.style.display = 'none';
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    convertBtn.disabled = true;
    message.style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function convertFile() {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    // Update UI
    convertBtn.disabled = true;
    convertBtn.querySelector('.btn-text').style.display = 'none';
    convertBtn.querySelector('.spinner').style.display = 'block';
    progressBar.style.display = 'block';
    message.style.display = 'none';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        if (progress <= 90) {
            progressFill.style.width = progress + '%';
        }
    }, 200);
    
    try {
        const response = await fetch('http://localhost:5000/api/convert', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        
        if (!response.ok) {
            throw new Error('Conversion failed');
        }
        
        // Download the converted file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = selectedFile.name.replace('.pdf', '.docx');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showMessage('Conversion successful! Your download will start automatically.', 'success');
        
        // Reset after success
        setTimeout(() => {
            removeFile();
            progressBar.style.display = 'none';
            progressFill.style.width = '0%';
        }, 3000);
        
    } catch (error) {
        clearInterval(progressInterval);
        showMessage('Conversion failed. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        convertBtn.disabled = false;
        convertBtn.querySelector('.btn-text').style.display = 'block';
        convertBtn.querySelector('.spinner').style.display = 'none';
    }
}

function showMessage(text, type) {
    message.textContent = text;
    message.className = 'message ' + type;
    message.style.display = 'block';
}