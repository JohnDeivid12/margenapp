# MargenApp - MVP Panel de Control IA

Este proyecto es un MVP para el análisis y monitoreo de márgenes de ganancia y alertas de riesgo mediante Inteligencia Artificial (Árboles de Decisión). Está construido con **FastAPI** en el Backend y **Angular** en el Frontend, utilizando **PostgreSQL** como base de datos.

---

## 🛠️ Requisitos Previos

Antes de empezar, asegúrate de tener instalado en tu máquina:

* [Python 3.10+](https://www.python.org/)
* [Node.js (versión LTS)](https://nodejs.org/)
* [PostgreSQL](https://www.postgresql.org/) corriendo localmente con la base de datos configurada.

---

## 🐍 Configuración del BACKEND (Python + FastAPI)

Párate en la carpeta raíz del backend desde tu terminal y sigue estos pasos:

### Paso 1: Actualizar el gestor de paquetes (Opcional pero recomendado)

```bash
python -m pip install --upgrade pip
```

### Paso 2: Instalar las librerías necesarias

Instala el entorno de ejecución, el framework web, el motor de base de datos y la suite de IA:

```bash
pip install fastapi uvicorn pandas scikit-learn psycopg2-binary
```

### Paso 3: Correr el servidor del Backend

Ejecuta el script principal para levantar el servidor de FastAPI:

```bash
python main.py
```

El backend estará disponible en: `http://127.0.0.1:8000`

---

## 🅰️ Configuración del FRONTEND (Angular 19+)

Abre una nueva terminal y muévete a la carpeta del frontend:

```bash
cd margenapp-frontend
```

### Paso 1: Instalar el Angular CLI de forma global

Si nunca has trabajado con Angular en tu PC, instala la herramienta de comandos globalmente:

```bash
npm install -g @angular/cli
```

### Paso 2: Instalar las dependencias del proyecto

¡NO uses `ng new`! Como ya descargaste el código del repositorio, solo debes restaurar los módulos de Node (incluyendo Bootstrap y Bootstrap Icons que ya están configurados en el `package.json`):

```bash
npm install
```

### Paso 3: Levantar el servidor de desarrollo

Arranca la aplicación web localmente:

```bash
ng serve
```

El frontend estará disponible en el navegador en: `http://localhost:4200`

---

## 👥 Flujo de Trabajo en Equipo (GitFlow)

Para mantener el código ordenado en estos días de entrega, trabajaremos bajo la siguiente estructura de ramas:

* `master`: Código estable de producción (entregas finales).
* `develop`: Rama de integración de características. Siempre trabajamos aquí.
* `feature-...`: Ramas específicas para tareas cortas.
