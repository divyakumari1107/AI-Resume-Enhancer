/**
 * AI Resume Enhancer & ATS Analyzer - Client Interactions
 */

document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------------------------------------
    // 1. DRAG AND DROP FILE UPLOAD
    // -------------------------------------------------------------
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("resumeFileInput");
    const fileInfo = document.getElementById("selectedFileInfo");
    const fileName = document.getElementById("selectedFileName");
    const fileSize = document.getElementById("selectedFileSize");
    const fileIcon = document.getElementById("fileTypeIcon");
    const removeBtn = document.getElementById("removeFileBtn");
    const submitBtn = document.getElementById("uploadSubmitBtn");
    const uploadForm = document.getElementById("resumeUploadForm");
    const progressContainer = document.getElementById("uploadProgressContainer");
    const progressBar = document.getElementById("uploadProgressBar");

    if (dropZone && fileInput) {
        // Prevent default drag behaviors
        ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop zone when item is dragged over it
        ["dragenter", "dragover"].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add("dragover"), false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove("dragover"), false);
        });

        // Handle dropped files
        dropZone.addEventListener("drop", function (e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelection(files[0]);
            }
        });

        // Click on dropzone opens file dialog
        dropZone.addEventListener("click", function (e) {
            if (e.target !== fileInput && !e.target.closest("button")) {
                fileInput.click();
            }
        });

        // Handle file input change
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                handleFileSelection(fileInput.files[0]);
            }
        });

        // Remove selected file
        if (removeBtn) {
            removeBtn.addEventListener("click", function (e) {
                e.stopPropagation();
                fileInput.value = "";
                if (fileInfo) fileInfo.classList.add("d-none");
                if (submitBtn) submitBtn.disabled = true;
            });
        }

        // Form submission with progress simulation
        if (uploadForm) {
            uploadForm.addEventListener("submit", function () {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing Resume...';
                }
                if (progressContainer) {
                    progressContainer.classList.remove("d-none");
                    let width = 10;
                    const interval = setInterval(function () {
                        if (width >= 90) {
                            clearInterval(interval);
                        } else {
                            width += 15;
                            progressBar.style.width = width + "%";
                            document.getElementById("uploadProgressPercent").innerText = width + "%";
                        }
                    }, 250);
                }
            });
        }
    }

    function handleFileSelection(file) {
        if (!file) return;

        // Validate extension
        const validExtensions = ["pdf", "docx"];
        const ext = file.name.split(".").pop().toLowerCase();

        if (!validExtensions.includes(ext)) {
            alert("Invalid file format. Please upload a .PDF or .DOCX document.");
            fileInput.value = "";
            return;
        }

        // Validate size (16MB limit)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            alert("File is too large. Maximum allowed size is 16MB.");
            fileInput.value = "";
            return;
        }

        // Update UI
        if (fileName) fileName.innerText = file.name;
        if (fileSize) fileSize.innerText = (file.size / 1024).toFixed(1) + " KB";
        
        if (fileIcon) {
            if (ext === "pdf") {
                fileIcon.className = "bi bi-file-earmark-pdf-fill text-danger fs-3";
            } else {
                fileIcon.className = "bi bi-file-earmark-word-fill text-primary fs-3";
            }
        }

        if (fileInfo) fileInfo.classList.remove("d-none");
        if (submitBtn) submitBtn.disabled = false;
    }

    // -------------------------------------------------------------
    // 2. LIVE RESUME BUILDER REAL-TIME PREVIEW SYNC
    // -------------------------------------------------------------
    const inputName = document.getElementById("inputName");
    const inputRole = document.getElementById("inputRole");
    const inputEmail = document.getElementById("inputEmail");
    const inputPhone = document.getElementById("inputPhone");
    const inputLinkedin = document.getElementById("inputLinkedin");
    const inputGithub = document.getElementById("inputGithub");
    const inputSummary = document.getElementById("inputSummary");
    const inputSkills = document.getElementById("inputSkills");
    const inputExperience = document.getElementById("inputExperience");
    const inputProjects = document.getElementById("inputProjects");
    const inputEducation = document.getElementById("inputEducation");
    const inputCertifications = document.getElementById("inputCertifications");

    if (inputName) {
        inputName.addEventListener("input", () => {
            const el = document.getElementById("prevName");
            if (el) el.innerText = inputName.value || "Candidate Name";
        });
    }

    if (inputRole) {
        inputRole.addEventListener("input", () => {
            const el = document.getElementById("prevRole");
            if (el) el.innerText = inputRole.value || "Software Engineering Professional";
        });
    }

    if (inputEmail || inputPhone || inputLinkedin || inputGithub) {
        const updateContact = () => {
            const contactContainer = document.getElementById("prevContact");
            if (!contactContainer) return;

            const parts = [];
            if (inputEmail && inputEmail.value) parts.push(inputEmail.value);
            if (inputPhone && inputPhone.value) parts.push(inputPhone.value);
            if (inputLinkedin && inputLinkedin.value) parts.push(inputLinkedin.value);
            if (inputGithub && inputGithub.value) parts.push(inputGithub.value);

            contactContainer.innerHTML = parts.join(" • ");
        };

        if (inputEmail) inputEmail.addEventListener("input", updateContact);
        if (inputPhone) inputPhone.addEventListener("input", updateContact);
        if (inputLinkedin) inputLinkedin.addEventListener("input", updateContact);
        if (inputGithub) inputGithub.addEventListener("input", updateContact);
    }

    if (inputSummary) {
        inputSummary.addEventListener("input", () => {
            const el = document.getElementById("prevSummary");
            if (el) el.innerText = inputSummary.value;
        });
    }

    if (inputSkills) {
        inputSkills.addEventListener("input", () => {
            const el = document.getElementById("prevSkills");
            if (el) {
                const skillsArr = inputSkills.value.split(",").map(s => s.trim()).filter(Boolean);
                el.innerText = skillsArr.join(" • ");
            }
        });
    }

    if (inputExperience) {
        inputExperience.addEventListener("input", () => {
            const el = document.getElementById("prevExperience");
            if (el) el.innerText = inputExperience.value;
        });
    }

    if (inputProjects) {
        inputProjects.addEventListener("input", () => {
            const el = document.getElementById("prevProjects");
            if (el) el.innerText = inputProjects.value;
        });
    }

    if (inputEducation) {
        inputEducation.addEventListener("input", () => {
            const el = document.getElementById("prevEducation");
            if (el) el.innerText = inputEducation.value;
        });
    }

    if (inputCertifications) {
        inputCertifications.addEventListener("input", () => {
            const el = document.getElementById("prevCertifications");
            if (el) el.innerText = inputCertifications.value;
        });
    }

    // -------------------------------------------------------------
    // 3. AI ENHANCE FORM LOADING OVERLAY
    // -------------------------------------------------------------
    const aiEnhanceForm = document.getElementById("aiEnhanceForm");
    const loadingOverlay = document.getElementById("loadingOverlay");

    if (aiEnhanceForm && loadingOverlay) {
        aiEnhanceForm.addEventListener("submit", function () {
            const titleEl = document.getElementById("loadingTitle");
            const subEl = document.getElementById("loadingSubtitle");
            if (titleEl) titleEl.innerText = "Enhancing with Gemini AI...";
            if (subEl) subEl.innerText = "Applying STAR methodology and active verb optimization";
            loadingOverlay.classList.remove("d-none");
        });
    }
});

// -------------------------------------------------------------
// 4. COPY TO CLIPBOARD HELPER
// -------------------------------------------------------------
function copyToClipboard(elementId, btnElement) {
    const target = document.getElementById(elementId);
    if (!target) return;

    const text = target.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const originalHtml = btnElement.innerHTML;
        btnElement.innerHTML = '<i class="bi bi-check2 text-success me-1"></i>Copied!';
        btnElement.classList.add("btn-success", "text-white");
        btnElement.classList.remove("btn-outline-secondary");

        setTimeout(() => {
            btnElement.innerHTML = originalHtml;
            btnElement.classList.remove("btn-success", "text-white");
            btnElement.classList.add("btn-outline-secondary");
        }, 2000);
    }).catch(err => {
        console.error("Clipboard copy failed: ", err);
    });
}
