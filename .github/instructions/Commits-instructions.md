# Estructura de Commits

Este documento proporciona una guía para escribir mensajes de commit coherentes y significativos siguiendo la convención [Conventional Commits](https://www.conventionalcommits.org/es) e incorporando íconos de GitHub para mejorar la legibilidad.

## Estructura básica

```text
<tipo>[ámbito opcional]: <descripción>

[cuerpo opcional]

[nota(s) al pie opcional(es)]
```

## Tipos de commits e íconos

| Tipo | Ícono | Descripción |
|------|-------|-------------|
| feat | ✨ | Nueva característica o funcionalidad |
| fix | 🐛 | Corrección de errores |
| docs | 📚 | Cambios en la documentación |
| style | 💎 | Cambios que no afectan el significado del código (espacios, formato, etc.) |
| refactor | ♻️ | Cambios en el código que no corrigen errores ni añaden funcionalidades |
| perf | ⚡ | Mejoras de rendimiento |
| test | 🧪 | Adición o corrección de pruebas |
| build | 🏗️ | Cambios que afectan el sistema de compilación o dependencias externas |
| ci | 👷 | Cambios en archivos de configuración de CI |
| chore | 🔧 | Tareas rutinarias, mantenimiento, etc. |
| revert | ⏪ | Reversión a un commit anterior |

## Ejemplos prácticos

### Nuevas funcionalidades

```text
feat(autenticación): ✨ implementar inicio de sesión con Google

Implementación de OAuth2 con Google para proceso de autenticación.
Incluye:
- Configuración del cliente OAuth2
- Manejo de tokens de acceso
- Redirección segura post-autenticación
```

### Corrección de errores

```text
fix(api): 🐛 corregir error en endpoint de usuarios

El endpoint retornaba código 500 cuando el usuario no existía en lugar
de un 404 adecuado.
```

### Documentación

```text
docs(readme): 📚 actualizar instrucciones de instalación

Actualización de los pasos de instalación para incluir los nuevos
requisitos del sistema y variables de entorno necesarias.
```

## Ámbitos comunes

Los ámbitos ayudan a especificar la parte del proyecto afectada. Algunos ejemplos:

- **api**: Cambios relacionados con la API
- **auth**: Autenticación y autorización
- **core**: Funcionalidad central
- **ui**: Interfaz de usuario
- **db**: Base de datos
- **config**: Configuración

## Recomendaciones adicionales

1. **Sé conciso pero informativo**: La primera línea no debe exceder los 72 caracteres.
2. **Usa voz imperativa**: "Añadir característica" en lugar de "Añadida característica" o "Añade característica".
3. **Incluye números de issues**: Utiliza palabras clave como "Fixes", "Closes", "Resolves" seguido del número de issue.
4. **Separa los cambios grandes**: Si el commit incluye muchos cambios, considera dividirlo en commits más pequeños y específicos.
5. **Sé consistente**: Mantén el mismo estilo en todos los mensajes de commit del proyecto.
6. **Idioma**: que el mesaje de commit sea en español.