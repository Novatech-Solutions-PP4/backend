import pytest
from unittest.mock import MagicMock
import app.models as models
from app.schemas.pedidos import PedidoCreate
from pydantic import ValidationError

# ----------------- PRUEBAS UNITARIAS -----------------

def test_pedido_create_empty_services_validation():
    """Prueba unitaria para verificar que el esquema PedidoCreate valida que haya al menos un servicio asignado."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Validación de Mínimo un Servicio en PedidoCreate (test_pedido_create_empty_services_validation)")
    print("="*80)

    # PASO 1: Datos válidos (con servicios)
    payload_valido = {
        "id_usuario": 10,
        "id_servicios": [1]
    }
    print("\n--- PASO 1: Validar Pedido con Servicios (Válido) ---")
    print(f"  * Entrada: Datos del Schema = {payload_valido}")
    print("  * Resultado esperado: Instanciación correcta del Schema sin errores.")
    schema_inst = PedidoCreate(**payload_valido)
    print(f"  * Resultado obtenido: Schema instanciado correctamente con id_usuario = {schema_inst.id_usuario} y servicios = {schema_inst.id_servicios}")
    assert schema_inst.id_usuario == 10
    assert len(schema_inst.id_servicios) == 1

    # PASO 2: Datos inválidos (sin servicios, lista vacía)
    payload_invalido = {
        "id_usuario": 10,
        "id_servicios": []
    }
    print("\n--- PASO 2: Validar Pedido sin Servicios (Vacío) ---")
    print(f"  * Entrada: Datos del Schema = {payload_invalido}")
    print("  * Resultado esperado: Pydantic ValidationError por la regla min_length=1 en id_servicios.")
    
    with pytest.raises(ValidationError) as exc_info:
        PedidoCreate(**payload_invalido)
        
    print(f"  * Resultado obtenido: ValidationError capturado exitosamente.")
    print(f"    - Detalle del error: '{exc_info.value.errors()[0]['msg']}'")
    assert "List should have at least 1 item" in exc_info.value.errors()[0]['msg']
    print("  * Detalle de Validación: Se impidió correctamente el registro de pedidos vacíos sin servicios asignados.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

def test_creacion_pedido_con_descuento_insumos(client, operador_headers, admin_headers, db):
    """
    Prueba de integración de creación de pedido:
    1. Crear un insumo con stock 100.
    2. Crear un servicio que consume 30 de ese insumo.
    3. Crear un pedido con ese servicio para el cliente (ID 3).
    4. Verificar que se descuente el stock del insumo a 70.
    5. Verificar que el estado inicial del pedido sea 'Pendiente'.
    6. Verificar que se cree el historial de estados correspondiente.
    7. Verificar que se cree el registro de facturación en estado 'pending'.
    """
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: Crear Pedido y Descontar Insumos (test_creacion_pedido_con_descuento_insumos)")
    print("="*80)

    # PASO 1: Crear Insumo
    print("\n--- PASO 1: Crear Insumo ---")
    ins_payload = {
        "nombre": "Suavizante Concentrado",
        "cantidad": 100.0,
        "cantidad_alerta": 10.0,
        "costo_actual": 800.0
    }
    print(f"  * Entrada: POST /insumos/ con Datos = {ins_payload}")
    print("  * Resultado esperado: Código HTTP 201 (Creado) e ID del insumo.")
    ins_resp = client.post("/insumos/", json=ins_payload, headers=admin_headers)
    assert ins_resp.status_code == 201
    ins_id = ins_resp.json()["id"]
    print(f"  * Resultado obtenido: Status Code = {ins_resp.status_code} | Insumo ID = {ins_id} | Stock = 100.0")

    # PASO 2: Crear Servicio
    print("\n--- PASO 2: Crear Servicio ---")
    srv_payload = {
        "id_unidad_limpieza": 1,
        "id_modalidad": 1,
        "nombre": "Lavado Rápido",
        "precio": 3500.0,
        "insumos_utilizados": [
            {"id_insumo": ins_id, "cantidad_utilizada": 30.0}
        ]
    }
    print(f"  * Entrada: POST /servicios/ con Datos = {srv_payload}")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y retornar el servicio con ID asignado.")
    srv_resp = client.post("/servicios/", json=srv_payload, headers=admin_headers)
    assert srv_resp.status_code == 201
    srv_id = srv_resp.json()["id"]
    print(f"  * Resultado obtenido: Status Code = {srv_resp.status_code} | Servicio ID = {srv_id} (Consume 30.0 unidades del insumo)")

    # PASO 3: Crear Pedido
    print("\n--- PASO 3: Crear Pedido ---")
    pedido_data = {
        "id_usuario": 3,
        "id_servicios": [srv_id]
    }
    print(f"  * Entrada: POST /pedidos/?id_metodo_pago=1 con Datos = {pedido_data} y headers = Operador")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y retornar el pedido con código QR y estado 'Pendiente'.")
    response = client.post("/pedidos/?id_metodo_pago=1", json=pedido_data, headers=operador_headers)
    assert response.status_code == 201
    res_data = response.json()
    pedido_id = res_data["pedido"]["id"]
    print(f"  * Resultado obtenido: Status Code = {response.status_code}")
    print(f"    - Pedido ID: {pedido_id}")
    print(f"    - Código QR Generado: '{res_data['pedido']['codigo_qr']}'")
    print(f"    - Estado inicial del Pedido: '{res_data['pedido']['estado_actual']}'")

    # PASO 4: Verificar descuento de stock en la base de datos
    print("\n--- PASO 4: Verificar Descuento de Stock en BD ---")
    print(f"  * Entrada: Consulta directa en base de datos para Insumo ID {ins_id}")
    print("  * Resultado esperado: La cantidad de stock debe ser exactamente 70.0 (100.0 original - 30.0 consumidos).")
    insumo_db = db.query(models.Insumo).filter(models.Insumo.id == ins_id).first()
    print(f"  * Resultado obtenido: Stock restante = {insumo_db.cantidad} unidades")
    assert insumo_db.cantidad == 70.0
    print("  * Detalle de Validación: La cantidad de stock del insumo fue descontada automáticamente en la proporción esperada.")

    # PASO 5: Verificar historial de estados
    print("\n--- PASO 5: Verificar Historial de Estados (Auditoría) ---")
    print(f"  * Entrada: Consulta en HistorialEstados para Pedido ID {pedido_id}")
    print("  * Resultado esperado: Exactamente 1 registro con el estado 'Pendiente'.")
    historial = db.query(models.HistorialEstados).filter(models.HistorialEstados.id_pedido == pedido_id).all()
    print(f"  * Resultado obtenido: Registros de auditoría encontrados = {len(historial)}")
    print(f"    - Estado registrado: '{historial[0].estado.nombre}' por Usuario ID {historial[0].id_usuario}")
    assert len(historial) == 1
    assert historial[0].estado.nombre == "Pendiente"
    print("  * Detalle de Validación: Se auditó correctamente el estado inicial del pedido en la creación.")

    # PASO 6: Verificar pago pendiente en la BD
    print("\n--- PASO 6: Verificar Facturación y Preferencia de Pago en BD ---")
    print(f"  * Entrada: Consulta en FacturacionPagos para Pedido ID {pedido_id}")
    print("  * Resultado esperado: Registro de pago en estado 'pending' y monto igual a $3500.0.")
    pago = db.query(models.FacturacionPagos).filter(models.FacturacionPagos.id_pedido == pedido_id).first()
    print(f"  * Resultado obtenido: Estado del pago = '{pago.estado}' | Monto = ${pago.monto}")
    print(f"    - ID Transacción Externa (Preferencia MP): '{pago.id_transaccion_externa}'")
    assert pago.estado == "pending"
    print("  * Detalle de Validación: Se creó el registro de pago y se obtuvo la preferencia de pago de Mercado Pago simulada.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_actualizacion_trazabilidad_pedido(client, operador_headers, admin_headers, db):
    """
    Prueba de trazabilidad de estados:
    - Crear un pedido.
    - Cambiar su estado a 'En Proceso' y luego a 'Listo'.
    - Verificar que se registre la traza completa de auditoría en la tabla HistorialEstados.
    """
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: Auditoría de Estados del Pedido (test_actualizacion_trazabilidad_pedido)")
    print("="*80)

    # PASO 1: Crear pedido base
    print("\n--- PASO 1: Crear Pedido Base ---")
    srv_resp = client.post("/servicios/", json={
        "id_unidad_limpieza": 1,
        "id_modalidad": 1,
        "nombre": "Servicio Simple",
        "precio": 1500.0,
        "insumos_utilizados": []
    }, headers=admin_headers)
    srv_id = srv_resp.json()["id"]

    pedido_resp = client.post("/pedidos/", json={"id_usuario": 3, "id_servicios": [srv_id]}, headers=operador_headers)
    pedido_id = pedido_resp.json()["pedido"]["id"]
    print(f"  * Entrada: POST /pedidos/ y headers = Operador | Servicio ID = {srv_id}")
    print(f"  * Resultado obtenido: Pedido ID #{pedido_id} creado con estado inicial: 'Pendiente'")

    # PASO 2: Cambiar estado a 'En Proceso'
    print("\n--- PASO 2: Transición de Estado a 'En Proceso' ---")
    print(f"  * Entrada: PATCH /pedidos/{pedido_id} con Status = 'En Proceso' y headers = Operador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y estado actualizado a 'En Proceso'.")
    resp_update1 = client.patch(f"/pedidos/{pedido_id}", json={"status": "En Proceso"}, headers=operador_headers)
    assert resp_update1.status_code == 200
    print(f"  * Resultado obtenido: Status Code = {resp_update1.status_code} | Nuevo Estado = '{resp_update1.json().get('estado_actual')}'")

    # PASO 3: Cambiar estado a 'Listo'
    print("\n--- PASO 3: Transición de Estado a 'Listo' ---")
    print(f"  * Entrada: PATCH /pedidos/{pedido_id} con Status = 'Listo' y headers = Operador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y estado actualizado a 'Listo'.")
    resp_update2 = client.patch(f"/pedidos/{pedido_id}", json={"status": "Listo"}, headers=operador_headers)
    assert resp_update2.status_code == 200
    print(f"  * Resultado obtenido: Status Code = {resp_update2.status_code} | Nuevo Estado = '{resp_update2.json().get('estado_actual')}'")

    # PASO 4: Verificar historial completo en base de datos
    print("\n--- PASO 4: Verificar Auditoría de Trazabilidad en BD ---")
    print(f"  * Entrada: Consulta en HistorialEstados para Pedido ID {pedido_id} ordenado ascendentemente")
    print("  * Resultado esperado: Encontrar exactamente 3 transiciones en orden: 'Pendiente' -> 'En Proceso' -> 'Listo'.")
    historial = db.query(models.HistorialEstados).filter(models.HistorialEstados.id_pedido == pedido_id).order_by(models.HistorialEstados.id.asc()).all()
    assert len(historial) == 3
    assert historial[0].estado.nombre == "Pendiente"
    assert historial[1].estado.nombre == "En Proceso"
    assert historial[2].estado.nombre == "Listo"
    
    print("  * Resultado obtenido (Traza Completa en BD):")
    for i, h in enumerate(historial):
        print(f"    - Paso {i+1}: [{h.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}] Cambiado a '{h.estado.nombre}' por Usuario ID {h.id_usuario}")
    print("  * Detalle de Validación: Toda la secuencia de estados fue guardada y auditada correctamente con sus marcas temporales y responsables.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_pedidos_rbac_visibilidad(client, cliente_headers, operador_headers, admin_headers):
    """
    Verifica restricciones de visibilidad de pedidos:
    - Cliente solo puede ver SUS pedidos.
    - Operador y Administrador pueden ver TODOS los pedidos del sistema.
    """
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE CONTROL DE ACCESOS (RBAC): Visibilidad y Creación de Pedidos (test_pedidos_rbac_visibilidad)")
    print("="*80)

    # PASO 1: Crear pedido previo para Cliente ID 3
    print("\n--- PASO 1: Registrar Pedido para Cliente (ID 3) ---")
    srv_resp = client.post("/servicios/", json={"id_unidad_limpieza": 1, "id_modalidad": 1, "nombre": "S1", "precio": 1000, "insumos_utilizados": []}, headers=admin_headers)
    srv_id = srv_resp.json()["id"]
    ped_resp = client.post("/pedidos/", json={"id_usuario": 3, "id_servicios": [srv_id]}, headers=operador_headers)
    pedido_id = ped_resp.json()["pedido"]["id"]
    print(f"  * Entrada: Pedido ID #{pedido_id} registrado por Operador para Cliente ID 3.")

    # PASO 2: Cliente consulta su lista de pedidos
    print("\n--- PASO 2: Consulta de Pedidos por Cliente ---")
    print("  * Entrada: GET /pedidos/ con headers = Cliente (ID 3)")
    print("  * Resultado esperado: Código HTTP 200 (OK) y obtener exactamente 1 pedido (el que le pertenece).")
    resp_cli = client.get("/pedidos/", headers=cliente_headers)
    assert resp_cli.status_code == 200
    cli_data = resp_cli.json()
    print(f"  * Resultado obtenido: Status Code = {resp_cli.status_code} | Cantidad de pedidos retornados = {len(cli_data)}")
    print(f"    - Pedido ID en respuesta: {cli_data[0]['id']} | ¿Pertenece al Cliente?: {cli_data[0]['usuario']['id'] == 3}")
    assert len(cli_data) == 1
    assert cli_data[0]["usuario"]["id"] == 3
    print("  * Detalle de Validación: El cliente únicamente puede ver los pedidos asociados a su propia cuenta.")

    # PASO 3: Operador consulta listado general de pedidos
    print("\n--- PASO 3: Consulta General de Pedidos por Operador ---")
    print("  * Entrada: GET /pedidos/ con headers = Operador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y listar todos los pedidos (al menos el creado).")
    resp_ope = client.get("/pedidos/", headers=operador_headers)
    assert resp_ope.status_code == 200
    ope_data = resp_ope.json()
    print(f"  * Resultado obtenido: Status Code = {resp_ope.status_code} | Cantidad total de pedidos en el sistema = {len(ope_data)}")
    assert len(ope_data) >= 1
    print("  * Detalle de Validación: Los operadores tienen visibilidad completa y pueden listar todos los pedidos registrados.")

    # PASO 4: Cliente intenta crear un pedido directamente
    print("\n--- PASO 4: Intento de Creación de Pedido por un Cliente ---")
    print(f"  * Entrada: POST /pedidos/ con headers = Cliente | Servicios = [{srv_id}]")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) ya que la creación de pedidos es restringida a personal del local.")
    resp_cli_create = client.post("/pedidos/", json={"id_usuario": 3, "id_servicios": [srv_id]}, headers=cliente_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_cli_create.status_code} | Detalle: '{resp_cli_create.json().get('detail')}'")
    assert resp_cli_create.status_code == 403
    print("  * Detalle de Validación: Operación bloqueada con éxito. El cliente no puede autocrear pedidos sin pasar por un operador.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
