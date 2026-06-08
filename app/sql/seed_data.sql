CREATE OR REPLACE PROCEDURE seed_initial_laundry_data()
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO roles (nombre)
    SELECT v.nombre 
    FROM (VALUES ('Administrador'), ('Operador'), ('Cliente')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM roles t WHERE t.nombre = v.nombre
    );

    INSERT INTO unidades_limpieza (nombre)
    SELECT v.nombre 
    FROM (VALUES ('Canasto'), ('Acolchado'), ('Calzado')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM unidades_limpieza t WHERE t.nombre = v.nombre
    );

    INSERT INTO modalidades_servicio (nombre)
    SELECT v.nombre 
    FROM (VALUES ('Económico'), ('Standar'), ('Delicado')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM modalidades_servicio t WHERE t.nombre = v.nombre
    );

    INSERT INTO estados (nombre)
    SELECT v.nombre 
    FROM (VALUES ('Pendiente'), ('En Proceso'), ('Listo'), ('Entregado'), ('Cancelado')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM estados t WHERE t.nombre = v.nombre
    );

    INSERT INTO metodos_pago (nombre)
    SELECT v.nombre 
    FROM (VALUES ('Mercado Pago')) AS v(nombre)
    WHERE NOT EXISTS (
        SELECT 1 FROM metodos_pago t WHERE t.nombre = v.nombre
    );

END;
$$;