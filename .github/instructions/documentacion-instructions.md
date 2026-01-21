# Guía para escribir un buen CHANGELOG

Este documento proporciona instrucciones sobre cómo mantener un archivo CHANGELOG efectivo y útil para tu proyecto.

## ¿Qué es un CHANGELOG?

Un CHANGELOG es un archivo que contiene una lista cronológica ordenada de los cambios significativos para cada versión de un proyecto. Su propósito es hacer más fácil para usuarios y contribuidores ver exactamente qué cambios importantes se han realizado entre cada versión del proyecto.

## Principios básicos

- El CHANGELOG está hecho para humanos, no para máquinas
- Debe haber una entrada para cada versión
- Los mismos tipos de cambios deben ser agrupados
- Las versiones y secciones deben ser enlazables
- La versión más reciente va primero
- Se debe mencionar la fecha de lanzamiento de cada versión

## Estructura recomendada

Nuestro formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y sigue los principios de [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

```markdown
# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Sin publicar]

### Added

- Características en desarrollo que se incluirán en la próxima versión

## [X.Y.Z] - AAAA-MM-DD

### Added

- Lista de nuevas características

### Changed

- Lista de cambios en funcionalidades existentes

### Deprecated

- Lista de características que pronto serán eliminadas

### Removed

- Lista de características eliminadas en esta versión

### Fixed

- Lista de errores corregidos

### Security

- Lista de vulnerabilidades solucionadas

[Sin publicar]: https://github.com/usuario/repositorio/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/usuario/repositorio/compare/vX.Y.(Z-1)...vX.Y.Z
```

## Categorías de cambios

- **Added**: Para nuevas características.
- **Changed**: Para cambios en funcionalidades existentes.
- **Deprecated**: Para características que pronto serán eliminadas.
- **Removed**: Para características eliminadas en esta versión.
- **Fixed**: Para cualquier corrección de errores.
- **Security**: Para invitar a los usuarios a actualizar en caso de vulnerabilidades.

## Versionado Semántico (SemVer)

Seguimos Semantic Versioning con el formato X.Y.Z:

- **X (Major)**: Cambios incompatibles con versiones anteriores
- **Y (Minor)**: Nuevas funcionalidades que mantienen compatibilidad
- **Z (Patch)**: Correcciones de errores que mantienen compatibilidad

## Referencias a tickets o requisitos

**IMPORTANTE:** Cada elemento añadido al CHANGELOG DEBE tener una referencia a un ticket, issue, historia de usuario o requisito. Esto garantiza la trazabilidad de los cambios y facilita encontrar información adicional sobre cada cambio.

Formatos de referencias aceptados:

- Referencias a requisitos: `[RF-XXX]`, `[RNF-XXX]`
- Referencias a issues: `(#XXX)`, `(Fixes #XXX)`, `(Resolves #XXX)`
- Referencias a tickets: `(TICKET-XXX)`
- Referencias a historias de usuario: `[HU-XXX]`

Ejemplos:

```markdown
### Added
- [RF-002] Implementación de autenticación de usuarios
- [HU-045] Soporte para múltiples idiomas (Fixes #45)
- [TICKET-123] Nueva interfaz para la sección de reportes
- [RNF-017] Mejora en tiempos de respuesta de la API (<100ms)
```

**Nunca incluyas un elemento en el CHANGELOG sin su correspondiente referencia.**

## Enlaces a comparaciones

Al final del documento, incluye enlaces a las comparaciones entre versiones:

```markdown
[Sin publicar]: https://github.com/usuario/repositorio/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/usuario/repositorio/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/usuario/repositorio/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/usuario/repositorio/releases/tag/v0.1.0
```

## Buenas prácticas

1. **Actualiza el CHANGELOG con cada cambio significativo**, no solo en los lanzamientos.
2. **Mantén una sección "Sin publicar"** para los cambios que aún no han sido lanzados.
3. **Usa lenguaje claro y directo**, evitando jerga técnica innecesaria.
4. **Incluye información relevante para los usuarios**, no detalles internos que solo importan a los desarrolladores.
5. **Asocia cada entrada con su respectiva referencia** (issue, ticket, requisito, etc.)
6. **Ordena las entradas** dentro de cada categoría por importancia o impacto.
7. **Menciona números de issue** cuando sea relevante.
8. **Incluye instrucciones de migración** cuando haya cambios importantes.
9. **Incluye la fecha** de cada lanzamiento.

## Ejemplo real

```markdown
## [1.2.0] - 2023-06-15

### Added
- [RF-042] Funcionalidad de exportación a PDF para reportes
- [HU-035] Nuevos temas visuales para el panel de control
- [TICKET-789] Soporte para autenticación mediante Google

### Changed
- [RF-100] Mejora en el rendimiento del procesamiento de imágenes
- [INFRA-22] Actualización de dependencias a las últimas versiones estables

### Fixed
- [BUG-123] Solución al problema de carga infinita en dispositivos móviles (#123)
- [QA-56] Corrección de la visualización incorrecta de gráficos en Safari
- [LANG-08] Arreglo de errores tipográficos en la interfaz en español
```

---

Recuerda que un buen CHANGELOG comunica claramente a los usuarios finales qué ha cambiado y cómo esos cambios podrían afectarles, facilitando la decisión de actualizar y entender qué obtendrán con cada nueva versión.