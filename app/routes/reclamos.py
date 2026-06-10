from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models
from app.schemas import reclamos as schemas_reclamos
from app.services import reclamos as services_reclamos
from app.dependencies.auth import get_current_user, RoleChecker
from app.utils import security

router = APIRouter(
    prefix="/reclamos",
    tags=["Reclamos"]
)

@router.get("", response_model=List[schemas_reclamos.ReclamoResponse])
def obtener_reclamos(
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    role = current_user.rol.nombre.lower()
    client_name = current_user.nombre if role == "cliente" else None
    reclamos = services_reclamos.get_all(db, skip=skip, limit=limit, user_role=role, client_name=client_name)
    
    
    for r in reclamos:
        r.unread_count = sum(1 for m in r.mensajes if not m.leido and m.id_usuario != current_user.id)
        
    
    reclamos.sort(key=lambda x: (x.unread_count > 0, x.fecha_creacion), reverse=True)
        
    return reclamos


@router.get("/{reclamo_id}", response_model=schemas_reclamos.ReclamoResponse)
def obtener_reclamo_por_id(
    reclamo_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    reclamo = services_reclamos.get_by_id(db, reclamo_id=reclamo_id)
    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and reclamo.pedido.id_usuario != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para ver este reclamo."
        )
        
    
    services_reclamos.mark_messages_as_read(db, reclamo_id=reclamo_id, current_user_id=current_user.id)
    reclamo = services_reclamos.get_by_id(db, reclamo_id=reclamo_id)
    reclamo.unread_count = 0
    
    return reclamo


@router.post("", response_model=schemas_reclamos.ReclamoResponse, status_code=status.HTTP_201_CREATED)
def crear_reclamo(
    reclamo: schemas_reclamos.ReclamoCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    
    pedido = db.query(models.Pedido).filter(models.Pedido.id == reclamo.id_pedido, models.Pedido.baja == False).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and pedido.id_usuario != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede iniciar un reclamo sobre un pedido que no le pertenece."
        )
            
    return services_reclamos.create(db=db, reclamo=reclamo, creator_id=current_user.id)


@router.patch("/{reclamo_id}", response_model=schemas_reclamos.ReclamoResponse)
def actualizar_estado_reclamo(
    reclamo_id: int,
    reclamo_update: schemas_reclamos.ReclamoUpdate,
    current_user: models.Usuario = Depends(RoleChecker(["Administrador", "Operador"])),
    db: Session = Depends(get_db)
):
    
    return services_reclamos.update(db, reclamo_id=reclamo_id, reclamo_update=reclamo_update)


@router.get("/{reclamo_id}/mensajes", response_model=List[schemas_reclamos.MensajeReclamoResponse])
def obtener_mensajes_reclamo(
    reclamo_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    reclamo = services_reclamos.get_by_id(db, reclamo_id=reclamo_id)
    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and reclamo.pedido.id_usuario != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes para ver los mensajes de este reclamo."
        )
        
    
    services_reclamos.mark_messages_as_read(db, reclamo_id=reclamo_id, current_user_id=current_user.id)
    reclamo = services_reclamos.get_by_id(db, reclamo_id=reclamo_id)
    
    return reclamo.mensajes


@router.post("/{reclamo_id}/mensajes", response_model=schemas_reclamos.MensajeReclamoResponse, status_code=status.HTTP_201_CREATED)
def enviar_mensaje_reclamo(
    reclamo_id: int,
    mensaje: schemas_reclamos.MensajeReclamoCreate,
    background_tasks: BackgroundTasks,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    reclamo = services_reclamos.get_by_id(db, reclamo_id=reclamo_id)
    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and reclamo.pedido.id_usuario != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para enviar mensajes en este reclamo."
        )
                
    new_msg = services_reclamos.create_message(db=db, reclamo_id=reclamo_id, mensaje=mensaje, usuario_id=current_user.id)
    background_tasks.add_task(notifier.broadcast_notification, reclamo_id, current_user.id)
    return new_msg


class ConnectionManager:
    def __init__(self):
        
        self.active_connections: dict[int, list[tuple[WebSocket, int]]] = {}

    async def connect(self, reclamo_id: int, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if reclamo_id not in self.active_connections:
            self.active_connections[reclamo_id] = []
        self.active_connections[reclamo_id].append((websocket, user_id))

    def disconnect(self, reclamo_id: int, websocket: WebSocket):
        if reclamo_id in self.active_connections:
            self.active_connections[reclamo_id] = [
                conn for conn in self.active_connections[reclamo_id] if conn[0] != websocket
            ]
            if not self.active_connections[reclamo_id]:
                del self.active_connections[reclamo_id]

    async def broadcast_to_room(self, reclamo_id: int, message: dict, exclude: WebSocket = None):
        if reclamo_id in self.active_connections:
            for connection_tuple in self.active_connections[reclamo_id]:
                conn_ws = connection_tuple[0]
                if conn_ws != exclude:
                    try:
                        await conn_ws.send_json(message)
                    except Exception:
                        pass

manager = ConnectionManager()


class NotificationManager:
    def __init__(self):
        
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def notify_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def broadcast_notification(self, claim_id: int, sender_id: int):
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            reclamo = db.query(models.Reclamo).filter(models.Reclamo.id == claim_id).first()
            if not reclamo:
                return

            client_id = reclamo.pedido.id_usuario
            
            
            if sender_id == client_id:
                for user_id in list(self.active_connections.keys()):
                    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
                    if user and user.rol.nombre.lower() in ["administrador", "operador"]:
                        unread_count = db.query(models.MensajeReclamo).filter(
                            models.MensajeReclamo.id_reclamo == claim_id,
                            models.MensajeReclamo.id_usuario != user_id,
                            models.MensajeReclamo.leido == False
                        ).count()
                        await self.notify_user(user_id, {
                            "type": "unread_update",
                            "claim_id": str(claim_id),
                            "unread_count": unread_count
                        })
            else:
                
                unread_count = db.query(models.MensajeReclamo).filter(
                    models.MensajeReclamo.id_reclamo == claim_id,
                    models.MensajeReclamo.id_usuario != client_id,
                    models.MensajeReclamo.leido == False
                ).count()
                await self.notify_user(client_id, {
                    "type": "unread_update",
                    "claim_id": str(claim_id),
                    "unread_count": unread_count
                })
        finally:
            db.close()

notifier = NotificationManager()


@router.websocket("/notificaciones/ws")
async def notificaciones_websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    
    if not token:
        await websocket.close(code=4008)
        return
        
    payload = security.verify_token(token)
    if not payload:
        await websocket.close(code=4008)
        return
        
    usuario_id_str = payload.get("sub")
    if not usuario_id_str:
        await websocket.close(code=4008)
        return
        
    usuario_id = int(usuario_id_str)
    current_user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not current_user or not current_user.cuenta_activa:
        await websocket.close(code=4008)
        return

    
    await notifier.connect(usuario_id, websocket)
    
    try:
        while True:
            
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifier.disconnect(usuario_id, websocket)
    except Exception:
        notifier.disconnect(usuario_id, websocket)


@router.websocket("/{reclamo_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    reclamo_id: int,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    
    if not token:
        await websocket.close(code=4008)
        return
        
    payload = security.verify_token(token)
    if not payload:
        await websocket.close(code=4008)
        return
        
    usuario_id_str = payload.get("sub")
    if not usuario_id_str:
        await websocket.close(code=4008)
        return
        
    usuario_id = int(usuario_id_str)
    current_user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not current_user or not current_user.cuenta_activa:
        await websocket.close(code=4008)
        return

    
    try:
        reclamo = services_reclamos.get_by_id(db, reclamo_id=reclamo_id)
    except Exception:
        await websocket.close(code=4004)
        return
        
    is_client = current_user.rol.nombre.lower() == "cliente"
    if is_client and reclamo.pedido.id_usuario != current_user.id:
        await websocket.close(code=4003)
        return

    
    await manager.connect(reclamo_id, websocket, current_user.id)
    
    
    services_reclamos.mark_messages_as_read(db, reclamo_id=reclamo_id, current_user_id=current_user.id)
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "message":
                mensaje_texto = data.get("mensaje", "").strip()
                if mensaje_texto:
                    from app.schemas.reclamos import MensajeReclamoCreate
                    mensaje_create = MensajeReclamoCreate(mensaje=mensaje_texto)
                    new_msg = services_reclamos.create_message(
                        db=db,
                        reclamo_id=reclamo_id,
                        mensaje=mensaje_create,
                        usuario_id=current_user.id
                    )
                    
                    
                    is_read = False
                    if reclamo_id in manager.active_connections:
                        for conn_ws, conn_uid in manager.active_connections[reclamo_id]:
                            if conn_uid != current_user.id:
                                is_read = True
                                break
                    if is_read:
                        new_msg.leido = True
                        db.commit()
                    
                    from app.schemas.reclamos import MensajeReclamoResponse
                    from fastapi.encoders import jsonable_encoder
                    
                    formatted_time = new_msg.fecha_envio.strftime('%d/%m/%Y — %H:%M') if new_msg.fecha_envio else ""
                    serialized_msg = jsonable_encoder(MensajeReclamoResponse.model_validate(new_msg))
                    serialized_msg["time"] = formatted_time
                    
                    await manager.broadcast_to_room(
                        reclamo_id=reclamo_id,
                        message={
                            "type": "message",
                            "message": serialized_msg
                        }
                    )
                    
                    
                    import asyncio
                    asyncio.create_task(notifier.broadcast_notification(reclamo_id, current_user.id))
                    
            elif msg_type == "typing":
                is_typing = bool(data.get("is_typing", False))
                sender_name = f"{current_user.nombre} {current_user.apellido}"
                role_suffix = f" ({current_user.rol.nombre})" if current_user.rol and current_user.rol.nombre.lower() != "cliente" else ""
                full_sender_name = f"{sender_name}{role_suffix}"
                
                await manager.broadcast_to_room(
                    reclamo_id=reclamo_id,
                    message={
                        "type": "typing",
                        "usuario_id": current_user.id,
                        "senderName": full_sender_name,
                        "is_typing": is_typing
                    },
                    exclude=websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(reclamo_id, websocket)
        await manager.broadcast_to_room(
            reclamo_id=reclamo_id,
            message={
                "type": "typing",
                "usuario_id": current_user.id,
                "is_typing": False
            },
            exclude=websocket
        )
    except Exception:
        manager.disconnect(reclamo_id, websocket)
