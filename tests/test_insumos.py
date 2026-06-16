import pytest
import app.models as models
from app.schemas.insumos import InsumoBase
from pydantic import ValidationError

# ----------------- PRUEBAS UNITARIAS -----------------

def test_insumo_base_validation():
    """Prueba unitaria para verificar que el esquema InsumoBase valide correctamente valores no negativos."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Validación de Valores No Negativos en InsumoBase (test_insumo_base_validation)")
    print("="*80)

    # PASO 1: Datos válidos
    payload_valido = {
        "nombre": "Detergente Hipoalergénico",
        "cantidad": 10.0,
        "cantidad_alerta": 2.0,
        "costo_actual": 450.0
    }
    print("\n--- PASO 1: Validar Datos Correctos (No Negativos) ---")
    print(f"  * Entrada: Datos del Schema = {payload_valido}")
    print("  * Resultado esperado: Instanciación correcta del Schema sin errores.")
    schema_inst = InsumoBase(**payload_valido)
    print(f"  * Resultado obtenido: Schema instanciado correctamente con cantidad = {schema_inst.cantidad} y costo = ${schema_inst.costo_actual}")
    assert schema_inst.cantidad == 10.0
    assert schema_inst.costo_actual == 450.0

    # PASO 2: Datos inválidos (cantidad negativa)
    payload_invalido = {
        "nombre": "Detergente Hipoalergénico",
        "cantidad": -5.0,
        "cantidad_alerta": 2.0,
        "costo_actual": 450.0
    }
    print("\n--- PASO 2: Validar Cantidad Negativa ---")
    print(f"  * Entrada: Datos del Schema = {payload_invalido}")
    print("  * Resultado esperado: Pydantic ValidationError levantado por la cantidad negativa.")
    
    with pytest.raises(ValidationError) as exc_info:
        InsumoBase(**payload_invalido)
        
    print(f"  * Resultado obtenido: ValidationError capturado exitosamente.")
    print(f"    - Detalle del error: '{exc_info.value.errors()[0]['msg']}'")
    assert "El valor no puede ser negativo" in exc_info.value.errors()[0]['msg']
    print("  * Detalle de Validación: La validación impidió exitosamente registrar una cantidad de insumo negativa.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

def test_crud_insumos_por_administrador(client, admin_headers):
    """Verifica que el Administrador pueda realizar el CRUD de insumos."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: CRUD de Insumos por Administrador (test_crud_insumos_por_administrador)")
    print("="*80)

    # PASO 1: Crear Insumo
    ins_data = {
        "nombre": "Detergente Ecológico",
        "cantidad": 100.0,
        "cantidad_alerta": 20.0,
        "costo_actual": 1200.5
    }
    print("\n--- PASO 1: Crear Insumo ---")
    print(f"  * Entrada: POST /insumos/ con Datos = {ins_data} y headers = Administrador")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y retornar el insumo con ID asignado.")
    response = client.post("/insumos/", json=ins_data, headers=admin_headers)
    assert response.status_code == 201
    res_json = response.json()
    ins_id = res_json["id"]
    print(f"  * Resultado obtenido: Status Code = {response.status_code}")
    print(f"    - ID Generado: {ins_id}")
    print(f"    - Insumo Creado: '{res_json['nombre']}' | Stock = {res_json['cantidad']} | Alerta Mínima = {res_json['cantidad_alerta']}")
    print("  * Detalle de Validación: El insumo se ha registrado correctamente con su stock inicial.")

    # PASO 2: Leer Insumo
    print("\n--- PASO 2: Leer Insumo ---")
    print(f"  * Entrada: GET /insumos/{ins_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y obtener los datos correctos del insumo.")
    response_get = client.get(f"/insumos/{ins_id}", headers=admin_headers)
    assert response_get.status_code == 200
    get_json = response_get.json()
    print(f"  * Resultado obtenido: Status Code = {response_get.status_code}")
    print(f"    - Nombre obtenido: '{get_json['nombre']}'")
    print(f"    - Costo Actual: ${get_json['costo_actual']}")
    print("  * Detalle de Validación: Los datos del insumo retornado coinciden con el registro de la base de datos.")

    # PASO 3: Actualizar Insumo
    update_data = {
        "cantidad": 80.0,
        "costo_actual": 1300.0
    }
    print("\n--- PASO 3: Actualizar Insumo ---")
    print(f"  * Entrada: PATCH /insumos/{ins_id} con Datos a actualizar = {update_data}")
    print("  * Resultado esperado: Código HTTP 200 (OK) con la cantidad rebajada a 80.0 y el costo a $1300.0.")
    response_update = client.patch(f"/insumos/{ins_id}", json=update_data, headers=admin_headers)
    assert response_update.status_code == 200
    update_json = response_update.json()
    print(f"  * Resultado obtenido: Status Code = {response_update.status_code}")
    print(f"    - Nueva cantidad: {update_json['cantidad']} (Esperado: 80.0)")
    print(f"    - Nuevo costo: ${update_json['costo_actual']} (Esperado: $1300.0)")
    print("  * Detalle de Validación: Modificaciones aplicadas y confirmadas en la respuesta.")
    assert update_json["cantidad"] == 80.0
    assert update_json["costo_actual"] == 1300.0

    # PASO 4: Eliminar Insumo
    print("\n--- PASO 4: Eliminar Insumo (Baja Lógica) ---")
    print(f"  * Entrada: DELETE /insumos/{ins_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y el campo 'baja' en True.")
    response_delete = client.delete(f"/insumos/{ins_id}", headers=admin_headers)
    assert response_delete.status_code == 200
    delete_json = response_delete.json()
    print(f"  * Resultado obtenido: Status Code = {response_delete.status_code}")
    print(f"    - baja = {delete_json['baja']} (Esperado: True)")
    print("  * Detalle de Validación: Insumo dado de baja correctamente (baja lógica).")
    assert delete_json["baja"] is True

    # PASO 5: Intentar obtener el insumo eliminado
    print("\n--- PASO 5: Intentar Consultar Insumo de Baja ---")
    print(f"  * Entrada: GET /insumos/{ins_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 404 (Not Found) debido a que tiene la baja lógica activa.")
    response_get_del = client.get(f"/insumos/{ins_id}", headers=admin_headers)
    print(f"  * Resultado obtenido: Status Code = {response_get_del.status_code}")
    print(f"    - Mensaje de Detalle: '{response_get_del.json().get('detail')}'")
    print("  * Detalle de Validación: La baja lógica funciona correctamente impidiendo consultas ordinarias.")
    assert response_get_del.status_code == 404

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_insumos_rbac_restricciones(client, operador_headers, cliente_headers, admin_headers):
    """Verifica restricciones de roles en Insumos."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE CONTROL DE ACCESOS (RBAC): Restricciones sobre Insumos (test_insumos_rbac_restricciones)")
    print("="*80)

    # PASO 1: Crear insumo previo para las pruebas
    ins_data = {
        "nombre": "Suavizante Vainilla",
        "cantidad": 50.0,
        "cantidad_alerta": 10.0,
        "costo_actual": 850.0
    }
    print("\n--- PASO 1: Crear Insumo Base por el Administrador ---")
    resp_create_admin = client.post("/insumos/", json=ins_data, headers=admin_headers)
    ins_id = resp_create_admin.json()["id"]
    print(f"  * Entrada: POST /insumos/ por Admin | Insumo: '{ins_data['nombre']}'")
    print(f"  * Resultado obtenido: ID asignado = {ins_id}")

    # PASO 2: Cliente intenta operar
    print("\n--- PASO 2: Intentos de Acceso y Modificación por un Cliente (Rol Cliente) ---")
    print("  * Entrada: Un Cliente realiza GET, POST, PATCH y DELETE sobre el módulo de insumos.")
    print("  * Resultado esperado: Denegar acceso con código HTTP 403 (Forbidden) en todos los casos.")
    r_c_get = client.get("/insumos/", headers=cliente_headers)
    r_c_post = client.post("/insumos/", json=ins_data, headers=cliente_headers)
    r_c_patch = client.patch(f"/insumos/{ins_id}", json={"cantidad": 10.0}, headers=cliente_headers)
    r_c_delete = client.delete(f"/insumos/{ins_id}", headers=cliente_headers)
    
    print(f"  * Resultados obtenidos (Cliente):")
    print(f"    - GET /insumos/: Status {r_c_get.status_code} | Detalle: '{r_c_get.json().get('detail')}'")
    print(f"    - POST /insumos/: Status {r_c_post.status_code} | Detalle: '{r_c_post.json().get('detail')}'")
    print(f"    - PATCH /insumos/{ins_id}: Status {r_c_patch.status_code} | Detalle: '{r_c_patch.json().get('detail')}'")
    print(f"    - DELETE /insumos/{ins_id}: Status {r_c_delete.status_code} | Detalle: '{r_c_delete.json().get('detail')}'")
    
    assert r_c_get.status_code == 403
    assert r_c_post.status_code == 403
    assert r_c_patch.status_code == 403
    assert r_c_delete.status_code == 403
    print("  * Detalle de Validación: El rol Cliente fue bloqueado con éxito de cualquier interacción con insumos.")

    # PASO 3: Operador intenta operar
    print("\n--- PASO 3: Intentos de Acceso y Modificación por un Operador (Rol Operador) ---")
    print("  * Entrada: Un Operador realiza GET (permitido) e intentos de POST, PATCH y DELETE (restringidos).")
    print("  * Resultado esperado: GET debe retornar 200 (OK). POST, PATCH y DELETE deben retornar 403 (Forbidden).")
    r_o_get = client.get("/insumos/", headers=operador_headers)
    r_o_post = client.post("/insumos/", json=ins_data, headers=operador_headers)
    r_o_patch = client.patch(f"/insumos/{ins_id}", json={"cantidad": 10.0}, headers=operador_headers)
    r_o_delete = client.delete(f"/insumos/{ins_id}", headers=operador_headers)
    
    print(f"  * Resultados obtenidos (Operador):")
    print(f"    - GET /insumos/ (Ver listado): Status {r_o_get.status_code} (Éxito)")
    print(f"    - POST /insumos/ (Crear): Status {r_o_post.status_code} | Detalle: '{r_o_post.json().get('detail')}' (Bloqueado)")
    print(f"    - PATCH /insumos/{ins_id} (Actualizar): Status {r_o_patch.status_code} | Detalle: '{r_o_patch.json().get('detail')}' (Bloqueado)")
    print(f"    - DELETE /insumos/{ins_id} (Eliminar): Status {r_o_delete.status_code} | Detalle: '{r_o_delete.json().get('detail')}' (Bloqueado)")
    
    assert r_o_get.status_code == 200
    assert r_o_post.status_code == 403
    assert r_o_patch.status_code == 403
    assert r_o_delete.status_code == 403
    print("  * Detalle de Validación: Operador puede ver insumos pero no tiene permisos para modificarlos o crearlos.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_control_alerta_stock_insumos(client, admin_headers):
    """Verifica la lógica de alerta cuando el stock cae debajo del mínimo configurado."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE TRAZABILIDAD: Alerta de Stock Mínimo de Insumos (test_control_alerta_stock_insumos)")
    print("="*80)

    # PASO 1: Crear insumo con stock bajo el mínimo
    ins_data = {
        "nombre": "Quita Manchas Fuerte",
        "cantidad": 15.0,
        "cantidad_alerta": 20.0,
        "costo_actual": 900.0
    }
    print("\n--- PASO 1: Crear Insumo con Stock Inicial Bajo el Mínimo Configurado ---")
    print(f"  * Entrada: POST /insumos/ con Datos = {ins_data} (Stock = 15.0 | Alerta = 20.0)")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y la condición de alerta (cantidad <= cantidad_alerta) debe ser True.")
    response = client.post("/insumos/", json=ins_data, headers=admin_headers)
    assert response.status_code == 201
    ins_json = response.json()
    ins_id = ins_json["id"]

    # Evaluar condición de alerta (cantidad <= cantidad_alerta)
    alerta_activa_1 = ins_json["cantidad"] <= ins_json["cantidad_alerta"]
    print(f"  * Resultado obtenido: Status Code = {response.status_code}")
    print(f"    - Stock Actual: {ins_json['cantidad']} unidades")
    print(f"    - Umbral de Alerta: {ins_json['cantidad_alerta']} unidades")
    print(f"    - ¿Alerta Activa?: {alerta_activa_1} (Esperado: True)")
    assert alerta_activa_1 is True
    print("  * Detalle de Validación: La lógica de alerta por stock mínimo se activó correctamente al estar la cantidad por debajo del límite.")

    # PASO 2: Actualizar stock para que supere el mínimo
    update_data = {"cantidad": 50.0}
    print("\n--- PASO 2: Aumentar Stock para Superar el Mínimo ---")
    print(f"  * Entrada: PATCH /insumos/{ins_id} con Datos = {update_data} (Nuevo Stock = 50.0 | Alerta = 20.0)")
    print("  * Resultado esperado: Código HTTP 200 (OK) y la condición de alerta (cantidad <= cantidad_alerta) debe cambiar a False.")
    response_up = client.patch(f"/insumos/{ins_id}", json=update_data, headers=admin_headers)
    assert response_up.status_code == 200
    ins_up_json = response_up.json()
    
    alerta_activa_2 = ins_up_json["cantidad"] <= ins_up_json["cantidad_alerta"]
    print(f"  * Resultado obtenido: Status Code = {response_up.status_code}")
    print(f"    - Stock Actualizado: {ins_up_json['cantidad']} unidades")
    print(f"    - Umbral de Alerta: {ins_up_json['cantidad_alerta']} unidades")
    print(f"    - ¿Alerta Activa?: {alerta_activa_2} (Esperado: False)")
    assert alerta_activa_2 is False
    print("  * Detalle de Validación: La alerta se desactivó correctamente una vez repuesto el stock por encima del umbral mínimo.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
