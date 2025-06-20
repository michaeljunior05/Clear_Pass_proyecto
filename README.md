# Clear Pass: Aplicación Web para Gestión de Importaciones

## Descripción del Proyecto

**Clear Pass** es una aplicación web diseñada para simplificar y brindar confianza en el proceso de gestión de importaciones. Este proyecto sirve como **Trabajo Práctico Integrador (TPI)**, demostrando la aplicación de principios de Programación Orientada a Objetos (POO), patrones de diseño y el uso de frameworks de Python para el desarrollo web full-stack.

## Características Principales

* **Autenticación de Usuarios:** Registro e inicio de sesión de usuarios (con formulario y Google Sign-In).
* **Gestión de Productos:** Simulación de consulta de productos desde una API externa.
* **Interfaz de Usuario Responsiva:** Diseño adaptativo para diferentes dispositivos (escritorio, móvil).
* **Arquitectura Modular:** Separación clara entre Frontend y Backend.

## Tecnologías Utilizadas

### Backend (Python)

* **Flask:** Micro-framework web ligero y flexible para el desarrollo de la API y el manejo de rutas.
* **Flask-Session:** Gestión de sesiones de usuario.
* **Flask-CORS:** Manejo de políticas de Cross-Origin Resource Sharing.
* **POO y Patrones de Diseño:**
    * **Patrón Repositorio:** `UserRepository`, `ProductRepository` para abstracción de datos.
    * **Patrón de Capa de Servicio:** `ExternalProductService` para interacción con APIs externas.
    * **Inyección de Dependencias:** Gestión de las dependencias de los controladores y repositorios.
    * **Herencia:** Implementación de `BaseRepository` abstracta para la consistencia de los repositorios.
    * **Alta Cohesión y Bajo Acoplamiento:** Principios aplicados en el diseño de clases y módulos.
* **Cifrado Fernet:** Uso de `cryptography` para el manejo seguro de claves.
* **Logging:** Para el seguimiento de eventos y depuración.

### Frontend (Web)

* **HTML5:** Estructura de las páginas.
* **Tailwind CSS:** Framework CSS utility-first para un diseño moderno y responsivo.
* **Jinja2:** Motor de plantillas para la renderización dinámica de HTML.
* **JavaScript (ES6 Modules):** Para la lógica interactiva del lado del cliente.
* **Google Identity Services (GSI):** Integración del inicio de sesión con Google.


## Configuración y Ejecución (Local)

### Requisitos

* Python 3.8+
* pip (gestor de paquetes de Python)

### Pasos de Configuración

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/michaeljunior05/clear_pass_proyecto.git](https://github.com/michaeljunior05/clear_pass_proyecto.git)
    cd clear_pass_proyecto
    ```

2.  **Crear y Activar Entorno Virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    ./venv/Scripts/activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *Nota: Asegúrate de que `backend/requirements.txt` contiene todas las librerías necesarias.*

4.  **Generar Clave Fernet (`email.key`):**
    * Para la seguridad de los datos, la aplicación requiere una clave de cifrado. **Este archivo NO debe subirse a GitHub.**
    * Ejecuta el siguiente script de Python para generar la clave:
        ```python
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        print(key.decode())
        ```
    * Copia la clave generada.
    * Crea un archivo llamado `email.key` dentro de la carpeta `backend/` (ej., `backend/email.key`) y pega la clave generada dentro.
    * **Asegúrate de que `backend/email.key` esté en tu `.gitignore`** para evitar que se suba accidentalmente.

### Ejecución de la Aplicación

1.  Asegúrate de que tu entorno virtual esté activado.
2.  Desde la raíz del proyecto, ejecuta:
    ```bash
    python app.py
    ```
3.  La aplicación se ejecutará localmente, usualmente en `https://127.0.0.1:5000/` (debido a la configuración SSL local).

---

