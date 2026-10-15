# Gramática de Pāṇini — Traducción al español

Sitio web interactivo para consultar la traducción al español de la *Aṣṭādhyāyī* de Pāṇini (versión de Anselmo Hernández Quiroz 2021), con navegación jerárquica, búsqueda avanzada, referencias cruzadas y visualización de pratyāhāras y anexos.

> **Fuente de verdad:** el archivo `.docx` original. Nunca se sobrescribe. Permanece en el disco duro del desarrollador.
> Todo el pipeline es idempotente y versionado.

---

## Tabla de contenidos

- [Objetivo](#objetivo)
- [Arquitectura de alto nivel](#arquitectura-de-alto-nivel)
- [Principios de integridad](#principios-de-integridad)
- [Estructura de los sūtras](#estructura-de-los-sūtras)
- [Modelo de datos (PostgreSQL)](#modelo-de-datos-postgresql)
- [Formato intermedio (JSONL)](#formato-intermedio-jsonl)
- [Pipeline de extracción](#pipeline-de-extracción)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Stack tecnológico](#stack-tecnológico)
- [API](#api)
- [Frontend](#frontend)
- [Plan de trabajo por fases](#plan-de-trabajo-por-fases)
- [Decisiones de diseño](#decisiones-de-diseño)
- [Licencia](#licencia)

---

## Objetivo

1. **Ingesta fiel** del `.docx` (sánscrito + español + estructura de sūtras, comentarios, notas, referencias cruzadas).
2. **Modelo de datos** que capture la estructura jerárquica y semántica de la *Aṣṭādhyāyī* y las anotaciones.
3. **Pipeline de exportación** a una base de datos.
4. **Capa web dinámica, interactiva e intuitiva** (navegación por *adhyāya* / *pāda* / *sūtra*, búsqueda, cross-references, visualización de pratyāhāras, etc.).

---

## Arquitectura de alto nivel
