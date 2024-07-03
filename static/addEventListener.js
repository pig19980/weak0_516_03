// code editor part
var editor = CodeMirror.fromTextArea(document.getElementById("upload-code"), {
    lineNumbers: false,
    mode: "javascript"
}).setSize(null, 300);


// modal part
document.addEventListener('DOMContentLoaded', () => {
    // Functions to open and close a modal
    function openModal($el) {
        $el.classList.add('is-active');
    }

    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    function closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(($modal) => {
            closeModal($modal);
        });
    }

    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
        const modal = $trigger.dataset.target;
        const $target = document.getElementById(modal);
        console.log(modal)

        $trigger.addEventListener('click', () => {
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeAllModals();
        }
    });
});

// image upload part
const fileInput = document.querySelector("#file-js-upload input[type=file]");
console.log(fileInput.files);
fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const fileName = $("#file-js-upload .file-name");
        const newImg = $("#modal-js-writing > div.modal-card > section > figure");
        fileName.text(file.name);

        newImg.find("img").attr("src", URL.createObjectURL(file)).attr("id", "before-uploading");

        newImg.append(
            `<button class="delete" aria-label="close" onclick="cancleUpload()"></button>`
        )
        // const newCloseButton = document.createElement("button");
        // newCloseButton.classList.add("delete");
        // newCloseButton.setAttribute("aria-label", "close");
        // newImg.appendChild(newCloseButton);

    }
};

