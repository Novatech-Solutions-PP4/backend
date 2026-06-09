from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Rol(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")

class Estado(Base):
    __tablename__ = "estados"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

    historiales = relationship("HistorialEstados", back_populates="estado")

class EstadoReclamo(Base):
    __tablename__ = "estados_reclamos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

    reclamos = relationship("Reclamo", back_populates="estado_rel")

class CategoriaReclamo(Base):
    __tablename__ = "categorias_reclamos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

    reclamos = relationship("Reclamo", back_populates="categoria_rel")

class MetodoPago(Base):
    __tablename__ = "metodos_pago"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

    pagos = relationship("FacturacionPagos", back_populates="metodo_pago")

class UnidadLimpieza(Base):
    __tablename__ = "unidades_limpieza"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    servicios = relationship("Servicio", back_populates="unidad_limpieza")

class ModalidadServicio(Base):
    __tablename__ = "modalidades_servicio"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    servicios = relationship("Servicio", back_populates="modalidad")

class Insumo(Base):
    __tablename__ = "insumos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cantidad = Column(Float, default=0.0)
    cantidad_alerta = Column(Float, default=0.0)
    costo_actual = Column(Float, default=0.0)
    baja = Column(Boolean, default=False)

    insumos_servicios = relationship("InsumosServicios", back_populates="insumo")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("roles.id"), nullable=False)
    password_cambiada = Column(Boolean, default=False)
    cuenta_activa = Column(Boolean, default=False)
    codigo_qr = Column(String, nullable=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    dni = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String, nullable=True)
    password = Column(String, nullable=False)
    baja = Column(Boolean, default=False)

    rol = relationship("Rol", back_populates="usuarios")
    pedidos = relationship("Pedido", back_populates="usuario")
    historiales = relationship("HistorialEstados", back_populates="usuario")
    mensajes_reclamo = relationship("MensajeReclamo", back_populates="usuario")

class Servicio(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    id_unidad_limpieza = Column(Integer, ForeignKey("unidades_limpieza.id"), nullable=False)
    id_modalidad = Column(Integer, ForeignKey("modalidades_servicio.id"), nullable=False)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    baja = Column(Boolean, default=False)

    unidad_limpieza = relationship("UnidadLimpieza", back_populates="servicios")
    modalidad = relationship("ModalidadServicio", back_populates="servicios")
    detalles_pedido = relationship("DetalleServicio", back_populates="servicio")
    insumos_utilizados = relationship("InsumosServicios", back_populates="servicio")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    codigo_qr = Column(String, nullable=True)
    estado_actual = Column(String, nullable=False)
    fecha_recepcion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_entrega_estimada = Column(DateTime, nullable=True)
    monto_actual = Column(Float, default=0.0)
    baja = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="pedidos")
    historial_estados = relationship("HistorialEstados", back_populates="pedido")
    reclamos = relationship("Reclamo", back_populates="pedido")
    detalles = relationship("DetalleServicio", back_populates="pedido")
    pagos = relationship("FacturacionPagos", back_populates="pedido")

class InsumosServicios(Base):
    __tablename__ = "insumos_servicios"
    id = Column(Integer, primary_key=True, index=True)
    id_servicio = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    id_insumo = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    cantidad_utilizada = Column(Float, nullable=False)

    servicio = relationship("Servicio", back_populates="insumos_utilizados")
    insumo = relationship("Insumo", back_populates="insumos_servicios")

class HistorialEstados(Base):
    __tablename__ = "historial_estados"
    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    id_estado = Column(Integer, ForeignKey("estados.id"), nullable=False)
    fecha_hora = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("Usuario", back_populates="historiales")
    pedido = relationship("Pedido", back_populates="historial_estados")
    estado = relationship("Estado", back_populates="historiales")

class Reclamo(Base):
    __tablename__ = "reclamos"
    id = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias_reclamos.id"), nullable=False)
    id_estado = Column(Integer, ForeignKey("estados_reclamos.id"), nullable=False)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pedido = relationship("Pedido", back_populates="reclamos")
    mensajes = relationship("MensajeReclamo", back_populates="reclamo", cascade="all, delete-orphan")
    categoria_rel = relationship("CategoriaReclamo", back_populates="reclamos")
    estado_rel = relationship("EstadoReclamo", back_populates="reclamos")

class FacturacionPagos(Base):
    __tablename__ = "facturacion_pagos"
    id = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey("metodos_pago.id"), nullable=False)
    id_transaccion_externa = Column(String, unique=True, index=True, nullable=True)
    estado = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime, nullable=True)

    pedido = relationship("Pedido", back_populates="pagos")
    metodo_pago = relationship("MetodoPago", back_populates="pagos")

class DetalleServicio(Base):
    __tablename__ = "detalles_servicio"
    id = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    precio_unitario_momento = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")
    servicio = relationship("Servicio", back_populates="detalles_pedido")

class MensajeReclamo(Base):
    __tablename__ = "mensajes_reclamos"
    id = Column(Integer, primary_key=True, index=True)
    id_reclamo = Column(Integer, ForeignKey("reclamos.id", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    mensaje = Column(String, nullable=False)
    fecha_envio = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reclamo = relationship("Reclamo", back_populates="mensajes")
    usuario = relationship("Usuario", back_populates="mensajes_reclamo")

    @property
    def text(self):
        return self.mensaje

    @property
    def sender(self):
        if self.usuario and self.usuario.rol:
            return "cliente" if self.usuario.rol.nombre.lower() == "cliente" else "soporte"

        if self.reclamo and self.reclamo.pedido and self.id_usuario == self.reclamo.pedido.id_usuario:
            return "cliente"
        return "soporte"

    @property
    def senderName(self):
        if self.usuario:
            role_suffix = f" ({self.usuario.rol.nombre})" if self.usuario.rol and self.usuario.rol.nombre.lower() != "cliente" else ""
            return f"{self.usuario.nombre} {self.usuario.apellido}{role_suffix}"
        return "Soporte"

    @property
    def time(self):
        return self.fecha_envio.strftime('%d/%m/%Y — %H:%M') if self.fecha_envio else ""