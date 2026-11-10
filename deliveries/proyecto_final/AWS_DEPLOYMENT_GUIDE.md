# Despliegue futuro de InmoScore

El proyecto recibido funciona como prototipo local. Este documento es un plan de continuidad, no una receta de despliegue probada. No hay una URL pública operativa acreditada en el paquete.

Para la presentación actual sigan **../03_instalacion_y_ejecucion.md**. No necesitan AWS ni otro servicio de pago.

## Qué existe

- Aplicación Next.js y API.
- Catálogo JSON local con predicciones preparadas.
- Contrato de persistencia en db/repository.ts.
- Implementación SQLite y migración del esquema.
- Scripts de desarrollo, compilación e inicio local.

## Qué tendría que resolverse antes de publicarlo

| Tema | Trabajo pendiente |
|---|---|
| Persistencia compartida | Implementar y probar un adaptador distinto si se necesitan varias instancias; el adaptador PostgreSQL no está incluido. |
| Empaquetado | Incluir scripts de arranque, datos, modelo si se prepara allí y todos los recursos que realmente necesita el servidor. No existe un contenedor verificado en esta entrega. |
| Identidad | Definir verificación y recuperación de cuentas, controles de acceso y configuración de cookies para el dominio elegido. |
| Operación | Configurar HTTPS, copias de seguridad, secretos y registros de errores. |
| Datos | Verificar permisos, disponibilidad de las fuentes y forma de actualizar el catálogo. |
| Pruebas | Validar el recorrido completo en el entorno elegido antes de compartir una URL pública. |

Los servicios mencionados por el equipo —ECS, RDS y API Gateway— son opciones de una etapa futura. Su presencia en la documentación no significa que estén contratados, configurados o funcionando. Tampoco basta con configurar DATABASE_URL para convertir la implementación SQLite en PostgreSQL.

No se mantiene una estimación de costos: el paquete no contiene una configuración desplegada ni un presupuesto validado. Esa evaluación debe hacerse cuando exista una necesidad concreta de publicación.

La prioridad de esta entrega es que los alumnos entiendan y demuestren el producto local. El despliegue no forma parte de las tareas sencillas de cierre.
