import os
import requests
from fastapi import HTTPException, status

MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
MERCADOPAGO_WEBHOOK_URL = os.getenv("MERCADOPAGO_WEBHOOK_URL", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def crear_preferencia_pago(pedido_id: int, monto: float, email_cliente: str) -> dict:
    
    if not MERCADOPAGO_ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración: MERCADOPAGO_ACCESS_TOKEN no está configurado."
        )
        
    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {
        "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    
    success_url = f"{FRONTEND_URL}/pedidos" if not FRONTEND_URL.endswith("/") else f"{FRONTEND_URL}pedidos"
    failure_url = f"{FRONTEND_URL}/pedidos" if not FRONTEND_URL.endswith("/") else f"{FRONTEND_URL}pedidos"
    pending_url = f"{FRONTEND_URL}/pedidos" if not FRONTEND_URL.endswith("/") else f"{FRONTEND_URL}pedidos"
    
    
    
    email_limpio = email_cliente
    if not email_cliente.endswith("@testuser.com"):
        email_limpio = f"{email_cliente.replace('@', '_at_')}@testuser.com"
        
    body = {
        "items": [
            {
                "id": f"pedido_{pedido_id}",
                "title": f"LavaPro - Pedido #{pedido_id}",
                "quantity": 1,
                "unit_price": float(monto),
                "currency_id": "ARS"
            }
        ],
        "payer": {
            "email": email_limpio
        },
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url
        },
        "auto_return": "approved",
        "notification_url": f"{MERCADOPAGO_WEBHOOK_URL}/pedidos/webhook/mercadopago",
        "external_reference": str(pedido_id)
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        if response.status_code != 201:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al conectar con Mercado Pago: {response.text}"
            )
        data = response.json()
        return {
            "preference_id": data.get("id"),
            "init_point": data.get("init_point")
        }
    except Exception as err:
        if isinstance(err, HTTPException):
            raise err
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo de conexión con Mercado Pago: {err}"
        )

def obtener_estado_pago(pago_id: str) -> dict:
    
    if not MERCADOPAGO_ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración: MERCADOPAGO_ACCESS_TOKEN no está configurado."
        )
        
    url = f"https://api.mercadopago.com/v1/payments/{pago_id}"
    headers = {
        "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo consultar el pago en Mercado Pago: {response.text}"
            )
        data = response.json()
        return {
            "id_pago": str(data.get("id")),
            "estado": data.get("status"), 
            "monto": float(data.get("transaction_amount", 0.0)),
            "external_reference": data.get("external_reference") 
        }
    except Exception as err:
        if isinstance(err, HTTPException):
            raise err
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar estado de pago en Mercado Pago: {err}"
        )
