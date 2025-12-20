# Proyecto de Finanzas con Flask

Este es un proyecto de aplicación web simple para el manejo de un portafolio de acciones usando Flask y una base de datos SQLite. El proyecto permite a los usuarios registrarse, iniciar sesión, comprar y vender acciones, y visualizar el historial de transacciones y el estado actual de su portafolio.
Proyecto completo solo en desarrollo...
## Descripción

La aplicación permite a los usuarios:

- **Registrarse**: Crear una nueva cuenta con un nombre de usuario y una contraseña segura.
- **Iniciar sesión**: Acceder a la aplicación con sus credenciales.
- **Comprar acciones**: Adquirir acciones de una empresa introduciendo el símbolo bursátil y la cantidad deseada.
- **Vender acciones**: Vender acciones que el usuario ya posee.
- **Consultar el portafolio**: Ver el valor actual de sus inversiones y el saldo en efectivo.
- **Ver historial de transacciones**: Consultar un registro de todas las transacciones realizadas.

## Requisitos

- Python 3.6 o superior
- `virtualenv` para la creación de entornos virtuales

## Instalación y Ejecución

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/bryan56gm/finance.git
   
2. **Muevete a la carpeta del proyecto:**
   ```bash
   cd finance

3. **Crea un entorno virtual:**
   ```bash
   python -m venv venv

4. **Activa el entorno virtual en Windows:**
   ```bash
   source venv/Scripts/activate
   
5. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   
6. **Ejecuta la aplicación Flask:**
   ```bash
   flask run
   
7. **La aplicación estará disponible en:**
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

![Flask Finance](https://raw.githubusercontent.com/bryan56gm/finance/main/preview.jpg)
