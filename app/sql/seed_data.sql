CREATE OR REPLACE PROCEDURE seed_initial_laundry_data()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO unidades_limpieza (nombre) 
    VALUES ('canasto'), ('acolchado'), ('calzado')
    ON CONFLICT (nombre) DO NOTHING;

    INSERT INTO modalidades_servicio (nombre) 
    VALUES ('economico'), ('standar'), ('delicado')
    ON CONFLICT (nombre) DO NOTHING;

    INSERT INTO estados (nombre) 
    VALUES ('pendiente'), ('en proceso'), ('listo'), ('entregado'), ('cancelado')
    ON CONFLICT (nombre) DO NOTHING;
END;
$$;
