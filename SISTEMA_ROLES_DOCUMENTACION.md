# Sistema de Control de Acceso por Roles - Documentación

## Resumen de Permisos Implementados

### 🔐 **ADMINISTRADOR**
- **Acceso completo** a todos los módulos y acciones
- **Dashboard**: Acceso exclusivo al panel de inicio con estadísticas
- **Puede**: Crear, editar, eliminar y ver en todos los módulos
- **Redirección**: Al iniciar sesión va al dashboard `/home`

### 👨‍💼 **SUPERVISOR**
- **Módulos permitidos**: Usuarios, Cámaras, Puntos Geográficos
- **Usuarios**: Solo **VER** (no puede crear usuarios)
- **Cámaras**: Crear, editar, ver (NO eliminar)
- **Puntos Geográficos**: Crear, editar, ver (NO eliminar)
- **Redirección**: Al iniciar sesión va a `/usuarios`

### 👨‍💻 **OPERADOR**
- **Módulos permitidos**: Tickets, Cámaras, Mapas
- **Tickets**: Crear, editar, ver (solo **sus propios tickets**)
- **Cámaras**: Crear, ver (solo **sus propias cámaras**)
- **Mapas**: Solo ver
- **Redirección**: Al iniciar sesión va a `/tickets`

## 🛡️ **Características de Seguridad**

### Filtrado por Propietario
- **Operadores** solo ven sus propios tickets y cámaras
- **Supervisores y Administradores** ven todos los registros
- La asignación de propietario es automática al crear registros

### Control de Interfaz
- **Botones de acción** se muestran/ocultan según permisos
- **Formularios de creación** solo aparecen si el usuario puede crear
- **Menú dinámico** muestra solo módulos permitidos

### Validación Doble
- **Frontend**: Oculta elementos no permitidos
- **Backend**: Valida permisos antes de ejecutar acciones
- **Bitácora**: Registra todos los intentos de acceso

## 📁 **Archivos Modificados**

### Controladores
- `controllers/tickets_controller.py` - Filtrado por operador
- `controllers/camaras_controller.py` - Filtrado por operador
- `controllers/usuarios_controller.py` - Solo lectura para supervisor
- `controllers/auth_controller.py` - Manejo de roles en sesión
- `controllers/home_controller.py` - Solo para administrador
- `controllers/redirect_controller.py` - Redirección por rol

### Templates
- `template/base.html` - Menú dinámico por roles
- `template/tickets.html` - Botones según permisos
- `template/camaras.html` - Botones según permisos
- `template/error_403.html` - Página de acceso denegado

### Sistema de Autorización
- `utils/auth_utils.py` - Sistema completo de permisos
- `utils/template_helpers.py` - Funciones para templates
- `app.py` - Context processor y error handlers

### Base de Datos
- `Database/permisos_corregidos.sql` - Configuración de permisos

## 🔧 **Funciones Principales**

### Para Controladores
```python
@action_required('crear', 'editar')  # Requiere alguna de estas acciones
def mi_funcion():
    pass

can_user_perform_action(username, 'modulo', 'accion')  # Verificar permisos
is_owner_or_admin(username, 'tabla', record_id)  # Verificar propietario
```

### Para Templates
```html
{% if can_perform_action('tickets', 'crear') %}
  <!-- Mostrar formulario de creación -->
{% endif %}

{% if is_admin() %}
  <!-- Solo para administradores -->
{% endif %}
```

## 🚀 **Cómo Usar**

1. **Ejecutar script de permisos**: `Database/permisos_corregidos.sql`
2. **Crear usuarios de prueba** con diferentes roles
3. **Probar cada rol** para verificar permisos
4. **Verificar logs en bitácora** para auditoría

## 📊 **Tabla de Permisos**

| Módulo | Administrador | Supervisor | Operador |
|---------|---------------|------------|----------|
| Dashboard | ✅ | ❌ | ❌ |
| Tickets | ✅ Todos | ❌ | ✅ Solo suyos (C,R,U) |
| Cámaras | ✅ | ✅ (C,R,U) | ✅ Solo suyas (C,R) |
| Mapas | ✅ | ❌ | ✅ (R) |
| Usuarios | ✅ | ✅ (R) | ❌ |
| Puntos Geog. | ✅ | ✅ (C,R,U) | ❌ |
| Bitácora | ✅ | ❌ | ❌ |

**Leyenda**: C=Crear, R=Ver, U=Editar, D=Eliminar

## ⚠️ **Notas Importantes**

- Los operadores **NO pueden eliminar** sus propios registros
- Los supervisores **NO pueden crear usuarios** 
- Solo administradores pueden **eliminar** registros
- Todos los accesos se **registran en bitácora**
- El sistema **mantiene compatibilidad** con funcionalidad existente