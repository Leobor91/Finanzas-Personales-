# Estructura de carpetas

```text
nombre_proyecto/
│
├── app/                                # Código fuente principal
│   ├── domain/                         # Capa de dominio (el núcleo)
│   │   ├── entities/                   # Entidades de dominio (objetos de valor)
│   │   │   ├── __init__.py
│   │   │   └── [entity_name].py
│   │   │
│   │   ├── exceptions/                 # Excepciones específicas del dominio
│   │   │   ├── __init__.py
│   │   │   └── domain_exceptions.py
│   │   │
│   │   ├── value_objects/              # Objetos de valor inmutables
│   │   │   ├── __init__.py
│   │   │   └── [value_object_name].py
│   │   │
│   │   ├── repositories/               # Puertos de repositorio (interfaces)
│   │   │   ├── __init__.py
│   │   │   └── [repository_name]_repository.py
│   │   │
│   │   └── services/                   # Servicios de dominio
│   │       ├── __init__.py
│   │       └── [service_name]_service.py
│   │
│   ├── application/                    # Capa de aplicación (casos de uso)
│   │   ├── __init__.py
│   │   ├── dtos/                       # Objetos de transferencia de datos
│   │   │   ├── __init__.py
│   │   │   ├── requests/               # DTOs de entrada
│   │   │   │   ├── __init__.py
│   │   │   │   └── [dto_name]_request.py
│   │   │   │
│   │   │   └── responses/              # DTOs de salida
│   │   │       ├── __init__.py
│   │   │       └── [dto_name]_response.py
│   │   │
│   │   ├── interfaces/                 # Puertos de entrada (interfaces)
│   │   │   ├── __init__.py
│   │   │   └── [use_case_name]_interface.py
│   │   │
│   │   ├── use_cases/                  # Implementaciones de casos de uso
│   │   │   ├── __init__.py
│   │   │   └── [use_case_name].py
│   │   │
│   │   └── mappers/                    # Convertidores entre dominio y DTOs
│   │       ├── __init__.py
│   │       └── [entity_name]_mapper.py
│   │
│   ├── infrastructure/                 # Capa de infraestructura
│   │   ├── __init__.py
│   │   │
│   │   ├── adapters/                   # Adaptadores
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── driving/                # Adaptadores primarios (entrada)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api/                # Adaptadores de API (REST, GraphQL)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── routes/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── [resource_name]_routes.py
│   │   │   │   │   │
│   │   │   │   │   └── controllers/
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       └── [resource_name]_controller.py
│   │   │   │   │
│   │   │   │   ├── cli/                # Adaptadores de línea de comandos
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── commands/
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       └── [command_name]_command.py
│   │   │   │   │
│   │   │   │   └── event_handlers/     # Adaptadores para eventos entrantes
│   │   │   │       ├── __init__.py
│   │   │   │       └── [event_name]_handler.py
│   │   │   │
│   │   │   └── driven/                 # Adaptadores secundarios (salida)
│   │   │       ├── __init__.py
│   │   │       ├── persistence/        # Adaptadores de persistencia
│   │   │       │   ├── __init__.py
│   │   │       │   ├── orm/            # Mappings ORM
│   │   │       │   │   ├── __init__.py
│   │   │       │   │   └── [entity_name]_orm.py
│   │   │       │   │
│   │   │       │   └── repositories/   # Implementaciones de repositorios
│   │   │       │       ├── __init__.py
│   │   │       │       └── [repository_name]_repository_impl.py
│   │   │       │
│   │   │       ├── messaging/          # Adaptadores para mensajería
│   │   │       │   ├── __init__.py
│   │   │       │   ├── publishers/
│   │   │       │   │   ├── __init__.py
│   │   │       │   │   └── [event_name]_publisher.py
│   │   │       │   │
│   │   │       │   └── consumers/
│   │   │       │       ├── __init__.py
│   │   │       │       └── [event_name]_consumer.py
│   │   │       │
│   │   │       └── services/           # Adaptadores para servicios externos
│   │   │           ├── __init__.py
│   │   │           └── [service_name]_service.py
│   │   │
│   │   ├── config/                     # Configuración de la aplicación
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   └── di_container.py         # Contenedor de inyección de dependencias
│   │   │
│   │   └── db/                         # Configuración de base de datos
│   │       ├── __init__.py
│   │       ├── connection.py
│   │       └── migrations/
│   │
│   └── utils/                          # Utilidades compartidas
│       ├── __init__.py
│       └── common/
│           ├── __init__.py
│           └── constants.py
│
├── tests/                              # Pruebas automatizadas
│   ├── __init__.py
│   ├── unit/                           # Tests unitarios
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   └── [entity_name]_test.py
│   │   │
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   └── [use_case_name]_test.py
│   │   │
│   │   └── infrastructure/
│   │       ├── __init__.py
│   │       └── adapters/
│   │           ├── __init__.py
│   │           └── [adapter_name]_test.py
│   │
│   ├── integration/                    # Tests de integración
│   │   ├── __init__.py
│   │   └── infrastructure/
│   │       ├── __init__.py
│   │       └── adapters/
│   │           ├── __init__.py
│   │           └── [adapter_name]_test.py
│   │
│   └── e2e/                            # Tests end-to-end
│       ├── __init__.py
│       └── api/
│           ├── __init__.py
│           └── [endpoint_name]_test.py
│
├── docs/                               # Documentación
│   ├── architecture/
│   ├── api/
│   └── domain/
│
├── scripts/                            # Scripts de utilidad
│   ├── setup.sh
│   └── deploy.sh
│
├── .gitignore
├── pyproject.toml                      # Configuración de dependencias (Poetry)
├── README.md
└── Dockerfile
```

