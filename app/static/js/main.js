document.addEventListener('DOMContentLoaded', () => {
    // 1. Alert Fade Logic: Fades out flash messages after 5 seconds
    const alerts = document.querySelectorAll('.neo-alert');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.transition = 'opacity 1s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 1000); // Remove from DOM after fade
            }, 5000);
        });
    }

    // 2. Password Match Validation: Prevents form submission if passwords don't match
    const signupForm = document.querySelector('form[action*="register"]');
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            const p1 = signupForm.querySelector('input[name="password"]').value;
            const p2 = signupForm.querySelector('input[name="confirm_password"]').value;
            
            if (p1 !== p2) {
                e.preventDefault(); // Stop the form from sending
                alert("Error: Passwords do not match!");
            }
        });
    }
});