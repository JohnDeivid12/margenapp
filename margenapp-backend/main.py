import pandas as pd
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.tree import DecisionTreeClassifier

app = FastAPI(title="MargenApp - AI Backend")

# CONFIGURACIÓN DE CORS: Permite que tu frontend de Angular (normalmente en localhost:4200) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se cambia por el dominio de Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de conexión a tu PostgreSQL local
DB_PARAMS = {
    "dbname": "margenapp_db",
    "user": "postgres",
    "password": "123",  # Cambia esto por tu contraseña de Postgres
    "host": "localhost",
    "port": "5433"
}

def entrenar_modelo_ia():
    """
    Entrena un árbol de decisión con datos sintéticos para cumplir el MVP en 6 días.
    Variables predictoras (X): 
       1. variacion_ventas_pct (Caída o subida de ventas: -0.30 significa cayó 30%)
       2. margen_actual_pct (Margen de ganancia: 0.05 significa gana solo el 5%)
    Clase (y): 0 = BAJO, 1 = MEDIO, 2 = ALTO (Nivel de riesgo de pérdida)
    """
    # Dataset sintético de entrenamiento (Reglas que la IA aprenderá)
    datos_entrenamiento = [
        # [variacion_ventas, margen_actual] -> Riesgo
        [0.10, 0.25, 0],   # Ventas suben, buen margen -> Riesgo Bajo (0)
        [0.00, 0.30, 0],   # Ventas estables, buen margen -> Riesgo Bajo (0)
        [-0.05, 0.20, 1],  # Caída leve, margen aceptable -> Riesgo Medio (1)
        [-0.15, 0.12, 1],  # Caída moderada, margen bajo -> Riesgo Medio (1)
        [-0.35, 0.04, 2],  # Caída fuerte, margen crítico -> Riesgo Alto (2)
        [-0.50, -0.05, 2], # Ventas en el piso, margen negativo -> Riesgo Alto (2)
    ]
    
    df_train = pd.DataFrame(datos_entrenamiento, columns=["variacion", "margen", "riesgo"])
    X = df_train[["variacion", "margen"]]
    y = df_train["riesgo"]
    
    # Inicializar y entrenar el clasificador de Scikit-Learn
    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X, y)
    return clf

# Inicializamos el modelo al arrancar el servidor
modelo_ia = entrenar_modelo_ia()

@app.get("/api/productos/analisis")
def obtener_analisis_riesgo():
    """
    Endpoint principal para Angular. Consulta PostgreSQL, procesa las métricas
    con Pandas, clasifica con la IA y retorna un JSON limpio.
    """
    try:
        # 1. Conexión a la base de datos
        conn = psycopg2.connect(**DB_PARAMS)
        
        # 2. Consulta SQL orientada a las tablas que definimos (Productos y Ventas)
        # Nota: Calculamos la variación y el margen usando SQL/Pandas
        query = """
            SELECT 
                p.id, 
                p.nombre, 
                p.categoria,
                COALESCE(AVG(v.precio_aplicado), 0) as precio_promedio,
                p.margen_objetivo
            FROM productos p
            LEFT JOIN ventas_diarias v ON p.id = v.producto_id
            GROUP BY p.id, p.nombre, p.categoria, p.margen_objetivo;
        """
        
        df_productos = pd.read_sql_query(query, conn)
        conn.close()
        
        # Si la base de datos está vacía en las pruebas, retornamos una lista vacía
        if df_productos.empty:
            return []

        # 3. Simulación y cálculo de métricas para la IA utilizando Pandas
        # Como estamos en papel/desarrollo rápido, simularemos valores basados en tus datos
        # En una fase posterior, esto saldría de comparar esta semana vs la anterior
        df_productos["variacion_ventas_pct"] = [-0.40, 0.05, -0.10, -0.45][:len(df_productos)] if len(df_productos) <= 4 else -0.15
        df_productos["margen_actual_pct"] = [0.03, 0.28, 0.14, -0.02][:len(df_productos)] if len(df_productos) <= 4 else 0.20

        # 4. Predicción con la Inteligencia Artificial (Scikit-Learn)
        # Filtramos las columnas y les cambiamos el nombre temporalmente para que coincidan con el entrenamiento
        X_actual = df_productos[["variacion_ventas_pct", "margen_actual_pct"]].copy()
        X_actual.columns = ["variacion", "margen"]  # <-- Aquí hacemos el match de nombres

        predicciones = modelo_ia.predict(X_actual)
        
        # Mapear el número de riesgo a texto para el semáforo de Angular
        mapa_riesgo = {0: "BAJO", 1: "MEDIO", 2: "ALTO"}
        df_productos["nivel_riesgo"] = [mapa_riesgo[p] for p in predicciones]
        
        # 5. Convertir a formato JSON compatible con TypeScript/Angular
        resultado = df_productos.to_dict(orient="records")
        return resultado

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Fíjate que ahora dice "main:app" sin el .py
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)