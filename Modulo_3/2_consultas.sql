USE segunda_parte; 

-- ────────────────────────────────────────────────────────────
-- Q3. Empleados cuyo cargo sea 'Secretaria' o 'Secretario'
-- ────────────────────────────────────────────────────────────
SELECT *
FROM   empleado
WHERE  cargoE IN ('Secretaria', 'Secretario');


-- ────────────────────────────────────────────────────────────
-- Q4. Nombre y ciudad de departamentos
--     Orden: nombreDepto ASC · Ciudad DESC
-- ────────────────────────────────────────────────────────────
SELECT nombreDepto,
       Ciudad
FROM   departamento
ORDER BY nombreDepto ASC,
         Ciudad      DESC;


-- ────────────────────────────────────────────────────────────
-- Q5. Nombre y cargo de empleados
--     Orden: cargoE ASC, salEmp ASC
-- ────────────────────────────────────────────────────────────
SELECT nomEmp,
       cargoE,
       salEmp
FROM   empleado
ORDER BY cargoE ASC,
         salEmp ASC;


-- ────────────────────────────────────────────────────────────
-- Q6. Departamento con la suma total de salarios más alta
-- ────────────────────────────────────────────────────────────
SELECT   d.nombreDepto,
         SUM(e.salEmp) AS total_salarios
FROM     departamento d
JOIN     empleado     e ON d.codDepto = e.codDepto
GROUP BY d.codDepto, d.nombreDepto
ORDER BY total_salarios DESC
LIMIT 1;


-- ────────────────────────────────────────────────────────────
-- Q7. Salarios y comisiones del departamento 2000 (RRHH)
--     Orden: comisionE ASC  (NULL aparece primero en MySQL)
-- ────────────────────────────────────────────────────────────
SELECT nomEmp,
       salEmp,
       comisionE
FROM   empleado
WHERE  codDepto = '2000'
ORDER BY comisionE ASC;


-- ────────────────────────────────────────────────────────────
-- Q8. Todas las comisiones distintas, ordenadas por valor
-- ────────────────────────────────────────────────────────────
SELECT DISTINCT comisionE
FROM   empleado
WHERE  comisionE IS NOT NULL
ORDER BY comisionE ASC;


-- ────────────────────────────────────────────────────────────
-- Q9. Empleados del departamento 3000 (TECNOLOGIA)
--     Valor total = salEmp + 5.000 €
--     Orden: nomEmp ASC (alfabético)
-- ────────────────────────────────────────────────────────────
SELECT nomEmp,
       salEmp,
       salEmp + 5000 AS total_a_pagar
FROM   empleado
WHERE  codDepto = '3000'
ORDER BY nomEmp ASC;


-- ────────────────────────────────────────────────────────────
-- Q10. Empleados cuya comisión es superior a su sueldo
-- ────────────────────────────────────────────────────────────
SELECT nomEmp,
       salEmp,
       comisionE
FROM   empleado
WHERE  comisionE > salEmp;


-- ────────────────────────────────────────────────────────────
-- Q11. Empleados cuya comisión es menor o igual al 30% del sueldo
-- ────────────────────────────────────────────────────────────
SELECT nomEmp,
       salEmp,
       comisionE,
       ROUND(salEmp * 0.30, 2) AS limite_30pct
FROM   empleado
WHERE  comisionE <= salEmp * 0.30;


-- ────────────────────────────────────────────────────────────
-- Q12. DNI · nombre · salario · comisión · salario total
--      Solo empleados con comisión > 10.000 €
--      Orden: nDIEmp ASC
-- ────────────────────────────────────────────────────────────
SELECT nDIEmp,
       nomEmp,
       salEmp,
       comisionE,
       salEmp + comisionE AS salario_total
FROM   empleado
WHERE  comisionE > 10000
ORDER BY nDIEmp ASC;


-- ────────────────────────────────────────────────────────────
-- Q13. Empleados que cumplen LAS TRES condiciones:
--      · nombre empieza por 'M'
--      · salario > 40.000 € O tienen comisión
--      · trabajan en el departamento 'VENTAS'
-- ────────────────────────────────────────────────────────────
SELECT e.*
FROM   empleado     e
JOIN   departamento d ON e.codDepto = d.codDepto
WHERE  e.nomEmp    LIKE 'M%'
  AND  ( e.salEmp > 40000 OR e.comisionE IS NOT NULL )
  AND  d.nombreDepto = 'VENTAS';


-- ────────────────────────────────────────────────────────────
-- Q14. Empleados cuyo salario está entre
--      la mitad de su comisión  y  el valor de su comisión
--      Es decir: comision/2 <= salario <= comision
-- ────────────────────────────────────────────────────────────
SELECT nomEmp,
       salEmp,
       comisionE,
       ROUND(comisionE / 2, 2) AS mitad_comision
FROM   empleado
WHERE  comisionE IS NOT NULL
  AND  salEmp BETWEEN comisionE / 2 AND comisionE;


