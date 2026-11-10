(() => {
    const input = document.getElementById("image-input");
    const chooseButton = document.getElementById("choose-image");
    const stage = document.getElementById("canvas-stage");
    const prompt = document.getElementById("upload-prompt");
    const image = document.getElementById("editor-image");
    const fileName = document.getElementById("file-name");
    const dimensions = document.getElementById("image-dimensions");
    const form = document.getElementById("editor-form");
    const outputInput = document.getElementById("output-image");
    const filenameInput = document.getElementById("filename");
    const saveButton = document.getElementById("save-image");
    const status = document.getElementById("editor-status");
    const sliders = [...document.querySelectorAll(".editor-sidebar input[type='range'][data-filter]")];
    const filterSelect = document.getElementById("image-filter");
    const resetButton = document.getElementById("reset-image");
    const downloadButton = document.getElementById("download-image");
    const isReturning = form.dataset.returning === "true";
    const returnImageUrl = form.dataset.imageUrl;
    let sourceUrl = null;
    let activeImage = null;
    let saveInProgress = false;

    const getPresetFilter = () => {
        const preset = filterSelect.value;
        if (preset === "normal") {
            return [];
        }
        if (preset === "grayscale") {
            return ["grayscale(100%)"];
        }
        if (preset === "blur") {
            return ["blur(3px)"];
        }
        if (preset === "sharpen") {
            return ["contrast(120%)", "saturate(120%)"];
        }
        if (preset === "smooth") {
            return ["contrast(110%)", "saturate(110%)"];
        }
        if (preset === "detail") {
            return ["contrast(120%)", "brightness(105%)"];
        }
        if (preset === "invert") {
            return ["invert(100%)"];
        }
        if (preset === "mirror") {
            return [];
        }
        return [];
    };

    const updatePreview = () => {
        const presetFilters = getPresetFilter();
        const sliderFilters = sliders.map((slider) =>
            `${slider.dataset.filter}(${slider.value}%)`
        );

        if (filterSelect.value === "mirror") {
            image.style.transform = "scaleX(-1)";
        } else {
            image.style.transform = "none";
        }

        image.style.filter = [...presetFilters, ...sliderFilters].join(" ");

        sliders.forEach((slider) => {
            document.getElementById(`${slider.id}-value`).textContent = `${slider.value}%`;
        });
    };

    const createEditedCanvas = () => {
        const canvas = document.createElement("canvas");
        canvas.width = activeImage.naturalWidth;
        canvas.height = activeImage.naturalHeight;
        const context = canvas.getContext("2d");
        if (!context) {
            throw new Error("Could not prepare the edited image.");
        }

        const presetFilters = getPresetFilter();
        const sliderFilters = sliders.map((slider) =>
            `${slider.dataset.filter}(${slider.value}%)`
        );
        context.filter = [...presetFilters, ...sliderFilters].join(" ");
        if (filterSelect.value === "mirror") {
            context.translate(canvas.width, 0);
            context.scale(-1, 1);
        }
        context.drawImage(activeImage, 0, 0);
        return canvas;
    };

    const canvasToBlob = (canvas, type, quality) => new Promise((resolve, reject) => {
        canvas.toBlob((blob) => {
            if (blob) {
                resolve(blob);
            } else {
                reject(new Error("Could not encode the edited image."));
            }
        }, type, quality);
    });

    const setImageAvailable = (available) => {
        sliders.forEach((slider) => { slider.disabled = !available; });
        filterSelect.disabled = !available;
        resetButton.disabled = !available;
        saveButton.disabled = !available;
        downloadButton.disabled = !available;
    };

    const loadFile = (file) => {
        if (!file) {
            return;
        }
        if (!file.type.startsWith("image/")) {
            fileName.textContent = "Please choose a valid image file.";
            return;
        }

        if (sourceUrl) {
            URL.revokeObjectURL(sourceUrl);
        }
        activeImage = null;
        setImageAvailable(false);
        const objectUrl = URL.createObjectURL(file);
        sourceUrl = objectUrl;
        activeImage = new Image();
        activeImage.onload = () => {
            if (sourceUrl !== objectUrl) {
                URL.revokeObjectURL(objectUrl);
                return;
            }
            image.src = objectUrl;
            image.style.display = "block";
            prompt.style.display = "none";
            fileName.textContent = file.name;
            fileName.title = file.name;
            dimensions.textContent = `${activeImage.naturalWidth} × ${activeImage.naturalHeight}`;
            setImageAvailable(true);
            status.textContent = "";
            updatePreview();
        };
        activeImage.onerror = () => {
            if (sourceUrl === objectUrl) {
                URL.revokeObjectURL(objectUrl);
                sourceUrl = null;
                activeImage = null;
                fileName.textContent = "Could not load this image.";
                status.textContent = "Could not load this image. Please choose another file.";
                setImageAvailable(false);
            }
        };
        activeImage.src = objectUrl;
    };

    chooseButton.addEventListener("click", () => input.click());
    input.addEventListener("change", () => loadFile(input.files[0]));

    ["dragenter", "dragover"].forEach((eventName) => {
        stage.addEventListener(eventName, (event) => {
            event.preventDefault();
            stage.classList.add("is-dragging");
        });
    });
    ["dragleave", "drop"].forEach((eventName) => {
        stage.addEventListener(eventName, (event) => {
            event.preventDefault();
            stage.classList.remove("is-dragging");
        });
    });
    stage.addEventListener("drop", (event) => {
        const file = event.dataTransfer.files[0];
        if (!file) {
            return;
        }

        const transfer = new DataTransfer();
        transfer.items.add(file);
        input.files = transfer.files;
        loadFile(file);
    });

    sliders.forEach((slider) => slider.addEventListener("input", updatePreview));
    filterSelect.addEventListener("change", updatePreview);

    resetButton.addEventListener("click", () => {
        sliders.forEach((slider) => {
            slider.value = "100";
        });
        filterSelect.value = "normal";
        updatePreview();
    });

    downloadButton.addEventListener("click", async () => {
        if (!activeImage) {
            return;
        }
        try {
            const canvas = createEditedCanvas();
            const blob = await canvasToBlob(canvas, "image/png");
            const downloadUrl = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = downloadUrl;
            link.download = `edited-${fileName.textContent.replace(/[^\w.-]/g, "_")}`;
            link.click();
            window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
        } catch (error) {
            status.textContent = error.message;
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!activeImage || saveInProgress) {
            return;
        }

        const filename = filenameInput.value.trim();
        if (!filename) {
            filenameInput.setCustomValidity("Please provide a filename.");
            filenameInput.reportValidity();
            return;
        }
        if (/\.[^./\\]+$/.test(filename)) {
            filenameInput.setCustomValidity("Enter a filename without an extension.");
            filenameInput.reportValidity();
            return;
        }
        filenameInput.setCustomValidity("");
        filenameInput.value = filename;
        saveInProgress = true;
        saveButton.disabled = true;

        try {
            const blob = await canvasToBlob(createEditedCanvas(), "image/jpeg", 0.92);
            const transfer = new DataTransfer();
            transfer.items.add(new File([blob], `${filename}.jpg`, { type: "image/jpeg" }));
            outputInput.files = transfer.files;
            HTMLFormElement.prototype.submit.call(form);
        } catch (error) {
            status.textContent = error.message;
            saveInProgress = false;
            saveButton.disabled = false;
        }
    });

    filenameInput.addEventListener("input", () => {
        filenameInput.setCustomValidity("");
    });

    if (isReturning) {
        fetch(returnImageUrl).then((response) => {
            if (!response.ok) {
                throw new Error("The image could not be restored. Please choose it again.");
            }
            return response.blob();
        }).then((blob) => {
            const filename = form.dataset.filename;
            filenameInput.value = filename;
            loadFile(new File([blob], `${filename || "edited-image"}.jpg`, { type: "image/jpeg" }));
        }).catch((error) => {
            status.textContent = error.message;
        });
    }

    window.addEventListener("pageshow", (event) => {
        if (event.persisted) {
            saveInProgress = false;
            setImageAvailable(Boolean(activeImage));
        }
    });

    window.addEventListener("pagehide", () => {
        if (saveInProgress) {
            return;
        }

        if (sourceUrl) {
            URL.revokeObjectURL(sourceUrl);
            sourceUrl = null;
        }

        activeImage = null;
        image.removeAttribute("src");
        image.style.display = "none";
        prompt.style.display = "";
        input.value = "";
        outputInput.value = "";
        filenameInput.value = "";
        fileName.textContent = "No image selected";
        fileName.removeAttribute("title");
        dimensions.textContent = "";
        setImageAvailable(false);
    });
})();
