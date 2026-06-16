import pytest
from app.utils import security
from unittest.mock import AsyncMock

# ----------------- PRUEBAS UNITARIAS -----------------

def test_password_hashing():
    """Prueba unitaria para verificar que el hashing de contraseñas sea seguro y verificable."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Hashing de Contraseñas (test_password_hashing)")
    print("="*80)
    
    password = "mi_clave_secreta"
    
    # PASO 1: Hashing de contraseña
    print("\n--- PASO 1: Hashing de contraseña ---")
    print(f"  * Entrada (Clave en texto plano): '{password}'")
    hash_password = security.get_password_hash(password)
    print(f"  * Resultado esperado: Retornar un hash cifrado seguro que no sea '{password}'")
    print(f"  * Resultado obtenido: '{hash_password}'")
    assert hash_password != password
    
    # PASO 2: Verificación de Contraseña Correcta
    print("\n--- PASO 2: Verificación de Contraseña Correcta ---")
    print(f"  * Entrada: Verificar contraseña correcta '{password}' contra el hash")
    print(f"  * Resultado esperado: True (Acceso autorizado)")
    is_correct = security.verify_password(password, hash_password)
    print(f"  * Resultado obtenido: {is_correct}")
    assert is_correct is True
    
    # PASO 3: Verificación de Contraseña Incorrecta
    wrong_password = "clave_incorrecta"
    print("\n--- PASO 3: Verificación de Contraseña Incorrecta ---")
    print(f"  * Entrada: Verificar contraseña incorrecta '{wrong_password}' contra el hash")
    print(f"  * Resultado esperado: False (Acceso denegado)")
    is_wrong = security.verify_password(wrong_password, hash_password)
    print(f"  * Resultado obtenido: {is_wrong} (Acceso denegado correctamente)")
    assert is_wrong is False
    
    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_token_generation_and_verification():
    """Prueba unitaria para la creación y verificación de tokens JWT."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Generación y Validación de JWT (test_token_generation_and_verification)")
    print("="*80)
    
    payload = {"sub": "123", "rol": "Cliente", "action": "test"}
    
    # PASO 1: Generación del token
    print("\n--- PASO 1: Generación de Access Token JWT ---")
    print(f"  * Entrada (Payload a firmar): {payload}")
    token = security.create_access_token(data=payload)
    print(f"  * Resultado esperado: Retornar un string JWT codificado y firmado")
    print(f"  * Resultado obtenido: '{token}'")
    assert token is not None
    
    # PASO 2: Decodificación y validación del token
    print("\n--- PASO 2: Decodificación y Validación del Token ---")
    print(f"  * Entrada: Validar el token anterior")
    decoded = security.verify_token(token)
    print(f"  * Resultado esperado: Retornar el payload original con 'sub'='123', 'rol'='Cliente' y 'action'='test'")
    print(f"  * Resultado obtenido: {decoded}")
    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["rol"] == "Cliente"
    assert decoded["action"] == "test"
    
    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_jwt_validation_error_handling():
    """Prueba unitaria para verificar el manejo de errores al validar tokens JWT inválidos o alterados."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Manejo de Errores en Validación JWT (test_jwt_validation_error_handling)")
    print("="*80)

    # PASO 1: Validar token mal formado
    token_invalido = "cabecera.payload.firma_incorrecta"
    print("\n--- PASO 1: Validar Token Mal Formado ---")
    print(f"  * Entrada: Intentar verificar token mal formado '{token_invalido}'")
    print("  * Resultado esperado: Retornar None (Token inválido)")
    resultado = security.verify_token(token_invalido)
    print(f"  * Resultado obtenido: {resultado}")
    assert resultado is None
    print("  * Detalle de Validación: El decodificador JWT manejó correctamente el formato inválido retornando None.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

@pytest.mark.asyncio
async def test_registro_y_activacion_flujo_completo(client, admin_headers, mocker):
    """Prueba de integración del flujo de registro y activación de cuenta."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: Registro y Activación de Cuenta (test_registro_y_activacion_flujo_completo)")
    print("="*80)
    
    mock_send_email = mocker.patch("app.utils.email.send_activation_email", new_callable=AsyncMock)

    # PASO 1: Registro por Administrador
    nuevo_usuario_data = {
        "id_rol": 3,
        "nombre": "Juan",
        "apellido": "Perez",
        "dni": "44444444",
        "email": "juan.perez@example.com",
        "telefono": "123456789"
    }
    print("\n--- PASO 1: Registro de Cuenta (Inactiva) ---")
    print(f"  * Entrada: Crear usuario con datos = {nuevo_usuario_data}")
    response = client.post("/usuarios/", json=nuevo_usuario_data, headers=admin_headers)
    assert response.status_code == 201
    res_data = response.json()
    print(f"  * Resultado esperado: Código 201. Cuenta creada en estado inactivo")
    print(f"  * Resultado obtenido: Status Code = {response.status_code} | cuenta_activa = {res_data['cuenta_activa']}")
    assert res_data["cuenta_activa"] is False
    
    # PASO 2: Envío de Email de Invitación
    print("\n--- PASO 2: Envío Automático de Correo con Token ---")
    mock_send_email.assert_called_once()
    llamar_args = mock_send_email.call_args[1]
    token_activacion = llamar_args["token"]
    print(f"  * Resultado esperado: Función 'send_activation_email' invocada y token generado")
    print(f"  * Resultado obtenido: Envío invocado hacia '{llamar_args['to_email']}' | Token = '{token_activacion[:30]}...'")
    assert token_activacion is not None

    # PASO 3: Intento de Login sin Activación
    login_fail_data = {
        "email": "juan.perez@example.com",
        "password": "password_temporal"
    }
    print("\n--- PASO 3: Intento de Acceso sin Activar Cuenta ---")
    print(f"  * Entrada: Login con {login_fail_data}")
    response_login_fail = client.post("/auth/login", json=login_fail_data)
    print(f"  * Resultado esperado: Acceso rechazado (código 401 o 403)")
    print(f"  * Resultado obtenido: Status Code = {response_login_fail.status_code} | Detalle = '{response_login_fail.json().get('detail')}'")
    assert response_login_fail.status_code in [401, 403]

    # PASO 4: Activación de Cuenta y Cambio de Contraseña
    datos_activacion = {
        "token": token_activacion,
        "password": "contrasenaSegura123"
    }
    print("\n--- PASO 4: Activación de Cuenta mediante Token ---")
    print(f"  * Entrada: Enviar token y nueva clave = '{datos_activacion['password']}'")
    response_activar = client.post("/auth/activar-cuenta", json=datos_activacion)
    assert response_activar.status_code == 200
    res_act = response_activar.json()
    print(f"  * Resultado esperado: Código 200. Cuenta activada (`cuenta_activa=True`)")
    print(f"  * Resultado obtenido: Status Code = {response_activar.status_code} | cuenta_activa = {res_act['cuenta_activa']}")
    assert res_act["cuenta_activa"] is True

    # PASO 5: Inicio de Sesión
    login_success_data = {
        "email": "juan.perez@example.com",
        "password": "contrasenaSegura123"
    }
    print("\n--- PASO 5: Inicio de Sesión con Nueva Contraseña ---")
    print(f"  * Entrada: Login con email = '{login_success_data['email']}' y clave")
    response_login = client.post("/auth/login", json=login_success_data)
    assert response_login.status_code == 200
    token_data = response_login.json()
    print(f"  * Resultado esperado: Login exitoso, retornar JWT access_token y perfil del usuario")
    print(f"  * Resultado obtenido: Status Code = {response_login.status_code}")
    print(f"    - Access Token: '{token_data['access_token'][:30]}...'")
    print(f"    - Perfil: Nombre = '{token_data['usuario']['nombre']}' | Rol = '{token_data['usuario']['rol']}'")
    assert "access_token" in token_data
    assert token_data["usuario"]["email"] == "juan.perez@example.com"
    
    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
