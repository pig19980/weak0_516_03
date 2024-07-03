// code editor part
var editor = CodeMirror.fromTextArea(document.getElementById("upload-code"), {
    lineNumbers: false,
    mode: "javascript"
});
editor.setSize(null, 300);

var modify_editors = {};
(document.querySelectorAll('.modify-code') || []).forEach(($textarea) => {
    var temp_editor = CodeMirror.fromTextArea($textarea, {
        lineNumbers: false,
        mode: "javascript"
    });
    temp_editor.setSize(null, 300);
    console.log(temp_editor);
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
        var modal = $trigger.dataset.target;
        var $target = document.getElementById(modal);

        $trigger.addEventListener('click', () => {
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
        var $target = $close.closest('.modal');

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
var fileUpload = $("#file-js-upload input[type=file]")[0];
fileUpload.onchange = () => {
    if (fileUpload.files.length > 0) {
        var file = fileUpload.files[0];
        var fileName = $("#file-js-upload .file-name");
        var newImg = $("#modal-js-writing > div.modal-card > section > figure");
        fileName.text(file.name);


        newImg.find("img").attr("src", URL.createObjectURL(file)).attr("id", "before-uploading");

        newImg.append(
            `<button class="delete" aria-label="close" onclick="cancleUpload()"></button>`
        )
    }
};

// modifying
var fileChanges = $('.js-modify input[type=file]');
fileChanges.each((index, $fileChange) => {
    var filechange = $fileChange;
    filechange.onchange = () => {
        if (filechange.files.length > 0) {
            var file = filechange.files[0];
            var target_id = filechange.dataset.targetid;
            var fileName = $(`#file-js-modify-${target_id} .file-name`);
            var newImg = $(`#modal-js-modify-${target_id} > div.modal-card > section > figure`);
            fileName.text(file.name);
    
            newImg.find("img").attr("src", URL.createObjectURL(file)).attr("id", `modify-img-${target_id}`);
    
            newImg.append(
                `<button class="delete" aria-label="close" onclick="CancleModify('${target_id}')"></button>`
            )
        }
    }

});