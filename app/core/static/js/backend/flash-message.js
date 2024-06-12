document.addEventListener('DOMContentLoaded', function() {
    var flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(function(message) {
        // Show flash message
        message.classList.add('show');

        // Close flash message after 5 seconds
        setTimeout(function() {
            message.classList.remove('show');
        }, 5000); // Adjust the time (in milliseconds) as needed

        // Add event listener to close button
        var closeBtn = message.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.classList.remove('show');
            });
        }
    });
});