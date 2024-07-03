// code editor part
let editor = CodeMirror.fromTextArea(document.getElementById("upload-code"), {
    lineNumbers: false,
    mode: "javascript"
});
editor.setSize(null, 300);

let modify_editors = {};
(document.querySelectorAll('.modify-code') || []).forEach(($textarea) => {
    let temp_editor = CodeMirror.fromTextArea($textarea, {
        lineNumbers: false,
        mode: "javascript"
    });
    temp_editor.setSize(null, 300);
    modify_editors[$textarea.dataset.targetid] = temp_editor;
});


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
const fileInput = $("#file-js-upload input[type=file]")[0];
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
    }
};

// modifying
const fileChanges = $('.js-modify input[type=file]');
fileChanges.each((index, $fileChange) => {
    const filechange = $fileChange;
    filechange.onchange = () => {
        if (filechange.files.length > 0) {
            const file = filechange.files[0];
            const target_id = filechange.dataset.targetid;
            const fileName = $(`#file-js-modify-${target_id} .file-name`);
            const newImg = $(`#modal-js-modify-${target_id} > div.modal-card > section > figure`);
            fileName.text(file.name);
    
            newImg.find("img").attr("src", URL.createObjectURL(file)).attr("id", "before-uploading");
    
            newImg.append(
                `<button class="delete" aria-label="close" onclick="cancleModify('${target_id}')"></button>`
            )
            console.log(target_id);
        }
    }

});
console.log(fileChanges);