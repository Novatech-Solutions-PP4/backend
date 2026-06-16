import pytest
from unittest.mock import AsyncMock
from app.schemas.usuarios import UsuarioActivar
from pydantic import ValidationError

# ----------------- PRUEBAS UNITARIAS -----------------

def test_usuario_activar_password_validation():
    """Prueba unitaria para verificar la validación de longitud de contraseña en el esquema UsuarioActivar."""
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA UNITARIA: Validación de Contraseña en Schema UsuarioActivar (test_usuario_activar_password_validation)")
    print("="*80)

    # PASO 1: Contraseña válida (8 caracteres o más)
    payload_valido = {
        "token": "token_prueba_123",
        "password": "miClaveSegura123"
    }
    print("\n--- PASO 1: Validar Contraseña Correcta (Longitud >= 8) ---")
    print(f"  * Entrada: Datos del Schema = {payload_valido}")
    print("  * Resultado esperado: Instanciación correcta del Schema sin errores.")
    schema_inst = UsuarioActivar(**payload_valido)
    print(f"  * Resultado obtenido: Schema instanciado correctamente con password = '{schema_inst.password}'")
    assert schema_inst.password == "miClaveSegura123"

    # PASO 2: Contraseña corta (menos de 8 caracteres)
    payload_invalido = {
        "token": "token_prueba_123",
        "password": "12345"
    }
    print("\n--- PASO 2: Validar Contraseña Corta (Longitud < 8) ---")
    print(f"  * Entrada: Datos del Schema = {payload_invalido}")
    print("  * Resultado esperado: Pydantic ValidationError levantado por la regla de validación.")
    
    with pytest.raises(ValidationError) as exc_info:
        UsuarioActivar(**payload_invalido)
    
    print(f"  * Resultado obtenido: ValidationError capturado exitosamente.")
    print(f"    - Detalle del error: '{exc_info.value.errors()[0]['msg']}'")
    assert "La contraseña debe tener un mínimo de 8 caracteres" in exc_info.value.errors()[0]['msg']
    print("  * Detalle de Validación: La validación de longitud del password se ejecutó correctamente y rechazó la contraseña corta.")

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE INTEGRACIÓN -----------------

