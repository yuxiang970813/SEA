// Bootstrap cliemt side validation script
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

// Disable past datetime
document.getElementsByName('datetime')[0].min = new Date(
    Date.now() - new Date().getTimezoneOffset() * 60000
)
    .toISOString()
    .slice(0, 16);
