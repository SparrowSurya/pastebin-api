/**
 * Pastebin SPA Frontend Controller
 * Powered by pure Vanilla Javascript.
 */

// Application state
const state = {
    files: [], // Array of file elements
    fileCounter: 0,
    currentPasteFiles: [] // Array of { name, text, kind } for viewer
};

// UI Elements
const creatorView = document.getElementById("creator-view");
const viewerView = document.getElementById("viewer-view");
const filesListContainer = document.getElementById("files-list");
const viewerFilesList = document.getElementById("viewer-files-list");
const addFileBtn = document.getElementById("add-file-btn");
const submitBtn = document.getElementById("submit-btn");
const pasteForm = document.getElementById("paste-form");
const expirySelect = document.getElementById("paste-expiry");
const newPasteBtn = document.getElementById("new-paste-btn");
const downloadAllBtn = document.getElementById("download-all-btn");
const toast = document.getElementById("toast");

// Supported syntax languages
const SUPPORTED_LANGUAGES = [
    { value: "text", label: "Plain Text" },
    { value: "python", label: "Python" },
    { value: "javascript", label: "JavaScript" },
    { value: "json", label: "JSON" },
    { value: "html", label: "HTML" },
    { value: "css", label: "CSS" },
    { value: "sql", label: "SQL" },
    { value: "markdown", label: "Markdown" },
    { value: "cpp", label: "C++" }
];

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
    // Event listeners
    addFileBtn.addEventListener("click", () => addFileField());
    submitBtn.addEventListener("click", createPaste);
    newPasteBtn.addEventListener("click", resetToCreator);
    downloadAllBtn.addEventListener("click", downloadAllFiles);
    
    // SPA Routing hooks
    window.addEventListener("hashchange", handleRouting);
    
    // Initial run
    handleRouting();
});

