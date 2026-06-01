CREATE OR REPLACE PROCEDURE seed_initial_laundry_data()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO unidades_limpieza (nombre)
    SELECT v.nombre 
    FROM (VALUES ('canasto'), ('acolchado'), ('calzado')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM unidades_limpieza t WHERE t.nombre = v.nombre
    );

    INSERT INTO modalidades_servicio (nombre)
    SELECT v.nombre 
    FROM (VALUES ('economico'), ('standar'), ('delicado')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM modalidades_servicio t WHERE t.nombre = v.nombre
    );

    INSERT INTO estados (nombre)
    SELECT v.nombre 
    FROM (VALUES ('pendiente'), ('en proceso'), ('listo'), ('entregado'), ('cancelado')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM estados t WHERE t.nombre = v.nombre
    );
END;
$$;
