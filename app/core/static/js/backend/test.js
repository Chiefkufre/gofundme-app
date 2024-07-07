document.addEventListener('DOMContentLoaded', function() {
    const loader = document.createElement('div');
    loader.classList.add('loader'); // Ensure you have styles for this loader
    loader.innerHTML = '<div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div>';

    function showToast(message, isSuccess = true) {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white ${isSuccess ? 'bg-success' : 'bg-danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    document.querySelectorAll('.publish-campaign-form').forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const button = this.querySelector('button');
            const span = button.querySelector('span'); 
            button.disabled = true;
            this.appendChild(loader);

            const formData = new FormData(this);
            console.log(this.action)
            console.log(formData)

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, data.success);
                if (data.success) {
                    if (data.is_publish) {
                        span.textContent = 'Pause campaign';
                        form.querySelector('input[name="is_publish"]').value = 'false';
                        // button.querySelector('em').classList.replace('ni-check-round-cut', 'ni-pause');
                    } else {
                        span.textContent = 'Publish campaign';
                        form.querySelector('input[name="is_publish"]').value = 'true';
                        // button.querySelector('em').classList.replace('ni-pause', 'ni-check-round-cut');
                    }
                }
            })
            .catch(error => showToast('Error occurred: ' + error, false))
            .finally(() => {
                button.disabled = false;
                loader.remove();
            });
        });
    });

    document.querySelectorAll('.delete-campaign-form').forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const button = this.querySelector('button');
            button.disabled = true;
            this.appendChild(loader);

            fetch(this.action, {
                method: 'DELETE',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, data.success);
                if (data.success) {
                    // Remove the item from the DOM
                    this.closest('.campaign-item').remove();
                }
            })
            .catch(error => showToast('Error occurred: ' + error, false))
            .finally(() => {
                button.disabled = false;
                loader.remove();
            });
        });
    });


    // function fetchNotification(){
    //     fetch()
    // }

    document.querySelectorAll('.delete-notification').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const notificationId = this.getAttribute('data-id');
            const notificationItem = this.closest('.nk-notification-item');
            
            fetch(`/notification/${notificationId}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, true);
                    if (notificationItem) notificationItem.remove();
                } else {
                    showToast(data.message, false);
                }
            })
            .catch(error => showToast('Error occurred: ' + error, false));
        });
    });
});
