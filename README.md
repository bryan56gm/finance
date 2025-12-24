# Proyecto de Finanzas con Flask

Este es un proyecto de aplicación web simple para el manejo de un
portafolio de acciones usando Flask y una base de datos relacional.\
El proyecto permite a los usuarios registrarse, iniciar sesión, comprar
y vender acciones, y visualizar el historial de transacciones y el
estado actual de su portafolio.

Proyecto completo solo en desarrollo...

## Descripción

La aplicación permite a los usuarios:

-   **Registrarse**: Crear una nueva cuenta con un nombre de usuario y
    una contraseña segura.
-   **Iniciar sesión**: Acceder a la aplicación con sus credenciales.
-   **Comprar acciones**: Adquirir acciones de una empresa introduciendo
    el símbolo bursátil y la cantidad deseada.
-   **Vender acciones**: Vender acciones que el usuario ya posee.
-   **Consultar el portafolio**: Ver el valor actual de sus inversiones
    y el saldo en efectivo.
-   **Ver historial de transacciones**: Consultar un registro de todas
    las transacciones realizadas.

## Base de Datos

-   **Desarrollo**: SQLite\
-   **Producción**: PostgreSQL

La aplicación utiliza **SQLAlchemy** como ORM, lo que permite cambiar de
SQLite a PostgreSQL sin modificar la lógica de la aplicación, únicamente
ajustando la variable de entorno `DATABASE_URL`.

> ⚠️ SQLite se usa únicamente para desarrollo local.\
> En producción, se recomienda PostgreSQL por su mejor manejo de
> concurrencia y escalabilidad.

## Requisitos

-   Python 3.6 o superior
-   `virtualenv` para la creación de entornos virtuales

## Instalación y Ejecución

1.  **Clona el repositorio:**

    ``` bash
    git clone https://github.com/bryan56gm/finance.git
    ```

2.  **Muévete a la carpeta del proyecto:**

    ``` bash
    cd finance
    ```

3.  **Crea un entorno virtual:**

    ``` bash
    python -m venv venv
    ```

4.  **Activa el entorno virtual en Windows:**

    ``` bash
    source venv/Scripts/activate
    ```

5.  **Instala las dependencias:**

    ``` bash
    pip install -r requirements.txt
    ```

6.  **Configura la base de datos (opcional en desarrollo):**

    Para desarrollo local no es necesario configurar nada adicional.\
    Para producción, define la variable de entorno:

    ``` bash
    DATABASE_URL=postgresql://usuario:password@host:puerto/dbname
    ```

7.  **Ejecuta la aplicación Flask:**

    ``` bash
    flask run
    ```

8.  **La aplicación estará disponible en:** <http://127.0.0.1:5000/>

![Flask Finance](preview.jpg)
