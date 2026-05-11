# Sistema de Orientación Vocacional Especializada

Plataforma desarrollada con Django para automatizar el proceso de orientación de especialidades en la Facultad de Ingeniería y Ciencias Aplicadas.

## Características (Avance 1)
* **Arquitectura MTV:** Patrón nativo de Django.
* **Validación Estricta Back-End:** Algoritmo de Módulo 10 para la cédula ecuatoriana ejecutado directamente en los modelos (`clean()`).
* **Relaciones Dinámicas (AJAX):** Dropdowns dependientes para Área Académica y Especialidad.
* **Redirección de Estado:** Uso de variables de sesión para forzar el flujo hacia el Test de Habilidades post-registro.

## Instrucciones de Ejecución Local
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno e instalar dependencias: `pip install django`
4. Aplicar migraciones: `python manage.py migrate`
5. Levantar el servidor: `python manage.py runserver`