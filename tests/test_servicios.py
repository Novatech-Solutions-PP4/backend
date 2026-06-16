import pytest
from app.schemas.servicios import ServicioCreate, ServicioBase
from pydantic import ValidationError

# ----------------- PRUEBAS UNITARIAS -----------------

def test_servicio_create_schema_parsing():
    """Prueba unitaria para verificar la inicialización y tipado correcto del esquema ServicioCreate."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Estructura y Parsing de ServicioCreate (test_servicio_create_schema_parsing)")
    print("="*80)

    # PASO 1: Cargar datos válidos
    payload = {
        "nombre": "Secado Express",
        "precio": 1200.0,
        "id_unidad_limpieza": 1,
        "id_modalidad": 2,
        "insumos_utilizados": [
            {"id_insumo": 10, "cantidad_utilizada": 1.5}
        ]
    }
    print("\n--- PASO 1: Instanciar Schema con Insumos Utilizados ---")
    print(f"  * Entrada: Payload = {payload}")
    print("  * Resultado esperado: Instancia correcta con sub-esquemas de insumos inicializados.")
    schema = ServicioCreate(**payload)
    print(f"  * Resultado obtenido: Instancia creada. Servicio = '{schema.nombre}' | Insumos asociados = {len(schema.insumos_utilizados)}")
    assert schema.nombre == "Secado Express"
    assert schema.insumos_utilizados[0].id_insumo == 10
    assert schema.insumos_utilizados[0].cantidad_utilizada == 1.5
    print("  * Detalle de Validación: La estructura de insumos anidados fue mapeada y tipada correctamente.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_servicio_precio_validation():
    """Prueba unitaria para verificar la validación de precio no negativo en ServicioBase."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Validación de Precio No Negativo (test_servicio_precio_validation)")
    print("="*80)

    # PASO 1: Precio negativo
    payload_invalido = {
        "nombre": "Secado Extra",
        "precio": -250.0
    }
    print("\n--- PASO 1: Validar Precio Negativo ---")
    print(f"  * Entrada: Datos del Schema = {payload_invalido}")
    print("  * Resultado esperado: Pydantic ValidationError levantado debido a la regla de negocio.")
    
    with pytest.raises(ValidationError) as exc_info:
        ServicioBase(**payload_invalido)

    print(f"  * Resultado obtenido: ValidationError capturado exitosamente.")
    print(f"    - Detalle del error: '{exc_info.value.errors()[0]['msg']}'")
    assert "El precio del servicio no puede ser negativo" in exc_info.value.errors()[0]['msg']
    print("  * Detalle de Validación: Se impidió correctamente el registro de servicios con precios negativos.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

def test_crud_servicios_por_administrador(client, admin_headers):
    """Verifica que el Administrador pueda realizar el CRUD de servicios."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: CRUD de Servicios por Administrador (test_crud_servicios_por_administrador)")
    print("="*80)

    # PASO 1: Crear insumo previo
    print("\n--- PASO 1: Crear Insumo Asociado ---")
    ins_data = {
        "nombre": "Detergente Líquido",
        "cantidad": 500.0,
        "cantidad_alerta": 50.0,
        "costo_actual": 1500.0
    }
    print(f"  * Entrada: POST /insumos/ con Datos = {ins_data}")
    print("  * Resultado esperado: Código HTTP 201 (Creado) e ID de insumo retornado.")
    ins_resp = client.post("/insumos/", json=ins_data, headers=admin_headers)
    assert ins_resp.status_code == 201
    ins_id = ins_resp.json()["id"]
    print(f"  * Resultado obtenido: Status Code = {ins_resp.status_code} | Insumo ID = {ins_id}")
    print("  * Detalle de Validación: Insumo creado correctamente para ser asignado al servicio.")

    # PASO 2: Crear Servicio
    print("\n--- PASO 2: Crear Servicio ---")
    srv_data = {
        "id_unidad_limpieza": 1,
        "id_modalidad": 2,
        "nombre": "Lavado Algodón Estándar",
        "precio": 3500.0,
        "insumos_utilizados": [
            {
                "id_insumo": ins_id,
                "cantidad_utilizada": 150.0
            }
        ]
    }
    print(f"  * Entrada: POST /servicios/ con Datos = {srv_data}")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y retornar el servicio con ID único.")
    response = client.post("/servicios/", json=srv_data, headers=admin_headers)
    assert response.status_code == 201
    res_json = response.json()
    srv_id = res_json["id"]
    print(f"  * Resultado obtenido: Status Code = {response.status_code}")
    print(f"    - ID Servicio: {srv_id}")
    print(f"    - Nombre Servicio: '{res_json['nombre']}' | Precio = ${res_json['precio']}")
    print("  * Detalle de Validación: Servicio registrado y guardado con sus relaciones correspondientes.")

    # PASO 3: Leer Servicio
    print("\n--- PASO 3: Leer Servicio ---")
    print(f"  * Entrada: GET /servicios/{srv_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y obtener el nombre de unidad de limpieza y modalidad.")
    response_get = client.get(f"/servicios/{srv_id}", headers=admin_headers)
    assert response_get.status_code == 200
    get_json = response_get.json()
    print(f"  * Resultado obtenido: Status Code = {response_get.status_code}")
    print(f"    - Unidad de Limpieza: '{get_json['unidad_limpieza']['nombre']}'")
    print(f"    - Modalidad de Servicio: '{get_json['modalidad']['nombre']}'")
    print("  * Detalle de Validación: Los datos y detalles de relaciones coinciden con la base de datos.")

    # PASO 4: Actualizar Servicio
    print("\n--- PASO 4: Actualizar Servicio ---")
    srv_update = {
        "nombre": "Lavado Algodón Premium",
        "precio": 4200.0,
        "insumos_utilizados": []
    }
    print(f"  * Entrada: PATCH /servicios/{srv_id} con Datos a actualizar = {srv_update}")
    print("  * Resultado esperado: Código HTTP 200 (OK) y el nuevo precio debe ser $4200.0.")
    response_patch = client.patch(f"/servicios/{srv_id}", json=srv_update, headers=admin_headers)
    assert response_patch.status_code == 200
    patch_json = response_patch.json()
    print(f"  * Resultado obtenido: Status Code = {response_patch.status_code}")
    print(f"    - Nuevo Nombre: '{patch_json['nombre']}' (Esperado: 'Lavado Algodón Premium')")
    print(f"    - Nuevo Precio: ${patch_json['precio']} (Esperado: 4200.0)")
    print("  * Detalle de Validación: El servicio se actualizó correctamente en el sistema.")
    assert patch_json["nombre"] == "Lavado Algodón Premium"
    assert patch_json["precio"] == 4200.0

    # PASO 5: Eliminar Servicio (baja lógica)
    print("\n--- PASO 5: Eliminar Servicio (Baja Lógica) ---")
    print(f"  * Entrada: DELETE /servicios/{srv_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y el campo 'baja' en True.")
    response_delete = client.delete(f"/servicios/{srv_id}", headers=admin_headers)
    assert response_delete.status_code == 200
    delete_json = response_delete.json()
    print(f"  * Resultado obtenido: Status Code = {response_delete.status_code}")
    print(f"    - baja = {delete_json['baja']} (Esperado: True)")
    print("  * Detalle de Validación: El servicio fue marcado como inactivo correctamente.")
    assert delete_json["baja"] is True

    # PASO 6: Intentar obtener el servicio borrado
    print("\n--- PASO 6: Intentar Consultar Servicio de Baja ---")
    print(f"  * Entrada: GET /servicios/{srv_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 404 (Not Found) debido a que tiene la baja lógica activa.")
    response_get_del = client.get(f"/servicios/{srv_id}", headers=admin_headers)
    print(f"  * Resultado obtenido: Status Code = {response_get_del.status_code}")
    print(f"    - Mensaje de Detalle: '{response_get_del.json().get('detail')}'")
    print("  * Detalle de Validación: Se comprueba la inactividad del servicio al no ser accesible mediante consultas ordinarias.")
    assert response_get_del.status_code == 404

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_servicios_rbac_restricciones(client, admin_headers, operador_headers, cliente_headers):
    """Verifica restricciones de roles en Servicios."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE CONTROL DE ACCESOS (RBAC): Restricciones sobre Servicios (test_servicios_rbac_restricciones)")
    print("="*80)

    # PASO 1: Crear servicio base como admin
    srv_data = {
        "id_unidad_limpieza": 2,
        "id_modalidad": 3,
        "nombre": "Limpieza Acolchado Plumas",
        "precio": 12000.0,
        "insumos_utilizados": []
    }
    print("\n--- PASO 1: Crear Servicio Base por el Administrador ---")
    resp_create = client.post("/servicios/", json=srv_data, headers=admin_headers)
    srv_id = resp_create.json()["id"]
    print(f"  * Entrada: POST /servicios/ por Admin | Servicio: '{srv_data['nombre']}'")
    print(f"  * Resultado obtenido: ID asignado = {srv_id}")

    # PASO 2: Clientes y Operadores PUEDEN consultar (GET)
    print("\n--- PASO 2: Consultar Servicios por Cliente y Operador (Rol Staff/Cliente) ---")
    print("  * Entrada: Clientes y Operadores realizan solicitudes GET para ver la lista de servicios.")
    print("  * Resultado esperado: Código HTTP 200 (OK) en ambas consultas.")
    r_c_get = client.get("/servicios/", headers=cliente_headers)
    r_o_get = client.get(f"/servicios/{srv_id}", headers=operador_headers)
    print(f"  * Resultados obtenidos:")
    print(f"    - Lectura por Cliente: Status Code = {r_c_get.status_code} (Éxito)")
    print(f"    - Lectura por Operador: Status Code = {r_o_get.status_code} (Éxito)")
    assert r_c_get.status_code == 200
    assert r_o_get.status_code == 200
    print("  * Detalle de Validación: Tanto los clientes como los operadores tienen autorización para visualizar el catálogo de servicios.")

    # PASO 3: Clientes NO pueden modificar, crear o borrar (403)
    print("\n--- PASO 3: Intentos de Modificación por un Cliente (Rol Cliente) ---")
    print("  * Entrada: Un Cliente intenta realizar POST, PATCH y DELETE sobre servicios.")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) en todas las operaciones de modificación.")
    r_c_post = client.post("/servicios/", json=srv_data, headers=cliente_headers)
    r_c_patch = client.patch(f"/servicios/{srv_id}", json={"precio": 13000.0}, headers=cliente_headers)
    r_c_delete = client.delete(f"/servicios/{srv_id}", headers=cliente_headers)
    
    print(f"  * Resultados obtenidos (Cliente):")
    print(f"    - POST /servicios/ (Crear): Status {r_c_post.status_code} | Detalle: '{r_c_post.json().get('detail')}'")
    print(f"    - PATCH /servicios/{srv_id} (Actualizar): Status {r_c_patch.status_code} | Detalle: '{r_c_patch.json().get('detail')}'")
    print(f"    - DELETE /servicios/{srv_id} (Eliminar): Status {r_c_delete.status_code} | Detalle: '{r_c_delete.json().get('detail')}'")
    
    assert r_c_post.status_code == 403
    assert r_c_patch.status_code == 403
    assert r_c_delete.status_code == 403
    print("  * Detalle de Validación: El rol Cliente fue denegado de realizar modificaciones en el catálogo de servicios.")

    # PASO 4: Operadores NO pueden modificar, crear o borrar (403)
    print("\n--- PASO 4: Intentos de Modificación por un Operador (Rol Operador) ---")
    print("  * Entrada: Un Operador intenta realizar POST, PATCH y DELETE sobre servicios.")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) en todas las operaciones de modificación.")
    r_o_post = client.post("/servicios/", json=srv_data, headers=operador_headers)
    r_o_patch = client.patch(f"/servicios/{srv_id}", json={"precio": 13000.0}, headers=operador_headers)
    r_o_delete = client.delete(f"/servicios/{srv_id}", headers=operador_headers)

    print(f"  * Resultados obtenidos (Operador):")
    print(f"    - POST /servicios/ (Crear): Status {r_o_post.status_code} | Detalle: '{r_o_post.json().get('detail')}'")
    print(f"    - PATCH /servicios/{srv_id} (Actualizar): Status {r_o_patch.status_code} | Detalle: '{r_o_patch.json().get('detail')}'")
    print(f"    - DELETE /servicios/{srv_id} (Eliminar): Status {r_o_delete.status_code} | Detalle: '{r_o_delete.json().get('detail')}'")

    assert r_o_post.status_code == 403
    assert r_o_patch.status_code == 403
    assert r_o_delete.status_code == 403
    print("  * Detalle de Validación: El rol Operador tiene acceso de solo lectura, por ende se le bloquea cualquier intento de edición o borrado.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
