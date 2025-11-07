# Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Puntuación para Competiciones de Robótica! Este documento provee las pautas y mejores prácticas para contribuir al proyecto.

## 🤝 Código de Conducta

Este proyecto y todos sus participantes están bajo el [Código de Conducta del Contribuidor](https://www.contributor-covenant.org/es/version/2/0/code_of_conduct/). Al participar, se espera que mantengas este código.

## 🚀 Cómo Contribuir

1. **Fork & Clone**
   ```bash
   git clone https://github.com/TU_USERNAME/robotics-scoring-system.git
   cd robotics-scoring-system
   ```

2. **Configura el Entorno**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Crea una Rama**
   ```bash
   git checkout -b feature/nombre-caracteristica
   ```

4. **Realiza tus Cambios**
   - Sigue el estilo de código existente
   - Añade tests para nuevas características
   - Actualiza la documentación según sea necesario

5. **Prueba tus Cambios**
   ```bash
   pytest tests/
   ```

6. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: descripción breve del cambio"
   git push origin feature/nombre-caracteristica
   ```

7. **Abre un Pull Request**
   - Usa el template proporcionado
   - Describe detalladamente tus cambios
   - Vincula issues relacionados

## 📝 Convenciones de Código

- Sigue PEP 8 para Python
- Usa type hints cuando sea posible
- Documenta todas las funciones y clases
- Mantén el coverage de tests > 80%

### Estilo de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva característica
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `test:` Añadir o modificar tests
- `refactor:` Refactorización de código
- `style:` Cambios de formato
- `chore:` Tareas de mantenimiento

## 🧪 Tests

- Usa pytest para tests
- Escribe tests unitarios y de integración
- Verifica coverage con pytest-cov

```bash
pytest --cov=src tests/
```

## 📚 Documentación

- Actualiza README.md si añades características
- Mantén la documentación de API actualizada
- Incluye docstrings en código nuevo
- Actualiza ejemplos si es necesario

## 🐛 Reportar Bugs

1. Usa el template de issue para bugs
2. Incluye pasos para reproducir
3. Adjunta logs y capturas relevantes
4. Indica versión y entorno

## 💡 Proponer Características

1. Usa el template de feature request
2. Describe el problema que resuelve
3. Sugiere una solución
4. Considera alternativas

## 📝 Pull Request Checklist

- [ ] Tests añadidos/actualizados
- [ ] Documentación actualizada
- [ ] Código sigue convenciones
- [ ] Commits son descriptivos
- [ ] CI/Tests pasan
- [ ] Revisado por ti mismo primero

## 🔄 Proceso de Review

1. Los mantenedores revisarán tu PR
2. Pueden pedir cambios
3. Una vez aprobado, será mergeado
4. Los cambios aparecerán en el siguiente release

## 🌟 Reconocimiento

Los contribuidores son listados en CONTRIBUTORS.md y reconocidos en los releases.

¡Gracias por contribuir!
