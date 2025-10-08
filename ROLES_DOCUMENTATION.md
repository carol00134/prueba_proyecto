# Sistema de Control de Acceso por Roles

## Resumen
Se ha implementado un sistema completo de control de acceso basado en roles para controlar qué usuarios pueden acceder a qué módulos del sistema.

## Roles y Permisos

### 🔴 Administrador
- **Acceso completo**: Todos los módulos
- Módulos: `tickets`, `cámaras`, `mapas`, `usuarios`, `puntos geográficos`, `bitácora`, `home`

### 🟡 Operador
- **Acceso limitado**: Gestión operativa
- Módulos: `tickets`, `cámaras`, `mapas`, `home`

### 🟢 Supervisor
- **Acceso de supervisión**: Gestión de recursos y personal
- Módulos: `cámaras`, `usuarios`, `puntos geográficos`, `home`

## Archivos Modificados

### 1. `utils/auth_utils.py` (NUEVO)
- Decoradores `@login_required` y `@role_required`
- Funciones para obtener roles de usuario
- Verificación de acceso a módulos

### 2. Controladores Actualizados
- `controllers/tickets_controller.py`: `@role_required('administrador', 'operador')`
- `controllers/camaras_controller.py`: `@role_required('administrador', 'operador', 'supervisor')`
- `controllers/mapas_controller.py`: `@role_required('administrador', 'operador')`
- `controllers/usuarios_controller.py`: `@role_required('administrador', 'supervisor')`
- `controllers/puntos_geograficos_controller.py`: `@role_required('administrador', 'supervisor')`
- `controllers/bitacora_controller.py`: `@role_required('administrador')`
- `controllers/home_controller.py`: `@login_required`

### 3. `controllers/auth_controller.py`
- Carga roles en la sesión durante el login
- Limpia información de roles en logout

### 4. `app.py`
- Handler para errores 403 (acceso denegado)
- Context processor para roles disponibles en templates

### 5. `template/base.html`
- Menú dinámico que muestra/oculta opciones según rol
- Información de rol en barra de usuario

### 6. `template/error_403.html` (NUEVO)
- Página de error para accesos denegados

## Cómo Funciona

### 1. Login
```python
# En auth_controller.py
user_info = get_user_role_info(username)
session['user_roles'] = user_info['roles_list']
```

### 2. Verificación de Acceso
```python
# En auth_utils.py
@role_required('administrador', 'operador')
def tickets():
    # Solo administradores y operadores pueden acceder
```

### 3. Menú Dinámico
```html
<!-- En base.html -->
{% if 'administrador' in session.get('user_roles', []) or 'operador' in session.get('user_roles', []) %}
<a href="{{ url_for('tickets_routes.tickets') }}">Tickets</a>
{% endif %}
```

## Seguridad

- ✅ Verificación a nivel de controlador (server-side)
- ✅ Menú dinámico (client-side)
- ✅ Registro de intentos de acceso denegado en bitácora
- ✅ Redirección a página de error 403
- ✅ Mantiene funcionalidad existente intacta

## Testing

### Usuarios de Prueba
Ejecutar `Database/setup_test_roles.sql` para crear:
- `admin_test` - Rol administrador
- `operador_test` - Rol operador  
- `supervisor_test` - Rol supervisor

### Script de Prueba
```bash
python test_roles.py
```

## Estructura de Base de Datos

```sql
-- Tabla roles
CREATE TABLE roles (
    id INT PRIMARY KEY,
    nombre VARCHAR(50),
    descripcion TEXT
);

-- Relación usuario-rol (muchos a muchos)
CREATE TABLE usuario_rol (
    usuario_id INT,
    rol_id INT,
    PRIMARY KEY (usuario_id, rol_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);
```

## Notas Importantes

1. **Compatibilidad**: El sistema mantiene toda la funcionalidad existente
2. **Escalabilidad**: Fácil agregar nuevos roles o módulos
3. **Seguridad**: Doble verificación (decorador + menú)
4. **Auditoría**: Todos los accesos se registran en bitácora