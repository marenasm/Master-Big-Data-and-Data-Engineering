USE segunda_parte; 

-- ============================================================
--  DATOS DE REFERENCIA PARA LAS CONSULTAS:
--  ·  Q3  → cargoE = 'Secretaria' / 'Secretario'
--  ·  Q7  → dept 2000 (RRHH): algunos con comisión
--  ·  Q9  → dept 3000 (TECNOLOGIA): 6 empleados
--  ·  Q10 → comisionE > salEmp   : E001,E004,E005,E022,E027,E042
--  ·  Q11 → comisionE ≤ 30% sal  : E003,E009,E010,E028
--  ·  Q12 → comisionE > 10.000 € : E002(15000), E042(12000)
--  ·  Q13 → nombre 'M%' + comisión + VENTAS: E001,E002,E003,E005
--  ·  Q14 → sal BETWEEN com/2 AND com: E001,E004,E005,E022,E027
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- 1. DEPARTAMENTOS
--    codDirector en NULL por ahora (referencia circular).
--    Se actualiza al final con UPDATE.
-- ─────────────────────────────────────────────────────────────
INSERT INTO departamento (codDepto, nombreDepto, Ciudad) VALUES
  ('0100', 'DIRECCION',      'Madrid'),
  ('1000', 'VENTAS',         'Madrid'),
  ('2000', 'RRHH',           'Barcelona'),
  ('3000', 'TECNOLOGIA',     'Madrid'),
  ('4000', 'FINANZAS',       'Valencia'),
  ('5000', 'MARKETING',      'Sevilla'),
  ('6000', 'LOGISTICA',      'Bilbao'),
  ('7000', 'JURIDICO',       'Madrid'),
  ('8000', 'OPERACIONES',    'Zaragoza'),
  ('9000', 'ADMINISTRACION', 'Madrid');

-- ─────────────────────────────────────────────────────────────
-- 2. EMPLEADOS — Nivel 0: CEO (sin jefe superior)
-- ─────────────────────────────────────────────────────────────
INSERT INTO empleado
  (nDIEmp, nomEmp, sexEmp, fedNac, fecIncorporacion, salEmp, comisionE, cargoE, jefeID, codDepto)
VALUES
  ('E041','Ricardo Molina',  'M','1970-03-15','2000-01-01', 12000, NULL,  'CEO',      NULL,   '0100');

-- ─────────────────────────────────────────────────────────────
-- 3. EMPLEADOS — Nivel 1: Directores (jefeID = E041)
--    E002 Manuel: salEmp=42000 > 40.000 → satisface Q13
--    E042 Monica: comisionE=12000 → satisface Q10 y Q12
-- ─────────────────────────────────────────────────────────────
INSERT INTO empleado
  (nDIEmp, nomEmp, sexEmp, fedNac, fecIncorporacion, salEmp, comisionE, cargoE, jefeID, codDepto)
VALUES
  ('E002','Manuel Rodriguez','M','1978-07-22','2015-06-01', 42000, 15000, 'Director', 'E041', '1000'),
  ('E007','Carmen Fernandez','F','1980-05-10','2010-04-01',  4200,  NULL, 'Director', 'E041', '2000'),
  ('E011','Javier Ruiz',     'M','1975-11-20','2008-01-15',  5500,  NULL, 'Director', 'E041', '3000'),
  ('E017','Patricia Blanco', 'F','1979-08-11','2007-09-01',  5000,  NULL, 'Director', 'E041', '4000'),
  ('E021','Alberto Ortiz',   'M','1977-10-30','2005-03-01',  5200,  NULL, 'Director', 'E041', '5000'),
  ('E025','Raquel Iglesias', 'F','1981-02-14','2009-06-01',  4600,  NULL, 'Director', 'E041', '6000'),
  ('E029','Beatriz Aguilar', 'F','1978-06-20','2006-02-01',  5800,  NULL, 'Director', 'E041', '7000'),
  ('E033','Sergio Rubio',    'M','1976-09-12','2004-01-20',  5100,  NULL, 'Director', 'E041', '8000'),
  ('E037','Ignacio Campos',  'M','1982-04-25','2011-03-01',  4400,  NULL, 'Director', 'E041', '9000'),
  ('E042','Monica Palomino', 'F','1975-08-09','2002-06-01',  8500, 12000, 'Director', 'E041', '0100'),
  ('E044','Hector Fuentes',  'M','1978-05-17','2005-11-15',  7200,  NULL, 'Director', 'E041', '0100');

