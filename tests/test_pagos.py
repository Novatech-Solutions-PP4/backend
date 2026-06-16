import pytest
import importlib
import app.models as models
from app.services import mercadopago as mp_original
from fastapi import HTTPException

# ----------------- PRUEBAS UNITARIAS -----------------

def test_crear_preferencia_sin_token(mocker):
    """Prueba unitaria para verificar que crear_preferencia_pago lanza un error HTTP 500 si no hay token de Mercado Pago."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Validación de Configuración en Mercado Pago (test_crear_preferencia_sin_token)")
    print("="*80)

    # PASO 1: Recargar el módulo para restaurar las funciones originales (deshacer el mock de conftest.py)
    importlib.reload(mp_original)

    # PASO 2: Remover token
    original_token = mp_original.MERCADOPAGO_ACCESS_TOKEN
    mp_original.MERCADOPAGO_ACCESS_TOKEN = ""
    print("\n--- PASO 1: Invocar Función sin Access Token ---")
    print("  * Entrada: crear_preferencia_pago con pedido_id = 1, monto = 500, email = 'test@example.com'")
    print("  * Resultado esperado: Levantar HTTPException con status_code 500 y detalle de configuración.")
    
    try:
        with pytest.raises(HTTPException) as exc_info:
            mp_original.crear_preferencia_pago(1, 500.0, "test@example.com")
            
        print(f"  * Resultado obtenido: HTTPException capturada con éxito.")
        print(f"    - Status Code: {exc_info.value.status_code}")
        print(f"    - Detalle: '{exc_info.value.detail}'")
        assert exc_info.value.status_code == 500
        assert "MERCADOPAGO_ACCESS_TOKEN no está configurado" in exc_info.value.detail
        print("  * Detalle de Validación: La función de cobro validó correctamente la falta de credenciales de API.")
    finally:
        mp_original.MERCADOPAGO_ACCESS_TOKEN = original_token

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)



# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

@pytest.fixture(autouse=False)
def mock_mercadopago_services(mocker):
    """Fixture para mockear las llamadas API de Mercado Pago en test_pagos."""
    mock_pref = mocker.patch("app.services.mercadopago.crear_preferencia_pago")
    mock_pref.return_value = {
        "preference_id": "pref_mock_pago_999",
        "init_point": "https://sandbox.mercadopago.com/checkout/mock"
    }
    
    mock_status = mocker.patch("app.services.mercadopago.obtener_estado_pago")
    mock_status.return_value = {
        "id_pago": "9876543210",
        "estado": "approved",
        "monto": 2500.0,
        "external_reference": "1"
    }
    return mock_pref, mock_status

def test_procesamiento_webhook_mercadopago_aprobado(client, admin_headers, operador_headers, db, mock_mercadopago_services):
    """Prueba el webhook de Mercado Pago (IPN) cuando el cobro es aprobado."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: Webhook Mercado Pago IPN Aprobado (test_procesamiento_webhook_mercadopago_aprobado)")
    print("="*80)

    # PASO 1: Crear servicio y pedido previo
    print("\n--- PASO 1: Crear Servicio y Pedido previo ---")
    srv_resp = client.post("/servicios/", json={
        "id_unidad_limpieza": 1,
        "id_modalidad": 1,
        "nombre": "Servicio de Planchado",
        "precio": 2500.0,
        "insumos_utilizados": []
    }, headers=admin_headers)
    srv_id = srv_resp.json()["id"]

    pedido_resp = client.post("/pedidos/", json={"id_usuario": 3, "id_servicios": [srv_id]}, headers=operador_headers)
    pedido_id = pedido_resp.json()["pedido"]["id"]

    pago_previo = db.query(models.FacturacionPagos).filter(models.FacturacionPagos.id_pedido == pedido_id).first()
    print(f"  * Entrada: Crear servicio ID = {srv_id} ($2500) | Pedido ID = {pedido_id}")
    print(f"  * Resultado obtenido: Facturación Estado Inicial en BD = '{pago_previo.estado}'")
    assert pago_previo.estado == "pending"

    # PASO 2: Recibir Webhook IPN
    print("\n--- PASO 2: Recibir Webhook IPN Simulado ---")
    webhook_payload = {
        "type": "payment",
        "data": {
            "id": "9876543210"
        }
    }
    print(f"  * Entrada: POST /pedidos/webhook/mercadopago?topic=payment con Payload = {webhook_payload}")
    print("  * Resultado esperado: Código HTTP 200 (OK) indicando procesamiento exitoso del webhook.")
    response_webhook = client.post(
        "/pedidos/webhook/mercadopago?topic=payment",
        json=webhook_payload
    )
    assert response_webhook.status_code == 200
    res_json = response_webhook.json()
    print(f"  * Resultado obtenido: Status Code = {response_webhook.status_code}")
    print(f"    - Webhook Response Status: '{res_json['status']}'")
    print(f"    - Nuevo estado de pago reportado: '{res_json['new_status']}'")

    # PASO 3: Validar actualización en la base de datos
    print("\n--- PASO 3: Validar Estado de Pago Actualizado en BD ---")
    print(f"  * Entrada: Consulta directa en base de datos para Pago del Pedido ID {pedido_id}")
    print("  * Resultado esperado: Estado del pago cambiado a 'approved' e ID de transacción externa registrado.")
    db.expire_all()
    pago_actualizado = db.query(models.FacturacionPagos).filter(models.FacturacionPagos.id_pedido == pedido_id).first()
    print(f"  * Resultado obtenido: Estado Final = '{pago_actualizado.estado}' | Transacción Ext ID = '{pago_actualizado.id_transaccion_externa}'")
    print(f"    - Fecha de Pago Registrada: {pago_actualizado.fecha_pago}")
    assert pago_actualizado.estado == "approved"
    assert pago_actualizado.id_transaccion_externa == "9876543210"
    print("  * Detalle de Validación: El webhook procesó la notificación de pago, consultó el mock del estado del pago y actualizó el estado en BD exitosamente.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
