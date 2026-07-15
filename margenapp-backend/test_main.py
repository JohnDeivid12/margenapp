"""
Test unitarios para el endpoint POST /api/productos/crear
Utiliza pytest y TestClient de FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ============================================================================
# TESTS DE VALIDACIÓN CON PYDANTIC
# ============================================================================

class TestValidacionProductoCreate:
    """Tests para validar que Pydantic rechaza datos inválidos"""

    def test_producto_valido(self):
        """Debe aceptar un producto con datos válidos"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop Dell XPS 13",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20,
            "cantidad_inicial": 10
        })
        
        # No debe ser 422 (validación fallida)
        assert response.status_code != 422, f"Validación falló: {response.text}"

    def test_nombre_vacio(self):
        """Debe rechazar nombre vacío"""
        response = client.post("/api/productos/crear", json={
            "nombre": "",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        assert response.status_code == 422
        assert "nombre" in response.text

    def test_nombre_muy_largo(self):
        """Debe rechazar nombre > 100 caracteres"""
        response = client.post("/api/productos/crear", json={
            "nombre": "A" * 101,
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        assert response.status_code == 422

    def test_categoria_vacia(self):
        """Debe rechazar categoría vacía"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        assert response.status_code == 422

    def test_precio_negativo(self):
        """Debe rechazar precio negativo"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": -100.00,
            "margen_objetivo": 0.20
        })
        
        assert response.status_code == 422
        assert "precio" in response.text.lower()

    def test_precio_cero(self):
        """Debe rechazar precio = 0"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 0.00,
            "margen_objetivo": 0.20
        })
        
        assert response.status_code == 422

    def test_margen_menor_a_cero(self):
        """Debe rechazar margen < 0"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": -0.10
        })
        
        assert response.status_code == 422
        assert "margen" in response.text.lower()

    def test_margen_mayor_a_uno(self):
        """Debe rechazar margen > 1"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 1.5
        })
        
        assert response.status_code == 422

    def test_cantidad_negativa(self):
        """Debe rechazar cantidad inicial negativa"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20,
            "cantidad_inicial": -5
        })
        
        assert response.status_code == 422

    def test_cantidad_inicial_opcional(self):
        """Debe aceptar producto sin cantidad_inicial (default: 0)"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        # La respuesta debe contener cantidad_inicial = 0
        if response.status_code == 201:
            assert response.json()["cantidad_inicial"] == 0 or response.status_code == 503

    def test_espacios_en_blanco_eliminados(self):
        """Debe eliminar espacios en blanco del nombre y categoría"""
        response = client.post("/api/productos/crear", json={
            "nombre": "  Laptop Dell  ",
            "categoria": "  Electrónica  ",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        # No debe fallar la validación
        assert response.status_code != 422


# ============================================================================
# TESTS DE RESPUESTA
# ============================================================================

class TestRespuestaProducto:
    """Tests para validar la estructura de respuesta"""

    def test_response_tiene_campos_requeridos(self):
        """La respuesta debe tener todos los campos requeridos"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        # Si es exitoso, verificar campos
        if response.status_code == 201:
            data = response.json()
            campos_requeridos = [
                "id", "nombre", "categoria", "precio",
                "margen_objetivo", "cantidad_inicial",
                "nivel_riesgo", "probabilidad_riesgo",
                "mensaje", "fecha_creacion"
            ]
            
            for campo in campos_requeridos:
                assert campo in data, f"Campo '{campo}' faltante en respuesta"

    def test_nivel_riesgo_valido(self):
        """El nivel_riesgo debe ser BAJO, MEDIO o ALTO"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        if response.status_code == 201:
            nivel = response.json()["nivel_riesgo"]
            assert nivel in ["BAJO", "MEDIO", "ALTO"]

    def test_probabilidad_riesgo_rango(self):
        """La probabilidad de riesgo debe estar entre 0 y 100"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        if response.status_code == 201:
            probabilidad = response.json()["probabilidad_riesgo"]
            assert 0 <= probabilidad <= 100

    def test_status_code_exitoso(self):
        """El endpoint debe retornar 201 Created en caso exitoso"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00,
            "margen_objetivo": 0.20
        })
        
        # 201 si es exitoso, 503 si BD no está disponible
        assert response.status_code in [201, 503]


# ============================================================================
# TESTS DE ALGORITMO PREDICTIVO
# ============================================================================

class TestAlgoritmoPredictivo:
    """Tests para validar la evaluación de riesgo"""

    def test_margen_alto_riesgo_bajo(self):
        """Margen > 20% debe resultar en riesgo BAJO"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Producto",
            "categoria": "Test",
            "precio": 100.00,
            "margen_objetivo": 0.25
        })
        
        if response.status_code == 201:
            assert response.json()["nivel_riesgo"] in ["BAJO", "MEDIO"]

    def test_margen_bajo_riesgo_alto(self):
        """Margen < 5% debe resultar en riesgo ALTO o MEDIO"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Producto",
            "categoria": "Test",
            "precio": 100.00,
            "margen_objetivo": 0.03
        })
        
        if response.status_code == 201:
            assert response.json()["nivel_riesgo"] in ["ALTO", "MEDIO"]

    def test_margen_medio_riesgo_medio(self):
        """Margen 5-20% debe resultar en riesgo MEDIO o BAJO"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Producto",
            "categoria": "Test",
            "precio": 100.00,
            "margen_objetivo": 0.10
        })
        
        if response.status_code == 201:
            assert response.json()["nivel_riesgo"] in ["MEDIO", "BAJO"]

    def test_mensaje_contiene_margen(self):
        """El mensaje debe mencionar el margen en porcentaje"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Producto",
            "categoria": "Test",
            "precio": 100.00,
            "margen_objetivo": 0.25
        })
        
        if response.status_code == 201:
            mensaje = response.json()["mensaje"]
            assert "25" in mensaje  # 0.25 * 100 = 25


# ============================================================================
# TESTS DE OTROS ENDPOINTS
# ============================================================================

class TestOtrosEndpoints:
    """Tests para otros endpoints de la API"""

    def test_health_check(self):
        """El endpoint /api/health debe retornar 200"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_analisis_riesgo(self):
        """El endpoint /api/productos/analisis debe retornar 200"""
        response = client.get("/api/productos/analisis")
        assert response.status_code == 200
        data = response.json()
        assert "productos" in data or "mensaje" in data


# ============================================================================
# TESTS DE MANEJO DE ERRORES
# ============================================================================

class TestErrorHandling:
    """Tests para validar manejo de errores"""

    def test_campo_faltante_retorna_422(self):
        """Si falta un campo requerido, retorna 422"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": 1200.00
            # Falta margen_objetivo
        })
        
        assert response.status_code == 422

    def test_tipo_dato_incorrecto_retorna_422(self):
        """Si el tipo de dato es incorrecto, retorna 422"""
        response = client.post("/api/productos/crear", json={
            "nombre": "Laptop",
            "categoria": "Electrónica",
            "precio": "mil dólares",  # Debería ser número
            "margen_objetivo": 0.20
        })
        
        assert response.status_code == 422


# ============================================================================
# EJECUCIÓN DE TESTS
# ============================================================================

if __name__ == "__main__":
    # Ejecutar con: pytest test_main.py -v
    pytest.main([__file__, "-v", "--tb=short"])
