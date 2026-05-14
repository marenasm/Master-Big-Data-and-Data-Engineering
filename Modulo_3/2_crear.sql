DROP DATABASE IF EXISTS segunda_parte;
CREATE DATABASE segunda_parte
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;

USE segunda_parte;

-- ─────────────────────────────────────────────────────────────
--  TABLA: departamento
--  NOTA: codDirector es FK → empleado, pero empleado aún no
--        existe. Se declara sin FK y se añade con ALTER después.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE departamento (
    codDepto    VARCHAR(4)   NOT NULL,
    nombreDepto VARCHAR(20)  NOT NULL,
    Ciudad      VARCHAR(15),
    codDirector VARCHAR(12),                        -- FK diferida (ver ALTER al final)

    CONSTRAINT PK_departamento PRIMARY KEY (codDepto)
);

-- ─────────────────────────────────────────────────────────────
--  TABLA: empleado
--  · jefeID  → autorreferencia a empleado (el propio jefe)
--  · codDepto → FK a departamento
--  · sexEmp  → sólo 'M' o 'F'  (CHECK constraint)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE empleado (
    nDIEmp           VARCHAR(12)  NOT NULL,         -- DNI / ID del empleado
    nomEmp           VARCHAR(30)  NOT NULL,
    sexEmp           CHAR(1),
    fedNac           DATE,
    fecIncorporacion DATE,
    salEmp           FLOAT,
    comisionE        FLOAT,
    cargoE           VARCHAR(15),
    jefeID           VARCHAR(12),                   -- FK autorreferencial
    codDepto         VARCHAR(4),                    -- FK a departamento

    CONSTRAINT PK_empleado      PRIMARY KEY (nDIEmp),
    CONSTRAINT FK_emp_depto     FOREIGN KEY (codDepto)
                                    REFERENCES departamento(codDepto),
    CONSTRAINT FK_emp_jefe      FOREIGN KEY (jefeID)
                                    REFERENCES empleado(nDIEmp),
    CONSTRAINT CK_sexo          CHECK (sexEmp IN ('M','F'))
);

-- ─────────────────────────────────────────────────────────────
--  FK DIFERIDA: departamento.codDirector → empleado.nDIEmp
--  Se añade ahora que la tabla empleado ya existe.
-- ─────────────────────────────────────────────────────────────
ALTER TABLE departamento
    ADD CONSTRAINT FK_depto_director
        FOREIGN KEY (codDirector) REFERENCES empleado(nDIEmp);

-- ─────────────────────────────────────────────────────────────
--  Verificación de estructura
-- ─────────────────────────────────────────────────────────────
DESCRIBE departamento;
DESCRIBE empleado;
SHOW TABLES;
