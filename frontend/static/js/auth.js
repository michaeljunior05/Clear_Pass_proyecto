// frontend/static/js/auth.js

/**
 * @file auth.js
 * @description Centraliza la lógica de autenticación (login, registro, Google Sign-In).
 */

import { showMessage } from './ui.js'; // Importar la función showMessage

/**
 * Función para manejar la respuesta del código de autorización de Google.
 * Esta función es un callback invocado por la librería GSI.
 * @param {Object} response - Objeto de respuesta de Google que contiene el código de autorización.
 */
async function handleGoogleAuthCode(response) {
    console.log("Respuesta de Google Auth Code recibida:", response);
    const code = response.code;

    if (code) {
        console.log("Enviando código de Google a /api/auth/google/callback...");
        try {
            const fetchResponse = await fetch('/api/auth/google/callback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ code }),
            });
            const data = await fetchResponse.json();

            if (fetchResponse.ok) {
                showMessage('Inicio de sesión con Google exitoso. Redirigiendo...', 'success');
                console.log('Inicio de sesión con Google exitoso (backend response):', data);
                window.location.href = '/productos'; 
            } else {
                showMessage(data.message || 'Error al iniciar sesión con Google', 'error');
                console.error('Error en el inicio de sesión con Google (backend error):', data);
            }
        } catch (error) {
            console.error('Error de red al intentar enviar el código de Google al backend:', error);
            showMessage('Error de red al intentar iniciar sesión con Google', 'error');
        }
    } else {
        console.error("No se recibió el código de autorización de Google. Respuesta:", response);
        showMessage('Error al iniciar sesión con Google: No se obtuvo el código de autorización.', 'error');
    }
}

/**
 * Inicializa los formularios de login y registro.
 */
export function initializeAuthForms() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const emailInput = loginForm.querySelector('input[name="email"]');
            const passwordInput = loginForm.querySelector('input[name="password"]');
            const email = emailInput.value;
            const password = passwordInput.value;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ email, password }),
                });
                const data = await response.json();

                if (response.ok) {
                    showMessage('Inicio de sesión exitoso. Redirigiendo...', 'success');
                    console.log('Inicio de sesión exitoso:', data);
                    window.location.href = '/productos'; 
                } else {
                    showMessage(data.message || 'Error al iniciar sesión', 'error');
                    console.error('Error en el inicio de sesión:', data);
                }
            } catch (error) {
                console.error('Error de red:', error);
                showMessage('Error de red al intentar iniciar sesión', 'error');
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
                showMessage('Las contraseñas no coinciden', 'error');
                return;
            }

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ email, password, confirm_password }),
                });
                const data = await response.json();

                if (response.ok) {
                    showMessage(data.message || 'Registro exitoso. Redirigiendo para iniciar sesión.', 'success');
                    console.log('Registro exitoso:', data);
                    setTimeout(() => {
                        window.location.href = '/login'; 
                    }, 1500); 
                } else {
                    showMessage(data.message || 'Error al registrarse', 'error');
                    console.error('Error al registrarse:', data);
                }
            } catch (error) {
                console.error('Error de red:', error);
                showMessage('Error de red al intentar registrarse', 'error');
            }
        });
    }
}

/**
 * Inicializa el botón de Google Sign-In.
 */
export function initializeGoogleSignIn() {
    // Asegúrate de que el ID del botón es 'googleSignIn' en tu HTML
    const googleSignInButton = document.getElementById('googleSignIn'); 
    // ¡IMPORTANTE! Asegúrate de que este Client ID sea el más reciente y correcto de tu Google Cloud Console.
    const googleClientId = '967793497246-m78gm3m77u9ebqgpev7h10op0lbpqepg.apps.googleusercontent.com'; 

    if (googleSignInButton) {
        // Verifica si la librería de Google GSI ya está cargada
        if (typeof google !== 'undefined' && google.accounts && google.accounts.oauth2) {
            const client = google.accounts.oauth2.initCodeClient({
                client_id: googleClientId,
                scope: 'openid email profile',
                redirect_uri: 'https://127.0.0.1:5000/api/auth/google/callback', // AHORA ES HTTPS
                ux_mode: 'popup', 
                callback: handleGoogleAuthCode 
                // Elimina o comenta si existe: auto_select: true,
            });

            // Mover client.requestCode() DENTRO del listener de clic del botón
            googleSignInButton.addEventListener('click', () => {
                console.log("Botón de Google clickeado. Solicitando código...");
                client.requestCode({
                    redirect_uri: 'https://127.0.0.1:5000/api/auth/google/callback' // Asegurar que es HTTPS
                });
            });
        } else {
            console.warn("Google API client no cargado. El botón de inicio de sesión de Google podría no funcionar.");
        }
    }
}
