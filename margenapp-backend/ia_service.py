"""
Servicio de Inteligencia Artificial - Predicción de riesgo
"""
import pandas as pd
from sklearn.tree import DecisionTreeClassifier


class IAService:
    """Servicio centralizado para predicciones de riesgo usando Machine Learning"""
    
    def __init__(self):
        """Inicializa y entrena el modelo de IA"""
        self.modelo = self._entrenar_modelo()
    
    @staticmethod
    def _entrenar_modelo():
        """
        Entrena un árbol de decisión con datos sintéticos.
        
        Variables predictoras (X): 
           1. variacion_ventas_pct: Caída o subida de ventas (-0.30 = cayó 30%)
           2. margen_actual_pct: Margen de ganancia (0.05 = gana solo 5%)
           
        Clase (y): 0 = BAJO, 1 = MEDIO, 2 = ALTO (Nivel de riesgo de pérdida)
        """
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
        
        clf = DecisionTreeClassifier(random_state=42)
        clf.fit(X, y)
        return clf
    
    def evaluar_riesgo(self, precio: float, margen_objetivo: float) -> tuple:
        """
        Ejecuta el algoritmo predictivo para evaluar el nivel de riesgo
        
        Retorna: (nivel_riesgo, probabilidad_riesgo, recomendacion, variacion_ventas)
        """
        # Simulamos la variación de ventas basada en el margen para alimentar el árbol
        if margen_objetivo < 0.05:
            variacion_ventas = -0.40  # Alto riesgo de caída
        elif margen_objetivo < 0.15:
            variacion_ventas = -0.15  # Riesgo moderado
        else:
            variacion_ventas = -0.05  # Riesgo bajo
        
        X_prediccion = pd.DataFrame({
            "variacion": [variacion_ventas],
            "margen": [margen_objetivo]
        })
        
        # Predicción del modelo
        prediccion_numerica = self.modelo.predict(X_prediccion)[0]
        mapa_riesgo = {0: "BAJO", 1: "MEDIO", 2: "ALTO"}
        nivel_riesgo_texto = mapa_riesgo[prediccion_numerica]
        
        # Probabilidades de cada clase
        probabilidades = self.modelo.predict_proba(X_prediccion)[0]
        probabilidad_riesgo_alto = probabilidades[2] * 100
        
        # Recomendaciones personalizadas
        recomendaciones = {
            "BAJO": f"✅ Riesgo bajo. Margen saludable del {margen_objetivo*100:.1f}%. Continúa monitoreando.",
            "MEDIO": f"⚠️ Riesgo moderado. Considera aumentar el margen del {margen_objetivo*100:.1f}% o revisar costos.",
            "ALTO": f"🔴 Riesgo alto. Margen crítico del {margen_objetivo*100:.1f}%. Acción inmediata recomendada."
        }
        
        return nivel_riesgo_texto, probabilidad_riesgo_alto, recomendaciones[nivel_riesgo_texto], variacion_ventas
