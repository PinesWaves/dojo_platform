/*************************** MODAL - PROFILE PIC ***************************/
// This code handles the modal for uploading a new profile picture
// Make sure to include Bootstrap's JS in your HTML file before this script
// <script src="/static/plugins/bootstrap-5.3.1/js/bootstrap.bundle.min.js"></script>
// Modal html location: templates/dashboard/common/profile_modal.html
$(document).ready(function () {
    $('#profile-pic-input').on('change', function () {
        const [file] = this.files;
        if (file) {
            $('#preview-pic').attr('src', URL.createObjectURL(file));
            $(this).next('.custom-file-label').text(file.name);
        }
    });

    // Clean the modal when closing
    $('#modal-profile-pic').on('hidden.bs.modal', function () {
        $('#profile-pic-input').val('');
        $('#delete-pic').prop('checked', false);
        $('.custom-file-label').text('Select picture');
    });
});


/*************************** PROFILE PIC CROPPER (IN MODAL PROFILE PIC) ***************************/
// This code uses the Cropper.js library to allow users to crop their profile picture before uploading
// Make sure to include Cropper.js in your HTML file before this script
// <script src="/static/plugins/cropperjs-v1.6.2/js/cropper.min.js' %}" rel="stylesheet"></script>
// <link  rel="stylesheet" href="/static/plugins/cropperjs-v1.6.2/css/cropper.min.css">
let cropper;
const image = document.getElementById('preview-pic');
const input = document.getElementById('profile-pic-input');

input.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    image.src = url;

    if (cropper) cropper.destroy();
    cropper = new Cropper(image, {
        aspectRatio: 1,
        viewMode: 1,
        autoCropArea: 1
    });

    document.querySelector('.custom-file-label').innerText = file.name;
});

// When submitting the form, we replace the image with the cropped one.
document.getElementById('form-profile-pic').addEventListener('submit', function (e) {
    if (cropper) {
        e.preventDefault();

        cropper.getCroppedCanvas().toBlob(blob => {
            const formData = new FormData(this);
            formData.set('picture', blob, 'avatar.png');

            fetch(this.action, {
                method: 'POST',
                body: formData
            }).then(resp => {
                if (resp.ok) {
                    window.location.reload();
                } else {
                    alert("An error occurred while uploading the pic.");
                }
            });
        });
    }
});
