# Política de Seguridad

## 🔒 Versiones Soportadas

| Versión | Soportada          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## 📝 Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad, por favor:

1. **NO** crees un issue público
2. Envía un email a [tu.email@ejemplo.com](mailto:tu.email@ejemplo.com)
3. Incluye:
   - Descripción detallada
   - Pasos para reproducir
   - Posible impacto
   - Sugerencias de mitigación si las tienes

## ⏱️ Proceso y Tiempos

Al recibir un reporte:

1. Confirmaremos recepción en 24 horas
2. Evaluaremos y responderemos en 72 horas:
   - Plan de mitigación
   - Tiempo estimado de resolución
   - Solicitud de información adicional

## 🛡️ Buenas Prácticas

### Para Usuarios
1. Mantén Python y dependencias actualizadas
2. Usa entornos virtuales
3. No exponer puertos seriales innecesariamente
4. Validar entrada de datos de cámara
5. Monitorear logs por actividad sospechosa

### Para Desarrolladores
1. Validar input en funciones críticas
2. Sanitizar datos de la cámara
3. Verificar checksums en comunicación serial
4. No hardcodear credenciales
5. Usar tipos estrictos donde sea posible

## 🔍 Alcance

Consideramos vulnerabilidades de seguridad:

1. Ejecución remota de código
2. Denegación de servicio
3. Bypass de validaciones
4. Manipulación de puntajes
5. Interferencia con hardware

## 🤝 Reconocimiento

Agradecemos a quienes reporten responsablemente. Con autorización:
- Listaremos su nombre/handle en CONTRIBUTORS.md
- Mencionaremos su contribución en release notes