def test_crud_usuarios_por_administrador(client, admin_headers, mocker):
    """
    CRUD completo realizado por el Administrador:
    - Crear un usuario Cliente.
    - Obtener el listado completo de usuarios.
    - Modificar campos del perfil.
    - Dar de baja lógica.
    """
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE INTEGRACIÓN: CRUD de Usuarios por Administrador (test_crud_usuarios_por_administrador)")
    print("="*80)

    mocker.patch("app.utils.email.send_activation_email", new_callable=AsyncMock)

    # PASO 1: Crear
    usr_data = {
        "id_rol": 3,
        "nombre": "Carlos",
        "apellido": "Gomez",
        "dni": "55555555",
        "email": "carlos.gomez@example.com",
        "telefono": "112233"
    }
    print("\n--- PASO 1: Registro de un nuevo Usuario Cliente ---")
    print(f"  * Entrada: POST /usuarios/ con Datos = {usr_data} y headers = Administrador")
    print("  * Resultado esperado: Código HTTP 201 (Creado) y retornar el objeto del usuario creado con ID único.")
    response = client.post("/usuarios/", json=usr_data, headers=admin_headers)
    assert response.status_code == 201
    res_json = response.json()
    user_id = res_json["id"]
    print(f"  * Resultado obtenido: Status Code = {response.status_code}")
    print(f"    - ID Generado: {user_id}")
    print(f"    - Nombre Registrado: '{res_json['nombre']} {res_json['apellido']}'")
    print(f"    - Email: '{res_json['email']}'")
    print(f"  * Detalle de Validación: Se creó el usuario con éxito en la base de datos.")

    # PASO 2: Leer
    print("\n--- PASO 2: Consulta del Usuario Creado por ID ---")
    print(f"  * Entrada: GET /usuarios/{user_id} con headers = Administrador")
    print(f"  * Resultado esperado: Código HTTP 200 (OK) y el nombre del usuario debe ser exactamente 'Carlos'.")
    response_get = client.get(f"/usuarios/{user_id}", headers=admin_headers)
    assert response_get.status_code == 200
    get_json = response_get.json()
    print(f"  * Resultado obtenido: Status Code = {response_get.status_code}")
    print(f"    - Nombre obtenido: '{get_json['nombre']}'")
    print(f"    - Apellido obtenido: '{get_json['apellido']}'")
    print(f"  * Detalle de Validación: Los datos del usuario retornado coinciden con el registro creado.")
    assert get_json["nombre"] == "Carlos"

    # PASO 3: Listar
    print("\n--- PASO 3: Listado General de Usuarios del Sistema ---")
    print("  * Entrada: GET /usuarios/ con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y que la lista contenga al menos 4 usuarios (incluyendo el recién creado y los pre-sembrados).")
    response_list = client.get("/usuarios/", headers=admin_headers)
    assert response_list.status_code == 200
    list_data = response_list.json()
    print(f"  * Resultado obtenido: Status Code = {response_list.status_code}")
    print(f"    - Cantidad total de usuarios listados: {len(list_data)}")
    print(f"  * Detalle de Validación: La lista de usuarios fue obtenida y el tamaño es el esperado.")
    assert len(list_data) >= 4

    # PASO 4: Actualizar
    update_data = {
        "nombre": "Carlos Alberto",
        "telefono": "999999"
    }
    print("\n--- PASO 4: Modificación del Perfil del Usuario ---")
    print(f"  * Entrada: PATCH /usuarios/{user_id} con Datos a actualizar = {update_data}")
    print("  * Resultado esperado: Código HTTP 200 (OK) y los datos de 'nombre' y 'telefono' deben reflejar el cambio.")
    response_update = client.patch(f"/usuarios/{user_id}", json=update_data, headers=admin_headers)
    assert response_update.status_code == 200
    update_json = response_update.json()
    print(f"  * Resultado obtenido: Status Code = {response_update.status_code}")
    print(f"    - Nuevo Nombre: '{update_json['nombre']}' (Esperado: 'Carlos Alberto')")
    print(f"    - Nuevo Teléfono: '{update_json['telefono']}' (Esperado: '999999')")
    print(f"  * Detalle de Validación: El perfil del usuario se actualizó exitosamente.")
    assert update_json["nombre"] == "Carlos Alberto"
    assert update_json["telefono"] == "999999"

    # PASO 5: Eliminar (baja lógica)
    print("\n--- PASO 5: Baja Lógica del Usuario del Sistema ---")
    print(f"  * Entrada: DELETE /usuarios/{user_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 200 (OK) y el campo 'baja' debe ser True.")
    response_delete = client.delete(f"/usuarios/{user_id}", headers=admin_headers)
    assert response_delete.status_code == 200
    delete_json = response_delete.json()
    print(f"  * Resultado obtenido: Status Code = {response_delete.status_code}")
    print(f"    - Estado de baja: {delete_json['baja']} (Esperado: True)")
    print(f"  * Detalle de Validación: El usuario fue marcado como inactivo (baja lógica) sin borrar físicamente el registro.")
    assert delete_json["baja"] is True

    # PASO 6: Intentar obtener el usuario eliminado
    print("\n--- PASO 6: Intentar Consultar el Usuario de Baja ---")
    print(f"  * Entrada: GET /usuarios/{user_id} con headers = Administrador")
    print("  * Resultado esperado: Código HTTP 404 (Not Found) ya que el usuario tiene la baja lógica activa.")
    response_get_deleted = client.get(f"/usuarios/{user_id}", headers=admin_headers)
    print(f"  * Resultado obtenido: Status Code = {response_get_deleted.status_code}")
    print(f"    - Mensaje de Detalle: '{response_get_deleted.json().get('detail')}'")
    print(f"  * Detalle de Validación: Correctamente no se permite el acceso al perfil por haber sido dado de baja.")
    assert response_get_deleted.status_code == 404

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

# ----------------- PRUEBAS DE ROLES Y PERMISOS (RBAC) -----------------

