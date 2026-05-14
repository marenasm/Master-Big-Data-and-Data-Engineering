# Módulo 2 — Arquitectura de Datos: Caso FARMIA en Azure

Este módulo presenta el diseño de una arquitectura de datos moderna en la nube para **FARMIA**, una empresa del sector farmacéutico. El trabajo explora cómo estructurar, almacenar y procesar grandes volúmenes de datos usando los servicios de **Microsoft Azure**.

---

## Contenido

| Archivo | Descripción |
|---|---|
| `ARQUITECTURA DE DATOS FARMIA EN AZURE.pdf` | Documento completo con el diseño de la arquitectura, justificación de decisiones técnicas y diagrama de componentes |

---

## Resumen del caso

El documento aborda la necesidad de FARMIA de consolidar sus fuentes de datos dispersas en una plataforma centralizada, escalable y segura. Se propone una arquitectura basada en los siguientes pilares:

- **Ingesta de datos** desde fuentes heterogéneas (ERP, sistemas de ventas, datos clínicos)
- **Almacenamiento** en capas (raw, curated, analytics) usando Azure Data Lake Storage Gen2
- **Procesamiento** con Azure Databricks y Azure Data Factory para pipelines ETL/ELT
- **Servicio y consumo** a través de Azure Synapse Analytics y Power BI
- **Seguridad y gobernanza** con Azure Active Directory y Microsoft Purview

---

## Tecnologías y servicios tratados

- Azure Data Lake Storage Gen2
- Azure Data Factory
- Azure Databricks
- Azure Synapse Analytics
- Power BI
- Microsoft Purview

---

## Contexto académico

Trabajo desarrollado en el marco del **Máster en Big Data e Ingeniería de Datos**. El objetivo fue aplicar conceptos de arquitectura de datos a un escenario empresarial real, tomando decisiones técnicas justificadas sobre cada componente de la plataforma.
