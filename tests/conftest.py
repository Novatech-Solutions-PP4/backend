import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurar la variable de entorno para usar SQLite temporal en los tests
os.environ["DATABASE_URL"] = "sqlite:///./test_lavapro.db"
os.environ["APP_ENV"] = "testing"

# Asegurar que el path del backend esté en sys.path para importaciones correctas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, get_db
from app.main import app
import app.models as models
from app.utils.security import get_password_hash, create_access_token
from fastapi.testclient import TestClient

# Crear motor SQLite y SessionLocal de pruebas
engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override para FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Eliminar base de datos vieja si existe
    if os.path.exists("./test_lavapro.db"):
        try:
            os.remove("./test_lavapro.db")
        except Exception:
            pass
            
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Sembrar datos estáticos requeridos por el sistema
    db = TestingSessionLocal()
    try:
        # 1. Roles
        roles = [
            models.Rol(id=1, nombre="Administrador"),
            models.Rol(id=2, nombre="Operador"),
            models.Rol(id=3, nombre="Cliente")
        ]
        db.add_all(roles)
        
        # 2. Estados de Pedidos
        estados = [
            models.Estado(id=1, nombre="Pendiente"),
            models.Estado(id=2, nombre="En Proceso"),
            models.Estado(id=3, nombre="Listo"),
            models.Estado(id=4, nombre="Entregado"),
            models.Estado(id=5, nombre="Cancelado")
        ]
        db.add_all(estados)
        
        # 3. Metodos de Pago
        metodos = [
            models.MetodoPago(id=1, nombre="Mercado Pago")
        ]
        db.add_all(metodos)
        
        # 4. Estados de Reclamos
        est_reclamos = [
            models.EstadoReclamo(id=1, nombre="Abierto"),
            models.EstadoReclamo(id=2, nombre="En Revisión"),
            models.EstadoReclamo(id=3, nombre="Resuelto")
        ]
        db.add_all(est_reclamos)
        
        # 5. Categorias de Reclamos
        cat_reclamos = [
            models.CategoriaReclamo(id=1, nombre="Prenda Dañada o Manchada"),
            models.CategoriaReclamo(id=2, nombre="Falta una Prenda en la Entrega"),
            models.CategoriaReclamo(id=3, nombre="Demora excesiva en los plazos"),
            models.CategoriaReclamo(id=4, nombre="Error en el Cobro / Precio de Lista"),
            models.CategoriaReclamo(id=5, nombre="Otro motivo específico")
        ]
        db.add_all(cat_reclamos)
        
        # 6. Unidades de Limpieza
        unidades = [
            models.UnidadLimpieza(id=1, nombre="Canasto"),
            models.UnidadLimpieza(id=2, nombre="Acolchado"),
            models.UnidadLimpieza(id=3, nombre="Calzado")
        ]
        db.add_all(unidades)
        
        # 7. Modalidades de Servicio
        modalidades = [
            models.ModalidadServicio(id=1, nombre="Económico"),
            models.ModalidadServicio(id=2, nombre="Standar"),
            models.ModalidadServicio(id=3, nombre="Delicado")
        ]
        db.add_all(modalidades)
        
        # 8. Usuarios por Defecto (Admin, Operador, Cliente) para pruebas de autorización
        pass_hash = get_password_hash("password123")
        
        admin_user = models.Usuario(
            id=1,
            id_rol=1, # Administrador
            nombre="Admin",
            apellido="LavaPro",
            dni="11111111",
            email="admin@lavapro.online",
            telefono="11223344",
            password=pass_hash,
            cuenta_activa=True,
            password_cambiada=True,
            codigo_qr="LAVAPRO-USR-1-11111111"
        )
        
        operador_user = models.Usuario(
            id=2,
            id_rol=2, # Operador
            nombre="Operador",
            apellido="LavaPro",
            dni="22222222",
            email="operador@lavapro.online",
            telefono="55667788",
            password=pass_hash,
            cuenta_activa=True,
            password_cambiada=True,
            codigo_qr="LAVAPRO-USR-2-22222222"
        )
        
        cliente_user = models.Usuario(
            id=3,
            id_rol=3, # Cliente
            nombre="Cliente",
            apellido="LavaPro",
            dni="33333333",
            email="cliente@lavapro.online",
            telefono="99001122",
            password=pass_hash,
            cuenta_activa=True,
            password_cambiada=True,
            codigo_qr="LAVAPRO-USR-3-33333333"
        )
        
        db.add_all([admin_user, operador_user, cliente_user])
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
    yield
    
    # Limpieza
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_lavapro.db"):
        try:
            os.remove("./test_lavapro.db")
        except Exception:
            pass

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    # Desactivar lifespan durante los tests si es necesario, o dejar que se ejecute (los errores de seed son controlados)
    with TestClient(app) as c:
        yield c

# Fixtures de tokens y cabeceras para roles
@pytest.fixture
def admin_headers():
    token = create_access_token(data={"sub": "1", "rol": "Administrador"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def operador_headers():
    token = create_access_token(data={"sub": "2", "rol": "Operador"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def cliente_headers():
    token = create_access_token(data={"sub": "3", "rol": "Cliente"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def mock_mercadopago(mocker):
    """Fixture autouse para mockear de forma global las llamadas de Mercado Pago."""
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