-- ─────────────────────────────────────────────────────────────
-- 4. EMPLEADOS — Nivel 2: Gerente intermedio (jefeID = E011)
--    Se inserta antes que E016, que tiene jefeID = E015
-- ─────────────────────────────────────────────────────────────
INSERT INTO empleado
  (nDIEmp, nomEmp, sexEmp, fedNac, fecIncorporacion, salEmp, comisionE, cargoE, jefeID, codDepto)
VALUES
  ('E015','Roberto Herrera', 'M','1986-04-03','2014-07-15',  4200,  NULL, 'Gerente',  'E011', '3000');

-- ─────────────────────────────────────────────────────────────
-- 5. EMPLEADOS — Nivel 3: Resto del equipo (44 total)
--
--  Condiciones cubiertas por diseño:
--  ┌──────┬─────────────────┬────────┬──────────┬─────────────────────────────────────┐
--  │ ID   │ Nombre          │  sal   │ comision │ Queries que satisface               │
--  ├──────┼─────────────────┼────────┼──────────┼─────────────────────────────────────┤
--  │ E001 │ Maria Gonzalez  │  2500  │   3200   │ Q10(3200>2500) Q13(M+com+VENTAS)    │
--  │      │                 │        │          │ Q14(1250≤2500≤3200)                 │
--  │ E003 │ Miguel Torres   │  3200  │    800   │ Q11(800≤960) Q13(M+com+VENTAS)      │
--  │ E004 │ Laura Jimenez   │  2000  │   3500   │ Q10(3500>2000) Q14(1750≤2000≤3500)  │
--  │ E005 │ Marcos Perez    │  1500  │   2000   │ Q10(2000>1500) Q13(M+com+VENTAS)    │
--  │      │                 │        │          │ Q14(1000≤1500≤2000)                 │
--  │ E009 │ Pablo Garcia    │  3500  │    800   │ Q11(800≤1050)                       │
--  │ E010 │ Isabel Lopez    │  2800  │    400   │ Q11(400≤840)                        │
--  │ E022 │ Natalia Munoz   │  2400  │   4800   │ Q10(4800>2400) Q14(2400≤2400≤4800)  │
--  │ E027 │ Teresa Pena     │  2900  │   5500   │ Q10(5500>2900) Q14(2750≤2900≤5500)  │
--  │ E028 │ Alvaro Ramos    │  4000  │   1000   │ Q11(1000≤1200)                      │
--  └──────┴─────────────────┴────────┴──────────┴─────────────────────────────────────┘
-- ─────────────────────────────────────────────────────────────
INSERT INTO empleado
  (nDIEmp, nomEmp, sexEmp, fedNac, fecIncorporacion, salEmp, comisionE, cargoE, jefeID, codDepto)
