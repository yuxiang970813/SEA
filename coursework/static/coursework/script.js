function deleteFile(file_id, filename) {
    // Make sure user really want delete file
    const result = confirm(`Are you sure want to delete ${filename}?`);
    if (result === true) {
        // Request delete file api
        fetch('/delete/file', {
            method: 'POST',
            body: JSON.stringify({
                file_id: file_id,
            }),
        })
            .then((response) => response.json())
            .then((result) => {
                if (result.error) {
                    alert(result.error);
                } else if (result.message) {
                    alert(result.message);
                    // Remove file row
                    document
                        .getElementById(`uploaded-file-${file_id}`)
                        .remove();
                }
            });
    }
}

function editMemo(assignmentStatusId) {
    // Search for the memo textarea
    const newMemo = document.getElementById('edit-memo').value;
    // Request edit memo api
    fetch('/edit/memo', {
        method: 'POST',
        body: JSON.stringify({
            assignmentStatusId: assignmentStatusId,
            newMemo: newMemo,
        }),
    })
        .then((response) => response.json())
        .then((result) => {
            if (result.error) {
                alert(result.error);
            } else if (result.message) {
                alert(result.message);
                location.replace('/');
            }
        });
}

function declineRequest(courseworkRequestId) {
    console.log(`Decline ${courseworkRequestId}`);
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
