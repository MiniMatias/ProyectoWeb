# Sistema de Inferencia de Orientación Vocacional 🎯

<p align="left">
   <img src="https://img.shields.io/badge/STATUS-RELEASE%20CANDIDATE%201.0-green">
   <img src="https://img.shields.io/badge/Django-5.0-092E20">
   <img src="https://img.shields.io/badge/Python-3.13-3776AB">
</p>

## Índice
* [Descripción del proyecto](#descripción-del-proyecto)
* [Estado del proyecto](#estado-del-proyecto)
* [Características de la aplicación y demostración](#características-de-la-aplicación-y-demostración)
* [Acceso al proyecto](#acceso-al-proyecto)
* [Abre y ejecuta el proyecto](#abre-y-ejecuta-el-proyecto)
* [Tecnologías utilizadas](#tecnologías-utilizadas)
* [Autores](#autores)

## Descripción del proyecto
Un sistema experto paramétrico construido en entorno web que evalúa perfiles de estudiantes y calcula afinidades vocacionales mediante un motor matemático. El objetivo principal es reemplazar la subjetividad de la orientación tradicional con análisis de pesos ponderados basados objetivamente en las habilidades del estudiante.

## Estado del proyecto
<h4 align="left"> 
	🚧  Sistema de Inferencia V1.0 🚀 Completado y Estabilizado  🚧
</h4>

## Características de la aplicación y demostración
El proyecto opera bajo el patrón arquitectónico MVT (Model-View-Template) y cuenta con las siguientes características clave:

* **Motor de Inferencia Vectorial:** Algoritmo dinámico en memoria RAM que cruza los promedios del estudiante contra una matriz relacional de pesos de carreras para extraer matemáticamente el "Top 3".
* **Integridad Estricta en el Backend:** Validación algorítmica de la cédula de identidad ecuatoriana codificada directamente a nivel de modelo de base de datos.
* **UI Analítica:** Gráficos Radiales interactivos inyectados dinámicamente con Chart.js según los resultados paramétricos del usuario.
* **Asincronía (AJAX):** Menús de registro interdependientes utilizando Fetch API nativo.

## Acceso al proyecto
Puedes acceder al código fuente completo de este proyecto clonando el repositorio desde GitHub. 

## Abre y ejecuta el proyecto
El sistema está diseñado para ser agnóstico a la infraestructura. Para reproducir el entorno de desarrollo localmente, sigue estos pasos:

**1. Clona el repositorio e ingresa a la carpeta:**
```bash
git clone [https://github.com/tu-usuario/ProyectoWeb.git](https://github.com/tu-usuario/ProyectoWeb.git)
cd ProyectoWeb
```

**2. Crea y activa un entorno virtual:**
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
```

**3. Instala las dependencias del núcleo:**
```bash
pip install -r requirements.txt
```

**4. Configura el entorno seguro:**
Crea un archivo `.env` en el directorio raíz (junto a `manage.py`) para evitar el colapso de la seguridad local:
```env
DEBUG=True
SECRET_KEY=django-insecure-clave-temporal-local
DATABASE_URL=sqlite:///db.sqlite3
```

**5. Inicializa y pobla la Base de Datos:**
El sistema contiene un script automatizado para cargar las habilidades, preguntas y métricas. Ejecuta estrictamente en este orden:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py poblar_base
```

**6. Ejecuta el servidor:**
```bash
python manage.py runserver
```
El sistema estará listo en `http://127.0.0.1:8000/acceso`.

## Tecnologías utilizadas
- `Python 3.13`
- `Django 5.0`
- `SQLite` (Desarrollo) / `PostgreSQL` (Producción)
- `JavaScript` (Fetch API) y `Chart.js`
- `HTML5` / `CSS3` / `Bootstrap`

## Autores
| [<img src="https://avatars.githubusercontent.com/u/MiniMatias" width=115><br><sub>Matias Monteros</sub>](https://github.com/MiniMatias) |
| :---: |

- ✉️ **Contacto Académico:** matias.monteros@udla.edu.ec
- 📱 **Numero de telefono:** [0999515429]

---
*Desarrollado como proyecto de aplicación práctica de algoritmos y arquitectura backend.*