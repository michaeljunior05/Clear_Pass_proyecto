// frontend/static/js/auth.js

/**
 * @file auth.js
 * @description Centraliza la lógica de autenticación (login, registro, Google Sign-In).
 */

import { showMessage } from './ui.js'; // Importar la función showMessage

/**
 * Función para manejar la respuesta de credenciales de Google.
 * Esta función es un callback invocado directamente por la librería GSI (desde data-callback).
 * Recibe un objeto de respuesta que contiene el ID token JWT.
 * ¡IMPORTANTE! Debe ser accesible globalmente (ej. window.handleCredentialResponse)
 */
window.handleCredentialResponse = async (response) => {
    console.log("Respuesta de credenciales de Google recibida:", response);
    const idToken = response.credential; // Este es el JWT que necesitas enviar al backend

    if (idToken) {
        console.log("Enviando ID token de Google a /api/auth/google-login...");
        try {
            // Asegúrate de que tu backend tenga una ruta /api/auth/google-login que espere un POST con JSON
            const fetchResponse = await fetch('/api/auth/google-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_token: idToken }),
            });
            const data = await fetchResponse.json();

            if (fetchResponse.ok) {
                showMessage('Inicio de sesión con Google exitoso. Redirigiendo...', 'success');
                console.log('Inicio de sesión con Google exitoso (backend response):', data);
                window.location.href = data.redirect_url || '/productos';
            } else {
                showMessage(data.message || 'Error al iniciar sesión con Google', 'error');
                console.error('Error en el inicio de sesión con Google (backend error):', data);
            }
        } catch (error) {
            console.error('Error de red al intentar enviar el token de Google al backend:', error);
            showMessage('Error de red al intentar iniciar sesión con Google', 'error');
        }
    } else {
        console.error("No se recibió el ID token de Google. Respuesta:", response);
        showMessage('Error al iniciar sesión con Google: No se obtuvo el token.', 'error');
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
            // ¡ATENCIÓN AQUÍ! Añadir .trim() para eliminar espacios en blanco al inicio/final
            const password = passwordInput.value.trim(); 
            const confirmPassword = confirmPasswordInput.value.trim(); // Añadir .trim() aquí también

            // Mantén estos console.log para el diagnóstico final si el problema persiste
            console.log("Email:", email);
            console.log("Contraseña (campo 1 - trimmed):", password);
            console.log("Confirmar Contraseña (campo 2 - trimmed):", confirmPassword);
            console.log("¿Coinciden (después de trim)?", password === confirmPassword);


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


// Inicializar los formularios cuando el DOM esté completamente cargado.
document.addEventListener('DOMContentLoaded', () => {
    initializeAuthForms();
    // No necesitamos llamar a initializeGoogleSignIn() aquí,
    // ya que GSI se inicializa a través de los atributos data-* en el HTML.
});
