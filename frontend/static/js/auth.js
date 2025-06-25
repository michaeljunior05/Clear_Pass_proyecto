// frontend/static/js/auth.js

/**
 * @file auth.js
 * @description Centraliza la lógica de autenticación (login, registro, Google Sign-In).
 */
// frontend/static/js/auth.js

import { showMessage } from './ui.js';

const API_BASE_URL = '/api'; // Asegúrate de que esto coincida con tus rutas de Flask

/**
 * Maneja la respuesta de Google One Tap o Google Sign-In button.
 * @param {Object} response - Objeto de respuesta de Google con el ID token.
 */
window.handleCredentialResponse = async (response) => {
    if (response.credential) {
        console.log("ID Token recibido de Google:", response.credential);
        try {
            const res = await fetch(`${API_BASE_URL}/google-login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: response.credential }),
            });

            const data = await res.json();

            if (res.ok) {
                showMessage(data.message, 'success');
                // Redirigir a la página de productos o dashboard después del login exitoso
                window.location.href = '/productos'; 
            } else {
                showMessage(data.message || 'Error en la autenticación con Google.', 'error');
            }
        } catch (error) {
            console.error('Error durante la autenticación con Google:', error);
            showMessage('Error de conexión o autenticación con Google.', 'error');
        }
    }
};

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
            const password = passwordInput.value.trim(); 
            const confirmPassword = confirmPasswordInput.value.trim(); // <-- AQUI YA ES EL VALOR

            // Los console.log de depuración ya están bien en auth.js

            if (password !== confirmPassword) {
                showMessage('Las contraseñas no coinciden', 'error');
                return;
            }

            try {
                // ASEGURATE QUE CONFIRM_PASSWORD SE PASA COMO EL VALOR YA OBTENIDO
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ email, password, confirm_password: confirmPassword }), // <-- ¡CAMBIO CLAVE AQUÍ!
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

// Inicializar los formularios cuando el DOM esté completamente cargado.
document.addEventListener('DOMContentLoaded', () => {
    initializeAuthForms();
    // No necesitamos llamar a initializeGoogleSignIn() aquí,
    // ya que GSI se inicializa a través de los atributos data-* en el HTML.
});