VALUES
  -- ── VENTAS (1000) ────────────────────────────────────────
  ('E001','Maria Gonzalez',  'F','1985-03-15','2020-01-10',  2500,  3200, 'Comercial',  'E002','1000'),
  ('E003','Miguel Torres',   'M','1990-11-30','2019-03-15',  3200,   800, 'Analista',   'E002','1000'),
  ('E004','Laura Jimenez',   'F','1992-04-18','2021-07-01',  2000,  3500, 'Comercial',  'E002','1000'),
  ('E005','Marcos Perez',    'M','1988-09-05','2018-02-20',  1500,  2000, 'Comercial',  'E002','1000'),
  ('E006','Ana Martin',      'F','1995-12-01','2022-09-01',  2000,  NULL, 'Secretaria', 'E002','1000'),

  -- ── RRHH (2000) ──────────────────────────────────────────
  ('E008','Rosa Sanchez',    'F','1994-08-25','2020-11-15',  1800,  NULL, 'Secretaria', 'E007','2000'),
  ('E009','Pablo Garcia',    'M','1987-03-30','2016-09-10',  3500,   800, 'Tecnico',    'E007','2000'),
  ('E010','Isabel Lopez',    'F','1991-01-15','2019-05-20',  2800,   400, 'Tecnico',    'E007','2000'),

  -- ── TECNOLOGIA (3000) ────────────────────────────────────
  ('E012','Sofia Moreno',    'F','1989-06-14','2017-03-01',  3800,  NULL, 'Analista',   'E011','3000'),
  ('E013','Andres Diaz',     'M','1993-02-28','2020-08-01',  3200,  NULL, 'Tecnico',    'E011','3000'),
  ('E014','Elena Castro',    'F','1991-09-17','2018-11-10',  3500,  NULL, 'Analista',   'E011','3000'),
  ('E016','Lucia Vargas',    'F','1996-07-22','2022-01-10',  2800,  NULL, 'Tecnico',    'E015','3000'),

  -- ── FINANZAS (4000) ──────────────────────────────────────
  ('E018','Luis Romero',     'M','1990-12-05','2018-04-15',  2200,  NULL, 'Secretario', 'E017','4000'),
  ('E019','Marta Navarro',   'F','1988-03-22','2016-10-01',  3400,  NULL, 'Contable',   'E017','4000'),
  ('E020','Carlos Molina',   'M','1983-07-19','2012-05-20',  3800,  NULL, 'Contable',   'E017','4000'),

  -- ── MARKETING (5000) ─────────────────────────────────────
  ('E022','Natalia Munoz',   'F','1992-05-07','2019-07-15',  2400,  4800, 'Comercial',  'E021','5000'),
  ('E023','Pilar Serrano',   'F','1994-11-13','2021-02-01',  1900,  NULL, 'Secretaria', 'E021','5000'),
  ('E024','Diego Mendoza',   'M','1986-08-28','2015-12-10',  3200,  NULL, 'Analista',   'E021','5000'),

  -- ── LOGISTICA (6000) ─────────────────────────────────────
  ('E026','Fernando Calvo',  'M','1993-09-25','2020-03-15',  2000,  NULL, 'Secretario', 'E025','6000'),
  ('E027','Teresa Pena',     'F','1989-04-10','2017-08-20',  2900,  5500, 'Tecnico',    'E025','6000'),
  ('E028','Alvaro Ramos',    'M','1991-12-03','2019-11-01',  4000,  1000, 'Tecnico',    'E025','6000'),

  -- ── JURIDICO (7000) ──────────────────────────────────────
  ('E030','Emilio Santos',   'M','1985-01-08','2013-09-15',  4200,  NULL, 'Tecnico',    'E029','7000'),
  ('E031','Veronica Cruz',   'F','1993-07-16','2021-04-01',  3000,  NULL, 'Tecnico',    'E029','7000'),
  ('E032','Adriana Flores',  'F','1996-03-29','2022-06-15',  1950,  NULL, 'Secretaria', 'E029','7000'),

  -- ── OPERACIONES (8000) ───────────────────────────────────
  ('E034','Nuria Medina',    'F','1990-05-04','2018-06-01',  3100,  NULL, 'Tecnico',    'E033','8000'),
  ('E035','Oscar Guerrero',  'M','1987-11-27','2015-04-10',  3400,  NULL, 'Tecnico',    'E033','8000'),
  ('E036','Claudia Vega',    'F','1994-02-16','2021-09-20',  2600,  NULL, 'Tecnico',    'E033','8000'),

  -- ── ADMINISTRACION (9000) ────────────────────────────────
  ('E038','Amparo Reyes',    'F','1992-10-18','2020-01-15',  2100,  NULL, 'Secretaria', 'E037','9000'),
  ('E039','Jesus Bravo',     'M','1988-07-31','2016-11-10',  3200,  NULL, 'Tecnico',    'E037','9000'),
  ('E040','Sonia Delgado',   'F','1995-01-22','2022-05-01',  2400,  NULL, 'Contable',   'E037','9000'),

  -- ── DIRECCION (0100) ─────────────────────────────────────
  ('E043','Sandra Vidal',    'F','1990-12-22','2015-09-01',  3500,  NULL, 'Secretaria', 'E042','0100');

-- ─────────────────────────────────────────────────────────────
-- 6. Asignar directores a sus departamentos
--    Ahora que los empleados existen, resolvemos la FK diferida
-- ─────────────────────────────────────────────────────────────
UPDATE departamento SET codDirector = 'E041' WHERE codDepto = '0100';
UPDATE departamento SET codDirector = 'E002' WHERE codDepto = '1000';
UPDATE departamento SET codDirector = 'E007' WHERE codDepto = '2000';
UPDATE departamento SET codDirector = 'E011' WHERE codDepto = '3000';
UPDATE departamento SET codDirector = 'E017' WHERE codDepto = '4000';
UPDATE departamento SET codDirector = 'E021' WHERE codDepto = '5000';
UPDATE departamento SET codDirector = 'E025' WHERE codDepto = '6000';
UPDATE departamento SET codDirector = 'E029' WHERE codDepto = '7000';
UPDATE departamento SET codDirector = 'E033' WHERE codDepto = '8000';
UPDATE departamento SET codDirector = 'E037' WHERE codDepto = '9000';

-- ─────────────────────────────────────────────────────────────
-- Verificacióndepartamentodepartamentodepartamento
-- ─────────────────────────────────────────────────────────────
SELECT 'DEPARTAMENTOS' AS tabla, COUNT(*) AS total FROM departamento
UNION ALL
SELECT 'EMPLEADOS',              COUNT(*)           FROM empleado;

SELECT * FROM departamento;
SELECT * FROM empleado ORDER BY codDepto, nDIEmp;
