document.getElementById('reg-log').addEventListener('change', function() {
    var form = document.getElementById('auth-form');
    if (this.checked) {
        form.action = signupUrl;
        form.querySelector('input[type="submit"]').value = "REGISTER";
    } else {
        form.action = loginUrl;
        form.querySelector('input[type="submit"]').value = "LOGIN";
    }
});
