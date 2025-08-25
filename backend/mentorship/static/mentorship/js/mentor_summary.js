document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('.mentor-summary-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const menteeId = form.dataset.menteeId;
            const url = window.location.href;  // Post to current page
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    const feedback = form.querySelector('.summary-feedback');
                    if (data.success) {
                        feedback.style.display = 'inline';
                        setTimeout(() => feedback.style.display = 'none', 2000);
                    } else if (data.errors) {
                        alert('Error saving summary: ' + JSON.stringify(data.errors));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An unexpected error occurred.');
                });
        });
    });
});
