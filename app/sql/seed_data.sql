CREATE OR REPLACE PROCEDURE seed_initial_laundry_data()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Regular inserts without the conflict check
    INSERT INTO unidades_limpieza (nombre) VALUES ('canasto'), ('acolchado'), ('calzado');
    INSERT INTO modalidades_servicio (nombre) VALUES ('economico'), ('standar'), ('delicado');
    INSERT INTO estados (nombre) VALUES ('pendiente'), ('en proceso'), ('listo'), ('entregado'), ('cancelado');
END;
$$;