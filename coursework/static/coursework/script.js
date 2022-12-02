function deleteFile(element) {
    //
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

    document.addEventListener('click', (event) => {
        // Find what was clicked on
        const element = event.target;

        // For use later
        const id = element.dataset.id;
        const fileRow = document.querySelector(`#uploaded-file-${id}`);
        console.log(fileRow);

        if (element.className === 'delete-file') {
            const result = confirm('Are you sure want to delete?');
            if (result === true) {
                // Delete file from models
                // deleteFile(element);
                // Remove file row in table
                fileRow.remove();
            }
        }
    });
});
