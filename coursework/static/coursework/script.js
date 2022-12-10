function deleteFile(file_id, filename) {
    // Make sure user really want delete file
    const result = confirm(`Are you sure want to delete ${filename}?`);
    if (result === true) {
        // Request delete file API
        fetch('/delete/file', {
            method: 'POST',
            body: JSON.stringify({
                file_id: file_id,
            }),
        })
            .then((response) => response.json())
            .then((result) => {
                // Alert error if error
                if (result.error) {
                    alert(result.error);
                }
                // Alert message & remove file row if success
                else if (result.message) {
                    alert(result.message);
                    document
                        .getElementById(`uploaded-file-${file_id}`)
                        .remove();
                }
            });
    }
}

function editMemo(assignmentStatusId) {
    // Search for the memo value
    const newMemo = document.getElementById('edit-memo').value;
    // Request edit memo API
    fetch('/edit/memo', {
        method: 'POST',
        body: JSON.stringify({
            assignmentStatusId: assignmentStatusId,
            newMemo: newMemo,
        }),
    })
        .then((response) => response.json())
        .then((result) => {
            // Alert error if error
            if (result.error) {
                alert(result.error);
            }
            // Alert message & redirect to index if success
            else if (result.message) {
                alert(result.message);
                location.replace('/');
            }
        });
}

function formSubmit() {
    // For use later
    const addButton = document.getElementById('label-upload');
    const spinner = document.getElementById('spinner');
    // Hide add button & show spinner
    addButton.classList.add('d-none');
    spinner.classList.remove('d-none');
    // Create and fill in form
    const formData = new FormData();
    formData.append('studentId', document.getElementById('student-id').value);
    formData.append(
        'assignmentId',
        document.getElementById('assignment-id').value
    );
    formData.append('file', document.getElementById('upload-file').files[0]);
    // Request upload file API
    fetch('/upload/file', {
        method: 'POST',
        body: formData,
    })
        .then((response) => response.json())
        .then((result) => {
            // Show add button & hide spinner
            addButton.classList.remove('d-none');
            spinner.classList.add('d-none');
            // Alert result
            if (result.error) {
                alert(result.error);
            } else if (result.message) {
                alert(result.message);
            }
            // Refresh page
            location.reload();
        });
}

document.addEventListener('DOMContentLoaded', () => {
    // Bootstrap client side validation function
    (function () {
        'use strict';
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.querySelectorAll('.needs-validation');
        // Loop over them and prevent submission
        Array.prototype.slice.call(forms).forEach(function (form) {
            form.addEventListener(
                'submit',
                function (event) {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                },
                false
            );
        });
    })();
});
