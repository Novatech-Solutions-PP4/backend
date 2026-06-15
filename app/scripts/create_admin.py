import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Usuario, Rol
from app.utils.security import get_password_hash

def create_admin_user(email: str, password: str, nombre: str, apellido: str, dni: str, telefono: str):
    db: Session = SessionLocal()
    try:
        admin_role = db.query(Rol).filter(Rol.nombre == "Administrador").first()
        if not admin_role:
            admin_role = Rol(nombre="Administrador")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Role 'Administrador' created.")
        
        existing_user = db.query(Usuario).filter(Usuario.email == email).first()
        if existing_user:
            print(f"Usuario con email {email} ya existe.")
            return

        existing_dni = db.query(Usuario).filter(Usuario.dni == dni).first()
        if existing_dni:
            print(f"Usuario con DNI {dni} ya existe.")
            return
        
        hashed_password = get_password_hash(password)
        
        new_admin = Usuario(
            id_rol=admin_role.id,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            email=email,
            telefono=telefono,
            password=hashed_password,
            cuenta_activa=True
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print(f"El usuario admin '{email}' fue creado exitosamente!")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear un usuario admin en la base de datos.")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin contraseña")
    parser.add_argument("--nombre", default="Admin", help="Admin nombre")
    parser.add_argument("--apellido", default="Principal", help="Admin apellido")
    parser.add_argument("--dni", required=True, help="Admin DNI")
    parser.add_argument("--telefono", default="", help="Admin numero de telefono")
    
    args = parser.parse_args()
    
    create_admin_user(
        email=args.email,
        password=args.password,
        nombre=args.nombre,
        apellido=args.apellido,
        dni=args.dni,
        telefono=args.telefono
    )