-- ────────────────────────────────────────────────────────────
-- Q15. Salario más alto, más bajo y diferencia entre ambos
-- ────────────────────────────────────────────────────────────
SELECT MAX(salEmp)                    AS sal_maximo,
       MIN(salEmp)                    AS sal_minimo,
       MAX(salEmp) - MIN(salEmp)      AS diferencia
FROM   empleado;


-- ────────────────────────────────────────────────────────────
-- Q16. Número de empleados de sexo femenino y masculino
--      desglosado por departamento
-- ────────────────────────────────────────────────────────────
SELECT   d.nombreDepto,
         SUM(CASE WHEN e.sexEmp = 'F' THEN 1 ELSE 0 END) AS Femenino,
         SUM(CASE WHEN e.sexEmp = 'M' THEN 1 ELSE 0 END) AS Masculino,
         COUNT(*)                                          AS Total
FROM     empleado     e
JOIN     departamento d ON e.codDepto = d.codDepto
GROUP BY d.codDepto, d.nombreDepto
ORDER BY d.nombreDepto ASC;


-- ────────────────────────────────────────────────────────────
-- Q17. Total de salarios por departamento
-- ────────────────────────────────────────────────────────────
SELECT   d.nombreDepto,
         COUNT(e.nDIEmp)   AS num_empleados,
         SUM(e.salEmp)     AS total_salarios,
         AVG(e.salEmp)     AS media_salarial
FROM     departamento d
JOIN     empleado     e ON d.codDepto = e.codDepto
GROUP BY d.codDepto, d.nombreDepto
ORDER BY total_salarios DESC;

-- ════════════════════════════════════════════════════════════
--  Q18. VISTA — Departamento(s) con la suma de salarios más alta
-- ════════════════════════════════════════════════════════════
CREATE OR REPLACE VIEW v_top_salarios AS
SELECT   d.nombreDepto,
         SUM(e.salEmp) AS total_salarios
FROM     departamento d
JOIN     empleado     e ON d.codDepto = e.codDepto
GROUP BY d.codDepto, d.nombreDepto
HAVING   SUM(e.salEmp) = (
            SELECT MAX(suma_depto)
            FROM (
                SELECT   SUM(salEmp) AS suma_depto
                FROM     empleado
                GROUP BY codDepto
            ) AS totales
         );

-- Uso de la vista:
SELECT * FROM v_top_salarios;


-- ════════════════════════════════════════════════════════════
--  Q19. PROCEDIMIENTO ALMACENADO — Replica la consulta Q13
-- ════════════════════════════════════════════════════════════
DROP PROCEDURE IF EXISTS pa_ventas_empleados_M;

DELIMITER //

CREATE PROCEDURE pa_ventas_empleados_M()
BEGIN
    SELECT e.nDIEmp,
           e.nomEmp,
           e.cargoE,
           e.salEmp,
           e.comisionE,
           d.nombreDepto
    FROM   empleado     e
    JOIN   departamento d ON e.codDepto = d.codDepto
    WHERE  e.nomEmp    LIKE 'M%'
      AND  ( e.salEmp > 40000 OR e.comisionE IS NOT NULL )
      AND  d.nombreDepto = 'VENTAS';
END //

DELIMITER ;

-- Llamada al procedimiento:
CALL pa_ventas_empleados_M();


-- ════════════════════════════════════════════════════════════
--  Q20. TRIGGER — Log automático de altas de empleados
-- ════════════════════════════════════════════════════════════

-- ── Tabla de transacciones diarias ──────────────────────────
CREATE TABLE IF NOT EXISTS log_transacciones (
    idLog           INT          AUTO_INCREMENT,
    nDIEmp          VARCHAR(12)  NOT NULL,
    nomEmp          VARCHAR(30),
    codDepto        VARCHAR(4),
    cargoE          VARCHAR(15),
    fechaAlta       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT PK_log PRIMARY KEY (idLog)
);

-- ── Trigger AFTER INSERT ─────────────────────────────────────
DROP TRIGGER IF EXISTS trg_alta_empleado;

DELIMITER //

CREATE TRIGGER trg_alta_empleado
AFTER INSERT ON empleado
FOR EACH ROW
BEGIN
    INSERT INTO log_transacciones (nDIEmp, nomEmp, codDepto, cargoE)
    VALUES (NEW.nDIEmp, NEW.nomEmp, NEW.codDepto, NEW.cargoE);
END //

DELIMITER ;

-- ── Prueba del trigger ───────────────────────────────────────
-- Insertar un empleado de prueba y comprobar que aparece en el log
INSERT INTO empleado
    (nDIEmp, nomEmp, sexEmp, fedNac, fecIncorporacion, salEmp, comisionE, cargoE, jefeID, codDepto)
VALUES
    ('E099', 'Prueba Trigger', 'M', '1995-06-15', CURDATE(), 2500, NULL, 'Tecnico', 'E041', '3000');

SELECT * FROM log_transacciones;