## Explicación de los Componentes Principales

### 1. Capa de Dominio (`app/domain/`)

- **Entidades (`entities/`)**: Objetos que tienen identidad y ciclo de vida. Contienen lógica de negocio esencial.
- **Objetos de Valor (`value_objects/`)**: Objetos inmutables que representan conceptos del dominio sin identidad.
- **Excepciones (`exceptions/`)**: Excepciones específicas del dominio para manejar errores de negocio.
- **Repositorios (`repositories/`)**: Interfaces (puertos) que definen operaciones de persistencia sin definir implementación.
- **Servicios (`services/`)**: Servicios de dominio que encapsulan lógica de negocio que no pertenece a una entidad específica.

### 2. Capa de Aplicación (`app/application/`)

- **DTOs (`dtos/`)**: Objetos para transferir datos entre capas sin exponer detalles internos.
- **Interfaces (`interfaces/`)**: Puertos de entrada que definen contratos para los casos de uso.
- **Casos de Uso (`use_cases/`)**: Implementación de casos de uso específicos de la aplicación.
- **Mappers (`mappers/`)**: Conversores entre entidades de dominio y DTOs.

### 3. Capa de Infraestructura (`app/infrastructure/`)

- **Adaptadores (`adapters/`)**:
  - **Driving/Primarios**: Inician la interacción con la aplicación (controladores API, CLI).
  - **Driven/Secundarios**: Implementaciones concretas de los puertos definidos en el dominio.
- **Configuración (`config/`)**: Configuración de la aplicación, incluyendo inyección de dependencias.
- **Base de Datos (`db/`)**: Configuración y migraciones de base de datos.

## Consideraciones de Diseño

1. **Inversión de Dependencias**: Las dependencias apuntan hacia el dominio, nunca al revés. El dominio no debe depender de ninguna capa externa.

2. **Separación Clara**: Cada capa tiene responsabilidades específicas y bien definidas:

    - **Dominio**: Reglas de negocio
    - **Aplicación**: Coordinación y orquestación de flujos
    - **Infraestructura**: Detalles técnicos y comunicación externa

3. **Testabilidad**: Esta estructura facilita la realización de pruebas al permitir sustituir adaptadores por mocks.

4. **Escalabilidad**: La organización modular permite agregar nuevas capacidades sin modificar el núcleo.
