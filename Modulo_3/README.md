# Módulo 3 — Modelado y Consulta de Bases de Datos Relacionales

Este módulo contiene dos ejercicios prácticos de diseño, poblado y consulta de bases de datos relacionales con **MySQL**. Cada parte tiene su propia base de datos, esquema y conjunto de consultas, cubriendo desde un sistema clínico hasta una gestión de recursos humanos.

---

## Estructura del módulo

```
Modulo_3/
├── 1_crear.sql           # DDL: esquema del sistema hospitalario
├── 1_llenar.sql          # DML: datos de ejemplo para el sistema hospitalario
├── 1_consultas.sql       # Consultas SELECT y JOINs sobre el sistema hospitalario
├── 1_diagrama.mwb        # Diagrama ER en formato MySQL Workbench
├── 2_crear.sql           # DDL: esquema del sistema de empleados y departamentos
├── 2_llenar.sql          # DML: datos de ejemplo para el sistema de RRHH
├── 2_consultas.sql       # Consultas avanzadas, vistas, procedimientos y triggers
├── diagrama_relacional.png  # Diagrama relacional exportado
└── Tarea modelado de datos.pdf  # Enunciado de la tarea
```

---

## Parte 1 — Sistema Hospitalario de Trasplantes

### Descripción

Base de datos diseñada para gestionar el ciclo completo de atención a pacientes sometidos a procedimientos de trasplante. Modela desde la operación quirúrgica hasta el seguimiento post-trasplante, la medicación y la facturación.

### Modelo de datos

| Tabla | Descripción |
|---|---|
| `MEDICO` | Especialistas del hospital (cirujanos, nefrólogos, cardiólogos, etc.) |
| `PACIENTE` | Pacientes con su historial médico y datos de contacto |
| `OPERACION_TRASPLANTE` | Registro de cada procedimiento: tipo, zonas donante/receptora, médico y paciente |
| `CITA` | Agenda de citas médicas con confirmación |
| `VISITA_SEGUIMIENTO` | Visitas post-trasplante con observaciones, resultados y recomendaciones |
| `DOCUMENTO_ARCHIVO` | Documentos clínicos adjuntos (biopsias, radiografías, consentimientos...) |
| `MEDICACION_TRATAMIENTO` | Inmunosupresores y otros tratamientos con dosis y duración |
| `FACTURA_PAGO` | Facturación de los procedimientos con estado de pago |

### Consultas incluidas

- Listados básicos de cada entidad
- JOINs entre 3 y 4 tablas para obtener información cruzada (citas con paciente y médico, historial completo por paciente, etc.)

---

## Parte 2 — Sistema de Empleados y Departamentos

### Descripción

Base de datos para la gestión de recursos humanos de una empresa con múltiples departamentos. Incluye una jerarquía de empleados (autorreferencia), asignación de directores por departamento y una relación circular resuelta mediante FK diferida con `ALTER TABLE`.

### Modelo de datos

| Tabla | Descripción |
|---|---|
| `departamento` | Departamentos de la empresa con ciudad y director asignado |
| `empleado` | Empleados con cargo, salario, comisión y referencia a su jefe directo |
| `log_transacciones` | Tabla auxiliar para el log de altas de empleados (usada por el trigger) |

**Aspectos técnicos destacados:**
- Autorreferencia en `empleado` (`jefeID → nDIEmp`)
- FK circular resuelta con `ALTER TABLE` diferido (`departamento.codDirector → empleado.nDIEmp`)
- Restricción `CHECK` sobre el campo `sexEmp`

### Consultas incluidas

Las consultas cubren un amplio espectro de SQL:

| Query | Descripción |
|---|---|
| Q3 | Filtrar empleados por cargo |
| Q4–Q5 | Ordenación multicolumna |
| Q6 | Departamento con mayor masa salarial (`GROUP BY` + `ORDER BY`) |
| Q7–Q8 | Filtros por departamento y comisiones distintas |
| Q9 | Columnas calculadas (salario + incremento) |
| Q10–Q11 | Comparación entre columnas (comisión vs. salario) |
| Q12 | Salario total con comisión, filtrado y ordenado |
| Q13 | Condiciones compuestas con `AND`/`OR` y `JOIN` |
| Q14 | `BETWEEN` con expresiones calculadas |
| Q15 | Funciones de agregación: `MAX`, `MIN`, diferencia |
| Q16 | Desglose por sexo y departamento con `CASE WHEN` |
| Q17 | Totales salariales con `COUNT`, `SUM` y `AVG` |
| Q18 | **Vista** con subconsulta para el top salarial |
| Q19 | **Procedimiento almacenado** que replica Q13 |
| Q20 | **Trigger** `AFTER INSERT` para log automático de altas |

---

## Cómo ejecutar

1. Tener **MySQL 8+** instalado (o usar MySQL Workbench).
2. Para cada parte, ejecutar los scripts en orden:

```sql
-- Parte 1
source 1_crear.sql;
source 1_llenar.sql;
source 1_consultas.sql;

-- Parte 2
source 2_crear.sql;
source 2_llenar.sql;
source 2_consultas.sql;
```

> Cada script de creación incluye `DROP DATABASE IF EXISTS` al inicio, por lo que puede ejecutarse de forma idempotente.

---

## Contexto académico

Ejercicio práctico del **Máster en Big Data e Ingeniería de Datos**, enfocado en el diseño relacional, normalización, integridad referencial y uso avanzado de SQL: vistas, procedimientos almacenados y triggers.
