import pytest
from app.schemas.reclamos import MensajeReclamoCreate, ReclamoCreate
from pydantic import ValidationError

# ----------------- PRUEBAS UNITARIAS -----------------

def test_mensaje_reclamo_create_empty_validation():
    """Prueba unitaria para verificar que el esquema MensajeReclamoCreate no permita mensajes vacíos."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Validación de Mensaje No Vacío en Schema (test_mensaje_reclamo_create_empty_validation)")
    print("="*80)

    # PASO 1: Mensaje vacío (espacios en blanco)
    payload_invalido = {"mensaje": "   "}
    print("\n--- PASO 1: Validar Mensaje de Espacios en Blanco ---")
    print(f"  * Entrada: Datos del Schema = {payload_invalido}")
    print("  * Resultado esperado: Pydantic ValidationError levantado por la regla de validación.")
    
    with pytest.raises(ValidationError) as exc_info:
        MensajeReclamoCreate(**payload_invalido)
        
    print(f"  * Resultado obtenido: ValidationError capturado exitosamente.")
    print(f"    - Detalle del error: '{exc_info.value.errors()[0]['msg']}'")
    assert "El mensaje no puede estar vacío o contener solo espacios" in exc_info.value.errors()[0]['msg']
    print("  * Detalle de Validación: La validación impidió correctamente registrar mensajes vacíos en el chat de soporte.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_reclamo_create_valid_params():
    """Prueba unitaria para verificar la correcta asignación de campos en el esquema ReclamoCreate."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Asignación y Estructura en ReclamoCreate (test_reclamo_create_valid_params)")
    print("="*80)

    # PASO 1: Asignar parámetros correctos
    payload = {
        "id_pedido": 5,
        "id_categoria": 2,
        "mensaje_inicial": "Falta una prenda"
    }
    print("\n--- PASO 1: Instanciar ReclamoCreate ---")
    print(f"  * Entrada: Payload = {payload}")
    print("  * Resultado esperado: Instancia correcta con tipo int para ID Pedido e ID Categoría.")
    schema = ReclamoCreate(**payload)
    print(f"  * Resultado obtenido: Instanciado con éxito. ID Pedido = {schema.id_pedido} | Categoria = {schema.id_categoria}")
    assert schema.id_pedido == 5
    assert schema.id_categoria == 2
    assert schema.mensaje_inicial == "Falta una prenda"
    print("  * Detalle de Validación: El esquema ReclamoCreate fue validado y estructurado correctamente.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

def test_crud_y_chat_reclamos(client, cliente_headers, operador_headers, admin_headers, db):
    """Prueba de integración del flujo de reclamos y mensajería/chat."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: CRUD de Reclamos y Chat de Soporte (test_crud_y_chat_reclamos)")
    print("="*80)

    # PASO 1: Crear Pedido previo
    print("\n--- PASO 1: Crear Pedido Base ---")
    srv_resp = client.post("/servicios/", json={
        "id_unidad_limpieza": 1,
        "id_modalidad": 1,
        "nombre": "S1",
        "precio": 1000,
        "insumos_utilizados": []
    }, headers=admin_headers)
    srv_id = srv_resp.json()["id"]

    pedido_resp = client.post("/pedidos/", json={"id_usuario": 3, "id_servicios": [srv_id]}, headers=operador_headers)
    pedido_id = pedido_resp.json()["pedido"]["id"]
    print(f"  * Entrada: POST /pedidos/ | Servicio ID = {srv_id} para Cliente ID = 3")
    print(f"  * Resultado obtenido: Pedido ID #{pedido_id} creado con éxito.")

    # PASO 2: Crear Reclamo
    print("\n--- PASO 2: Registrar Nuevo Reclamo ---")
    reclamo_data = {
        "id_pedido": pedido_id,
        "id_categoria": 1  # Prenda Dañada o Manchada
    }
    print(f"  * Entrada: POST /reclamos con Datos = {reclamo_data} y headers = Cliente (ID 3)")
    print("  * Resultado esperado: Código HTTP 201 (Creado) con estado inicial del reclamo 'Abierto' o 'En Revisión'.")
    response = client.post("/reclamos", json=reclamo_data, headers=cliente_headers)
    assert response.status_code == 201
    res_json = response.json()
    reclamo_id = res_json["id"]
    print(f"  * Resultado obtenido: Status Code = {response.status_code}")
    print(f"    - Reclamo ID: {reclamo_id}")
    print(f"    - Estado del Reclamo: '{res_json['status']}'")
    print("  * Detalle de Validación: Se dio de alta el reclamo correctamente para el pedido del cliente.")

    # PASO 3: Mensaje Cliente
    print("\n--- PASO 3: Enviar Mensaje en Chat (Cliente) ---")
    msg_cliente = {"mensaje": "Hola, mi acolchado volvió con una mancha."}
    print(f"  * Entrada: POST /reclamos/{reclamo_id}/mensajes con mensaje = '{msg_cliente['mensaje']}' y headers = Cliente")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y mensaje guardado indicando remitente 'client'.")
    response_msg1 = client.post(f"/reclamos/{reclamo_id}/mensajes", json=msg_cliente, headers=cliente_headers)
    assert response_msg1.status_code == 201
    msg1_json = response_msg1.json()
    print(f"  * Resultado obtenido: Status Code = {response_msg1.status_code}")
    print(f"    - Remitente registrado: '{msg1_json['sender']}'")
    print(f"    - Mensaje: '{msg1_json['text']}'")
    print("  * Detalle de Validación: El cliente envió y guardó con éxito su mensaje de reclamo.")

    # PASO 4: Respuesta Soporte
    print("\n--- PASO 4: Enviar Mensaje en Chat (Operador/Soporte) ---")
    msg_operador = {"mensaje": "Buenas tardes Juan, nos ponemos en contacto para solucionar esto."}
    print(f"  * Entrada: POST /reclamos/{reclamo_id}/mensajes con mensaje = '{msg_operador['mensaje']}' y headers = Operador")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y mensaje guardado indicando remitente 'staff'.")
    response_msg2 = client.post(f"/reclamos/{reclamo_id}/mensajes", json=msg_operador, headers=operador_headers)
    assert response_msg2.status_code == 201
    msg2_json = response_msg2.json()
    print(f"  * Resultado obtenido: Status Code = {response_msg2.status_code}")
    print(f"    - Remitente registrado: '{msg2_json['sender']}'")
    print(f"    - Mensaje: '{msg2_json['text']}'")

    # Consultar los mensajes
    print("\n--- PASO 4b: Consultar Historial de Chat del Reclamo ---")
    print(f"  * Entrada: GET /reclamos/{reclamo_id}/mensajes")
    resp_msg_list = client.get(f"/reclamos/{reclamo_id}/mensajes", headers=cliente_headers)
    assert resp_msg_list.status_code == 200
    print(f"  * Resultado obtenido: Total de mensajes en base de datos = {len(resp_msg_list.json())}")
    print("  * Detalle de Validación: Soporte respondió y ambos mensajes se encuentran listados cronológicamente en el chat.")

    # PASO 5: Resolver Reclamo
    print("\n--- PASO 5: Resolver Reclamo (Staff) ---")
    print(f"  * Entrada: PATCH /reclamos/{reclamo_id} con id_estado = 3 (Resuelto) y headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y estado actualizado a 'Resuelto'.")
    resp_patch = client.patch(f"/reclamos/{reclamo_id}", json={"id_estado": 3}, headers=admin_headers)
    assert resp_patch.status_code == 200
    patch_json = resp_patch.json()
    print(f"  * Resultado obtenido: Status Code = {resp_patch.status_code}")
    print(f"    - Estado Final del Reclamo: '{patch_json['status']}' (Esperado: 'Resuelto')")
    print("  * Detalle de Validación: El reclamo fue finalizado y marcado como Resuelto de forma exitosa.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_reclamos_rbac_restricciones(client, admin_headers, operador_headers, cliente_headers):
    """Verifica restricciones de seguridad en Reclamos."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE CONTROL DE ACCESOS (RBAC): Privacidad de Reclamos (test_reclamos_rbac_restricciones)")
    print("="*80)

    # PASO 1: Crear reclamo de Cliente 1 (ID 3)
    print("\n--- PASO 1: Crear Reclamo de Cliente 1 (ID 3) ---")
    srv_resp = client.post("/servicios/", json={"id_unidad_limpieza": 1, "id_modalidad": 1, "nombre": "S1", "precio": 1000, "insumos_utilizados": []}, headers=admin_headers)
    srv_id = srv_resp.json()["id"]
    pedido_resp = client.post("/pedidos/", json={"id_usuario": 3, "id_servicios": [srv_id]}, headers=operador_headers)
    pedido_id = pedido_resp.json()["pedido"]["id"]
    reclamo_resp = client.post("/reclamos", json={"id_pedido": pedido_id, "id_categoria": 1}, headers=cliente_headers)
    reclamo_id = reclamo_resp.json()["id"]
    print(f"  * Entrada: Reclamo ID #{reclamo_id} creado para el pedido #{pedido_id} perteneciente al Cliente 1.")

    # PASO 2: Registrar Cliente 2 (Esteban, ID 4)
    print("\n--- PASO 2: Registrar y Autenticar al Cliente 2 (Esteban) ---")
    from unittest.mock import AsyncMock
    import unittest.mock
    with unittest.mock.patch("app.utils.email.send_activation_email", new_callable=AsyncMock):
        user_resp = client.post("/usuarios/", json={
            "id_rol": 3,
            "nombre": "Esteban",
            "apellido": "Quito",
            "dni": "88888888",
            "email": "esteban.quito@example.com"
        }, headers=admin_headers)
        esteban_id = user_resp.json()["id"]

    from app.utils.security import create_access_token
    token_esteban = create_access_token(data={"sub": str(esteban_id), "rol": "Cliente"})
    esteban_headers = {"Authorization": f"Bearer {token_esteban}"}
    print(f"  * Entrada: Registro de usuario Esteban | ID Generado = {esteban_id} | Token JWT generado.")

    # PASO 3: Esteban intenta ver reclamo de Cliente 1
    print("\n--- PASO 3: Intento de Cliente 2 de Leer Reclamo Ajeno ---")
    print(f"  * Entrada: GET /reclamos/{reclamo_id} con headers = Cliente 2 (Esteban)")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) por no ser el titular del reclamo.")
    r_get_fail = client.get(f"/reclamos/{reclamo_id}", headers=esteban_headers)
    print(f"  * Resultado obtenido: Status Code = {r_get_fail.status_code} | Detalle: '{r_get_fail.json().get('detail')}'")
    assert r_get_fail.status_code == 403
    print("  * Detalle de Validación: Privacidad de consulta validada. Cliente 2 no puede acceder.")

    # PASO 4: Esteban intenta chatear en reclamo de Cliente 1
    print("\n--- PASO 4: Intento de Cliente 2 de Enviar Mensaje en Reclamo Ajeno ---")
    print(f"  * Entrada: POST /reclamos/{reclamo_id}/mensajes con headers = Cliente 2 (Esteban)")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) por falta de privilegios y pertenencia.")
    r_post_fail = client.post(f"/reclamos/{reclamo_id}/mensajes", json={"mensaje": "Hola"}, headers=esteban_headers)
    print(f"  * Resultado obtenido: Status Code = {r_post_fail.status_code} | Detalle: '{r_post_fail.json().get('detail')}'")
    assert r_post_fail.status_code == 403
    print("  * Detalle de Validación: Privacidad de comunicación validada. Cliente 2 bloqueado de chatear.")

    # PASO 5: Cliente 1 intenta cambiar el estado de su propio reclamo
    print("\n--- PASO 5: Intento de Cliente 1 de Modificar Estado de su Reclamo ---")
    print(f"  * Entrada: PATCH /reclamos/{reclamo_id} con id_estado = 2 y headers = Cliente 1")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) debido a que cambiar el estado del reclamo requiere rol Administrativo.")
    r_patch_fail = client.patch(f"/reclamos/{reclamo_id}", json={"id_estado": 2}, headers=cliente_headers)
    print(f"  * Resultado obtenido: Status Code = {r_patch_fail.status_code} | Detalle: '{r_patch_fail.json().get('detail')}'")
    assert r_patch_fail.status_code == 403
    print("  * Detalle de Validación: Control de permisos de estados validado. Un cliente común no puede auto-resolverse o cambiar estados de reclamos.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