// Toast notification helper
function showToast(message, isError = false) {
    toast.textContent = message;
    toast.style.borderColor = isError ? "var(--danger)" : "var(--card-border)";
    toast.classList.add("show");
    
    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

// Router handler
function handleRouting() {
    const hash = window.location.hash.substring(1);
    
    if (hash && hash.length === 4) {
        // Fetch and show existing paste
        loadPaste(hash);
    } else {
        // Show creation panel
        showCreator();
    }
}

// Show creator view
function showCreator() {
    creatorView.classList.add("active");
    viewerView.classList.remove("active");
    
    // Reset file form if empty
    filesListContainer.innerHTML = "";
    state.files = [];
    state.fileCounter = 0;
    addFileField(); // Add default first file
}

// Show viewer view
function showViewer() {
    viewerView.classList.add("active");
    creatorView.classList.remove("active");
}

// Reset view back to creator
function resetToCreator() {
    window.location.hash = "";
}

// Add a file input field to the DOM dynamically
function addFileField(nameVal = "", kindVal = "text", textVal = "") {
    state.fileCounter++;
    const fileId = `file-${state.fileCounter}`;
    
    const fileItem = document.createElement("div");
    fileItem.className = "file-item card-panel";
    fileItem.id = fileId;
    
    // Options HTML for language selector
    const optionsHtml = SUPPORTED_LANGUAGES.map(lang => 
        `<option value="${lang.value}" ${lang.value === kindVal ? 'selected' : ''}>${lang.label}</option>`
    ).join('');
    
    fileItem.innerHTML = `
        <div class="file-header-input">
            <i class="fa-regular fa-file-code" style="color: var(--text-muted);"></i>
            <input type="text" class="form-input file-name" placeholder="filename.txt (e.g. script.py)" value="${escapeHtml(nameVal)}" required>
            <select class="form-select form-select-sm file-kind">
                <option value="">Auto-detect</option>
                ${optionsHtml}
            </select>
            <button type="button" class="btn-remove" title="Remove File">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </div>
        <div class="code-editor-wrapper">
            <textarea class="code-textarea file-text" placeholder="Paste or write your code snippet here..." required>${escapeHtml(textVal)}</textarea>
        </div>
    `;
    
    // Delete file handler
    const removeBtn = fileItem.querySelector(".btn-remove");
    removeBtn.addEventListener("click", () => removeFileField(fileId));
    
    // Code textarea indentation handler (support Tab key)
    const textarea = fileItem.querySelector(".file-text");
    textarea.addEventListener("keydown", (e) => {
        if (e.key === "Tab") {
            e.preventDefault();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            textarea.value = textarea.value.substring(0, start) + "    " + textarea.value.substring(end);
            textarea.selectionStart = textarea.selectionEnd = start + 4;
        }
    });

    filesListContainer.appendChild(fileItem);
    state.files.push({ id: fileId, element: fileItem });
    
    // Update delete buttons state (disable if only 1 file)
    updateDeleteButtonsVisibility();
}

// Remove file block
function removeFileField(fileId) {
    if (state.files.length <= 1) {
        return;
    }
    
    const fileIndex = state.files.findIndex(f => f.id === fileId);
    if (fileIndex !== -1) {
        const fileObj = state.files[fileIndex];
        fileObj.element.style.animation = "slideIn 0.2s ease-out reverse";
        
        setTimeout(() => {
            fileObj.element.remove();
            state.files.splice(fileIndex, 1);
            updateDeleteButtonsVisibility();
        }, 180);
    }
}

// Enable/disable trash button based on file count
function updateDeleteButtonsVisibility() {
    const isSingle = state.files.length <= 1;
    state.files.forEach(f => {
        const btn = f.element.querySelector(".btn-remove");
        btn.style.opacity = isSingle ? "0.3" : "1";
        btn.style.cursor = isSingle ? "not-allowed" : "pointer";
    });
}

// Create Paste AJAX Request (Standard fetch-based pure Javascript)
function createPaste() {
    // Validate form inputs
    const fileItems = filesListContainer.querySelectorAll(".file-item");
    const filesData = [];
    let isValid = true;
    
    fileItems.forEach(item => {
        const nameInput = item.querySelector(".file-name");
        const kindSelect = item.querySelector(".file-kind");
        const textTextarea = item.querySelector(".file-text");
        
        const name = nameInput.value.trim();
        const kind = kindSelect.value;
        const text = textTextarea.value;
        
        if (!text.trim()) {
            textTextarea.focus();
            isValid = false;
        }
        
        filesData.push({
            name: name,
            kind: kind,
            text: text
        });
    });
    
    if (!isValid) {
        showToast("Please provide content for all files.", true);
        return;
    }
    
    const expiry = parseInt(expirySelect.value);
    
    // Loader state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin icon-spaced"></i>Creating...`;
    
    // Standard Fetch API call
    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            files: filesData,
            expiry: expiry
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server returned an error");
        }
        return response.json();
    })
    .then(key => {
        // Redirect to View view using hash
        window.location.hash = `#${key}`;
        showToast("Paste created successfully!");
    })
    .catch(error => {
        console.error("API Error:", error);
        showToast("Failed to create paste. Try again.", true);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-paper-plane icon-spaced"></i>Create Paste`;
    });
}

// Load Paste details from API (Standard fetch-based pure Javascript)
function loadPaste(key) {
    viewerFilesList.innerHTML = `<div class="card-panel text-center" style="color: var(--text-muted);">
        <i class="fa-solid fa-spinner fa-spin icon-spaced"></i>Loading paste data...
    </div>`;
    showViewer();
    
    fetch(`/${key}`)
    .then(response => {
        if (response.status === 404) {
            throw new Error("Paste not found or has expired");
        }
        if (!response.ok) {
            throw new Error("Server error");
        }
        return response.json();
    })
    .then(pasteData => {
        renderPaste(pasteData);
    })
    .catch(error => {
        console.error("Load Error:", error);
        viewerFilesList.innerHTML = `
            <div class="card-panel text-center" style="border-color: var(--danger);">
                <i class="fa-solid fa-triangle-exclamation icon-spaced" style="color: var(--danger);"></i>
                <p style="margin-top: 0.5rem;">${error.message}</p>
                <button onclick="resetToCreator()" class="btn btn-secondary" style="margin: 1rem auto 0;">Back to Creator</button>
            </div>
        `;
    });
}

