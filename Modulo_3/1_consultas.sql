USE primera_parte;

-- Ver todos los médicos
SELECT * FROM MEDICO;

-- Ver todos los pacientes
SELECT * FROM PACIENTE;

-- Ver todas las operaciones
SELECT * FROM OPERACION_TRASPLANTE;

-- Ver todas las citas
SELECT * FROM CITA;

-- Ver todas las visitas de seguimiento
SELECT * FROM VISITA_SEGUIMIENTO;

-- Ver todos los documentos
SELECT * FROM DOCUMENTO_ARCHIVO;

-- Ver todas las medicaciones
SELECT * FROM MEDICACION_TRATAMIENTO;

-- Ver todas las facturas
SELECT * FROM FACTURA_PAGO;

-- -------------------------------------------------------
-- JOIN 1: Citas con nombre del paciente y del médico
-- Une 3 tablas: CITA + PACIENTE + MEDICO
-- -------------------------------------------------------
SELECT
    C.ID_CITA,
    P.NOMBRE        AS PACIENTE,
    M.NOMBRE        AS MEDICO,
    C.FECHA_HORA,
    C.MOTIVO,
    C.CONFIRMACION
FROM CITA C
JOIN PACIENTE P ON C.ID_PACIENTE = P.ID_PACIENTE
JOIN MEDICO   M ON C.ID_MEDICO   = M.ID_MEDICO;

-- -------------------------------------------------------
-- JOIN 2: Operaciones con nombre del paciente y del médico
-- Une 3 tablas: OPERACION_TRASPLANTE + PACIENTE + MEDICO
-- -------------------------------------------------------
SELECT
    O.ID_OPERACION,
    P.NOMBRE            AS PACIENTE,
    M.NOMBRE            AS MEDICO,
    M.ESPECIALIDAD,
    O.FECHA,
    O.TIPO_PROCEDIMIENTO,
    O.ZONA_DONANTE,
    O.ZONA_RECEPTORA
FROM OPERACION_TRASPLANTE O
JOIN PACIENTE P ON O.ID_PACIENTE = P.ID_PACIENTE
JOIN MEDICO   M ON O.ID_MEDICO   = M.ID_MEDICO;

-- -------------------------------------------------------
-- JOIN 3: Visitas de seguimiento con paciente y médico
-- -------------------------------------------------------
SELECT
    V.ID_VISITA,
    P.NOMBRE        AS PACIENTE,
    M.NOMBRE        AS MEDICO,
    V.FECHA,
    V.OBSERVACIONES,
    V.RESULTADOS,
    V.RECOMENDACIONES
FROM VISITA_SEGUIMIENTO V
JOIN PACIENTE P ON V.ID_PACIENTE = P.ID_PACIENTE
JOIN MEDICO   M ON V.ID_MEDICO   = M.ID_MEDICO;

-- -------------------------------------------------------
-- JOIN 4: Medicación con nombre del paciente
-- -------------------------------------------------------
SELECT
    MT.ID_MEDICACION,
    P.NOMBRE        AS PACIENTE,
    MT.NOMBRE       AS MEDICAMENTO,
    MT.DOSIS,
    MT.FRECUENCIA,
    MT.DURACION,
    MT.FECHA_INICIO,
    MT.FECHA_FIN
FROM MEDICACION_TRATAMIENTO MT
JOIN PACIENTE P ON MT.ID_PACIENTE = P.ID_PACIENTE;

-- -------------------------------------------------------
-- JOIN 5: Facturas con nombre del paciente
-- -------------------------------------------------------
SELECT
    F.ID_FACTURA,
    P.NOMBRE        AS PACIENTE,
    F.FECHA,
    F.CONCEPTO,
    F.MONTO,
    F.ESTADO_PAGO
FROM FACTURA_PAGO F
JOIN PACIENTE P ON F.ID_PACIENTE = P.ID_PACIENTE;

-- -------------------------------------------------------
-- JOIN 6 : Historial completo por paciente
-- Une 4 tablas: PACIENTE + OPERACION + MEDICACION + FACTURA
-- -------------------------------------------------------
SELECT
    P.NOMBRE                    AS PACIENTE,
    O.TIPO_PROCEDIMIENTO        AS OPERACION,
    O.FECHA                     AS FECHA_OPERACION,
    MT.NOMBRE                   AS MEDICAMENTO,
    MT.DOSIS,
    F.MONTO,
    F.ESTADO_PAGO
FROM PACIENTE P
JOIN OPERACION_TRASPLANTE   O  ON P.ID_PACIENTE = O.ID_PACIENTE
JOIN MEDICACION_TRATAMIENTO MT ON P.ID_PACIENTE = MT.ID_PACIENTE
JOIN FACTURA_PAGO           F  ON P.ID_PACIENTE = F.ID_PACIENTE;