def test_rbac_restricciones_cliente(client, cliente_headers, mocker):
    """
    Validar restricciones de rol Cliente:
    - No puede ver el listado de usuarios (403).
    - No puede registrar nuevos usuarios (403).
    - No puede dar de baja usuarios (403).
    - No puede modificar perfiles ajenos (403).
    """
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE CONTROL DE ACCESOS (RBAC): Restricciones del Rol Cliente (test_rbac_restricciones_cliente)")
    print("="*80)
    
    mocker.patch("app.utils.email.send_activation_email", new_callable=AsyncMock)

    # PASO 1: Listar
    print("\n--- PASO 1: Intento de Listar Usuarios por un Cliente ---")
    print("  * Entrada: GET /usuarios/ con headers = Cliente")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden / Permisos insuficientes)")
    resp_list = client.get("/usuarios/", headers=cliente_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_list.status_code} | Detalle = '{resp_list.json().get('detail')}'")
    print("  * Detalle de Validación: Acceso denegado correctamente por no poseer rol Administrativo o de Operador.")
    assert resp_list.status_code == 403

    # PASO 2: Crear
    print("\n--- PASO 2: Intento de Registrar Usuario por un Cliente ---")
    print("  * Entrada: POST /usuarios/ con headers = Cliente y datos básicos de usuario")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden / Permisos insuficientes)")
    resp_create = client.post("/usuarios/", json={"id_rol": 3, "nombre": "Fail", "apellido": "Fail", "dni": "99", "email": "fail@fail.com"}, headers=cliente_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_create.status_code} | Detalle = '{resp_create.json().get('detail')}'")
    print("  * Detalle de Validación: Operación rechazada. Los clientes no pueden dar de alta a otros usuarios.")
    assert resp_create.status_code == 403

    # PASO 3: Eliminar
    print("\n--- PASO 3: Intento de Eliminar un Usuario por un Cliente ---")
    print("  * Entrada: DELETE /usuarios/1 (Usuario Administrador) con headers = Cliente")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden / Permisos insuficientes)")
    resp_delete = client.delete("/usuarios/1", headers=cliente_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_delete.status_code} | Detalle = '{resp_delete.json().get('detail')}'")
    print("  * Detalle de Validación: Operación denegada. Los clientes no tienen permiso para borrar usuarios.")
    assert resp_delete.status_code == 403

    # PASO 4: Ver perfil ajeno
    print("\n--- PASO 4: Intento de Consultar Perfil Ajeno por un Cliente ---")
    print("  * Entrada: GET /usuarios/1 (Perfil del Administrador) con headers = Cliente")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden / Permisos insuficientes)")
    resp_profile = client.get("/usuarios/1", headers=cliente_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_profile.status_code} | Detalle = '{resp_profile.json().get('detail')}'")
    print("  * Detalle de Validación: Operación rechazada. Un cliente solo puede ver su propio perfil, no el de terceros.")
    assert resp_profile.status_code == 403

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)

def test_rbac_restricciones_operador(client, operador_headers, mocker):
    """
    Validar restricciones del rol Operador:
    - Puede registrar a un Cliente.
    - NO puede registrar a un Administrador u otro Operador (403).
    - NO puede eliminar usuarios (403).
    """
    print("\n" + "="*80)
    print("EJECUTANDO PRUEBA DE CONTROL DE ACCESOS (RBAC): Restricciones del Rol Operador (test_rbac_restricciones_operador)")
    print("="*80)

    mocker.patch("app.utils.email.send_activation_email", new_callable=AsyncMock)

    # PASO 1: Operador registra Cliente
    usr_cliente_data = {
        "id_rol": 3,
        "nombre": "Ana",
        "apellido": "Lopez",
        "dni": "66666666",
        "email": "ana.lopez@example.com"
    }
    print("\n--- PASO 1: Registro de un Cliente por un Operador ---")
    print(f"  * Entrada: POST /usuarios/ con Rol = Cliente (3) y headers = Operador")
    print("  * Resultado esperado: Código HTTP 201 (Creado) ya que los operadores están autorizados a dar de alta clientes.")
    resp_ok = client.post("/usuarios/", json=usr_cliente_data, headers=operador_headers)
    assert resp_ok.status_code == 201
    print(f"  * Resultado obtenido: Status Code = {resp_ok.status_code} | ID Registrado = {resp_ok.json().get('id')}")
    print("  * Detalle de Validación: Operación permitida y registrada con éxito.")

    # PASO 2: Operador intenta registrar Administrador
    usr_admin_data = {
        "id_rol": 1,
        "nombre": "Malo",
        "apellido": "Malo",
        "dni": "77777777",
        "email": "malo@example.com"
    }
    print("\n--- PASO 2: Intento de Registro de Administrador por un Operador ---")
    print(f"  * Entrada: POST /usuarios/ con Rol = Administrador (1) y headers = Operador")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) ya que los operadores no pueden crear roles con jerarquía superior.")
    resp_fail = client.post("/usuarios/", json=usr_admin_data, headers=operador_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_fail.status_code} | Detalle = '{resp_fail.json().get('detail')}'")
    print("  * Detalle de Validación: Bloqueo exitoso. Un operador no puede escalar privilegios creando administradores.")
    assert resp_fail.status_code == 403

    # PASO 3: Operador intenta eliminar a un usuario
    print("\n--- PASO 3: Intento de Eliminación de Usuario por un Operador ---")
    print("  * Entrada: DELETE /usuarios/3 con headers = Operador")
    print("  * Resultado esperado: Código HTTP 403 (Forbidden) ya que la baja de usuarios es una facultad exclusiva de Administradores.")
    resp_delete = client.delete("/usuarios/3", headers=operador_headers)
    print(f"  * Resultado obtenido: Status Code = {resp_delete.status_code} | Detalle = '{resp_delete.json().get('detail')}'")
    print("  * Detalle de Validación: Bloqueo exitoso. Los operadores tienen prohibido dar de baja cuentas de usuario.")
    assert resp_delete.status_code == 403

    print("\nESTADO DE LA PRUEBA: PASSED (Éxito)")
    print("="*80)
