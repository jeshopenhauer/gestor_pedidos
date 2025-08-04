# 🚚 Configuración API Real de DHL - Guía Completa

## 📋 **Resumen**
Tu sistema ya está preparado para usar la API real de DHL. Solo necesitas obtener tu API Key y reemplazarla en el código.

---

## 🔑 **Paso 1: Registro en DHL Developer Portal**

### 1.1 Crear cuenta
1. Ve a: **https://developer.dhl.com/**
2. Clic en "**Sign Up**" (esquina superior derecha)
3. Completa el formulario:
   - **Email**: Tu email corporativo
   - **Company**: Nombre de tu empresa
   - **Country**: España
   - **Use Case**: "Package tracking for internal logistics"

### 1.2 Verificar email
- Revisa tu correo y confirma la cuenta
- Inicia sesión en el portal

### 1.3 Crear aplicación
1. Ve a "**My Apps**" en el dashboard
2. Clic en "**Create New App**"
3. Selecciona "**Tracking API**"
4. Completa:
   - **App Name**: "Gestor Pedidos Tracking"
   - **Description**: "Sistema interno de seguimiento de paquetes"
   - **Expected Volume**: "< 1000 requests/month"

### 1.4 Obtener API Key
- Una vez creada la app, copia tu **API Key**
- Formato típico: `dhl_sandbox_abc123def456ghi789`

---

## 🔧 **Paso 2: Configurar tu API Key**

### 2.1 Reemplazar en el código
En el archivo `index.html`, busca esta línea (línea ~2752):

```javascript
const API_KEY = 'TU_API_KEY_AQUI'; // ⚠️ REEMPLAZA CON TU API KEY REAL
```

Cámbiala por:
```javascript
const API_KEY = 'tu_api_key_real_aqui'; // ✅ Tu API Key de DHL
```

### 2.2 Ejemplo completo
```javascript
// ANTES (modo demo)
const API_KEY = 'TU_API_KEY_AQUI';

// DESPUÉS (API real)
const API_KEY = 'dhl_sandbox_abc123def456ghi789';
```

---

## 🧪 **Paso 3: Pruebas**

### 3.1 Ambiente Sandbox (recomendado primero)
- La API Key inicial será para **sandbox**
- Usa números de tracking de prueba de DHL
- Ejemplos de tracking sandbox: `1234567890`, `JJD0001234567890`

### 3.2 Ambiente Producción
- Para datos reales, solicita acceso a producción en el portal
- Cambia la URL base si es necesario:
```javascript
const API_URL = 'https://api.dhl.com/track/shipments'; // Producción
```

---

## 📊 **Límites de la API**

### Plan Gratuito
- ✅ **250 consultas/día**
- ✅ **1 consulta/segundo**
- ✅ Datos en tiempo real
- ✅ Historial completo de eventos

### Plan Premium (si necesitas más)
- 🚀 **10,000+ consultas/día**
- 🚀 **10 consultas/segundo**
- 💰 Costo por consulta adicional

---

## 🔍 **Verificar que funciona**

### Indicadores de éxito:
1. **En consola del navegador** (F12):
   ```
   🟢 Consultando API real de DHL...
   📦 Procesando datos reales de DHL API
   ```

2. **Sin estos mensajes**:
   ```
   🔶 Usando modo demostración - Configura tu API Key para usar datos reales
   ```

3. **Datos reales**: Los resultados mostrarán información actual de DHL

---

## ⚠️ **Troubleshooting**

### Error 401 - API Key inválida
```
✅ Solución: Verifica que copiaste bien tu API Key
✅ Revisa que no tenga espacios extra
✅ Confirma que la app esté activa en el portal
```

### Error 404 - Tracking no encontrado
```
✅ Normal: El número no existe en DHL
✅ Verifica el formato del tracking
✅ Usa números reales de DHL
```

### Error 429 - Límite excedido
```
✅ Espera un minuto antes de la siguiente consulta
✅ Considera actualizar a plan premium
✅ Optimiza las consultas en tu aplicación
```

---

## 🔐 **Seguridad**

### ⚠️ **IMPORTANTE**
- **NO subas tu API Key a repositorios públicos**
- **NO la compartas en screenshots**
- **Considera usar variables de entorno en producción**

### Alternativa segura:
```javascript
// Para producción, considera:
const API_KEY = process.env.DHL_API_KEY || 'TU_API_KEY_AQUI';
```

---

## 🎯 **Ventajas de la API Real**

### vs Datos Simulados:
- ✅ **Información real y actualizada**
- ✅ **Estados precisos de paquetes**
- ✅ **Fechas exactas de entrega**
- ✅ **Ubicaciones reales**
- ✅ **Historial completo de eventos**
- ✅ **Integración directa con sistema DHL**

---

## 📞 **Soporte**

### Si tienes problemas:
1. **Portal DHL**: https://developer.dhl.com/support
2. **Documentación**: https://developer.dhl.com/api-reference
3. **Email DHL**: developer.support@dhl.com
4. **Foros**: Sección community del portal

---

## ✅ **Checklist Final**

- [ ] Cuenta creada en DHL Developer Portal
- [ ] App de tracking creada
- [ ] API Key copiada
- [ ] API Key reemplazada en `index.html`
- [ ] Prueba realizada con tracking real
- [ ] Consola muestra "🟢 Consultando API real de DHL..."
- [ ] Datos reales mostrados en la interfaz

---

**🎉 ¡Listo! Tu sistema ahora usa la API real de DHL para seguimiento en tiempo real.**
