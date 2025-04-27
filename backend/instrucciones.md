# (POR AHORA NO LO HAGAN, YO DESPUES LES EXPLICO TODO Y COMO DEBEN HACERLO)
## Paso 1: Crear un entorno virtual

¿Qué estamos haciendo? Un entorno virtual en Python permite instalar todas las dependencias del proyecto
sin afectar otras aplicaciones de tu computadora. 
Así, si en el futuro trabajas en otro proyecto, las librerías de uno no interferirán con las de otro.


1. Abre la terminal y entra a la carpeta backend de tu proyecto:
 ´´git bash
cd Clear-Pass-proyecto/backend

2. Crea un entorno virtual con phyton
´´git bash
python -m venv venv
*Esto crea una carpeta llamada venv, donde se guardarán las librerías del proyecto.*

3. Activa el entorno vitual
´´git bash
venv\Scripts\activate
*Cuando el entorno virtual está activo, verás (venv) al inicio de la línea de comandos.*

## Paso 2: Instalar Flask y MySQL en el entorno virtual

¿Qué estamos haciendo? Flask es el framework (herramienta) que usaremos para construir el backend de nuestra aplicación web. Flask no viene preinstalado con Python, así que debemos instalarlo. También instalaremos flask-mysqldb, que nos permitirá conectarnos con la base de datos MySQL.## Paso 2: Instalar Flask y MySQL en el entorno vitual

1. Asegúrate de que el entorno virtual está activado.
2. Instala Flask y las librerías necesarias con este comando:
''git bash
pip install flask flask-mysqldb flask-login

3. ¿Cómo verificar que Flask se instaló correctamente? Escribe:
python -m flask --version

*Si ves una versión de Flask en pantalla, la instalación fue correcta.*


# (POR AHORA NO LO HAGAN, YO DESPUES LES EXPLICO TODO Y COMO DEBEN HACERLO)

