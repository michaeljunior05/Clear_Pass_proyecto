document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form'); // Selecciona el formulario de inicio de sesión por su ID
    const registerForm = document.getElementById('register-form'); // Selecciona el formulario de registro por su ID
    const googleSignInButton = document.getElementById('googleSignIn');
    const googleClientId = '222270840199-pcntooj9dsvmsn79j11glth1fueaurij.apps.googleusercontent.com'; // Tu ID de cliente de Google

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const emailInput = loginForm.querySelector('input[name="email"]');
            const passwordInput = loginForm.querySelector('input[name="password"]');
            const email = emailInput.value;
            const password = passwordInput.value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ email, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = '/productos';
                    console.log('Inicio de sesión exitoso:', data);
                } else {
                    console.error('Error en el inicio de sesión:', data);
                    alert(data.message || 'Error al iniciar sesión');
                }

            } catch (error) {
                console.error('Error de red:', error);
                alert('Error de red al intentar iniciar sesión');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const emailInput = registerForm.querySelector('input[name="email"]');
            const passwordInput = registerForm.querySelector('input[name="password"]');
            const confirmPasswordInput = registerForm.querySelector('input[name="confirm_password"]');
            const email = emailInput.value;
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;

            if (password !== confirmPassword) {
                alert('Las contraseñas no coinciden');
                return;
            }

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ email, password, confirm_password }),
                });

                const data = await response.json();

                const messageDiv = document.createElement('div'); // Crea un div para el mensaje
                messageDiv.classList.add('success-message'); // O alguna clase para estilos
                messageDiv.textContent = data.message || 'Registro exitoso. Serás redirigido para iniciar sesión.';

                registerForm.parentNode.insertBefore(messageDiv, registerForm); // Inserta el mensaje antes del formulario

                if (response.ok) {
                    console.log('Registro exitoso:', data);
                    // Redirigir a la página de inicio de sesión después de unos segundos
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 3000); // Redirige después de 3 segundos
                } else {
                    console.error('Error al registrarse:', data);
                    alert(data.message || 'Error al registrarse');
                }

            } catch (error) {
                console.error('Error de red:', error);
                alert('Error de red al intentar registrarse');
            }
        });
    }

    if (googleSignInButton) {
        const client = google.accounts.oauth2.initCodeClient({
            client_id: googleClientId,
            scope: 'openid email profile',
            redirect_uri: 'http://127.0.0.1:5000/auth/google/callback',
        });

        googleSignInButton.addEventListener('click', () => {
            client.requestCode();
        });
    }

    // Función que se ejecutará después de que Google redirija (en el frontend)
    window.onload = async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');

        if (code) {
            try {
                const response = await fetch('/auth/google/callback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ code }),
                });

                const data = await response.json();

                if (response.ok) {
                    console.log('Inicio de sesión con Google exitoso:', data);
                    window.location.href = '/productos'; // Redirige a la página principal
                } else {
                    console.error('Error en el inicio de sesión con Google:', data);
                    alert(data.message || 'Error al iniciar sesión con Google');
                }
            } catch (error) {
                console.error('Error de red al intentar iniciar sesión con Google:', error);
                alert('Error de red al intentar iniciar sesión con Google');
            }
        }
    };
});