// Render retrieved Paste onto the screen
function renderPaste(pasteData) {
    viewerFilesList.innerHTML = "";
    
    // Save current files for downloading all
    state.currentPasteFiles = pasteData.files;
    
    // Configure Prism autoloader languages path
    if (window.Prism && window.Prism.plugins && window.Prism.plugins.autoloader) {
        window.Prism.plugins.autoloader.languages_path = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/';
    }
    
    // Render files
    pasteData.files.forEach((file, index) => {
        const fileCard = document.createElement("div");
        fileCard.className = "viewer-file-card card-panel";
        
        // Display filename or fallback placeholder
        const hasName = file.name && file.name.trim().length > 0;
        const displayName = hasName ? file.name.trim() : "";
        const codeId = `code-block-${index}`;
        
        fileCard.innerHTML = `
            <div class="viewer-file-header" style="${hasName ? '' : 'justify-content: flex-end;'}">
                ${hasName ? `
                <div class="viewer-file-title">
                    <i class="fa-regular fa-file-lines" style="color: var(--primary-color);"></i>
                    <span>${escapeHtml(displayName)}</span>
                </div>
                ` : ''}
                <div class="viewer-file-actions">
                    <button class="action-icon-btn copy-btn" data-target="${codeId}" title="Copy Code">
                        <i class="fa-regular fa-copy"></i>
                    </button>
                    <button class="action-icon-btn download-btn" title="Download File">
                        <i class="fa-solid fa-download"></i>
                    </button>
                </div>
            </div>
            <div class="code-render-box">
                <pre class="language-${escapeHtml(file.kind || 'text')}"><code id="${codeId}" class="language-${escapeHtml(file.kind || 'text')}">${escapeHtml(file.text)}</code></pre>
            </div>
        `;
        
        // Wire up copy button
        const copyBtn = fileCard.querySelector(".copy-btn");
        copyBtn.addEventListener("click", () => copyCodeText(copyBtn, file.text));
        
        // Wire up download button
        const downloadBtn = fileCard.querySelector(".download-btn");
        downloadBtn.addEventListener("click", () => downloadFile(displayName || `unnamed_snippet_${index + 1}.txt`, file.text));
        
        viewerFilesList.appendChild(fileCard);
    });

    // Trigger Prism highlighting on rendered code blocks
    if (window.Prism) {
        window.Prism.highlightAll();
    }
}

// Copy button implementation
function copyCodeText(button, text) {
    navigator.clipboard.writeText(text)
    .then(() => {
        const originalContent = button.innerHTML;
        button.innerHTML = `<i class="fa-solid fa-check" style="color: var(--success);"></i>`;
        button.disabled = true;
        
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.disabled = false;
        }, 2000);
    })
    .catch(err => {
        console.error("Clipboard Copy Failed:", err);
        showToast("Copy failed.", true);
    });
}

// Download single file helper
function downloadFile(filename, text) {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Download all files helper
function downloadAllFiles() {
    if (!state.currentPasteFiles || state.currentPasteFiles.length === 0) {
        showToast("No files to download", true);
        return;
    }
    
    const key = window.location.hash.substring(1) || "code";
    
    if (state.currentPasteFiles.length === 1) {
        // Only one file - download directly
        const file = state.currentPasteFiles[0];
        const displayName = file.name ? file.name : `unnamed_snippet_1.txt`;
        downloadFile(displayName, file.text);
    } else {
        // Multiple files - zip them
        if (typeof JSZip === "undefined") {
            showToast("Zip library loading...", true);
            return;
        }
        
        const zip = new JSZip();
        const nameCount = {};
        
        state.currentPasteFiles.forEach((file, index) => {
            let displayName = file.name ? file.name.trim() : "";
            if (!displayName) {
                displayName = `unnamed_snippet_${index + 1}.txt`;
            }
            
            // Deduplicate filenames if needed
            if (nameCount[displayName]) {
                const parts = displayName.split(".");
                if (parts.length > 1) {
                    const ext = parts.pop();
                    displayName = `${parts.join(".")}_(${nameCount[displayName]}).${ext}`;
                } else {
                    displayName = `${displayName}_(${nameCount[displayName]})`;
                }
                nameCount[displayName]++;
            } else {
                nameCount[displayName] = 1;
            }
            
            zip.file(displayName, file.text);
        });
        
        zip.generateAsync({ type: "blob" })
        .then((content) => {
            const url = URL.createObjectURL(content);
            const a = document.createElement("a");
            a.href = url;
            a.download = `paste-${key}.zip`;
            a.click();
            URL.revokeObjectURL(url);
        })
        .catch((err) => {
            console.error("Zipping Failed:", err);
            showToast("Failed to create zip file.", true);
        });
    }
}

// Helper: Escape HTML string to prevent script injections
function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}