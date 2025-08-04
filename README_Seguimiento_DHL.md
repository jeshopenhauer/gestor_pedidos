# 🚚 Seguimiento DHL - Guía de Uso

## 📋 Funcionalidades Implementadas

### ✅ **Botón Principal en Header**
- **Ubicación**: Header principal de la aplicación
- **Texto**: "🚚 Seguimiento DHL" (color naranja DHL)
- **Función**: Abre el modal de seguimiento para consultar cualquier número de tracking

### ✅ **Botones en Pedidos con Tracking**
- **Ubicación**: En pedidos que tienen número de tracking asignado
- **Texto**: "🚚 Seguir en DHL" (botones pequeños)
- **Función**: Abre directamente el seguimiento para ese pedido específico

### ✅ **Modal de Seguimiento Completo**
- **Entrada manual**: Campo para ingresar cualquier número de tracking
- **Vista embebida**: Iframe que muestra la página oficial de DHL España
- **Enlace directo**: Opción de abrir en nueva pestaña si el iframe falla

## 🎯 **Cómo Usar la Funcionalidad**

### **Método 1: Desde el Header**
1. Hacer clic en "🚚 Seguimiento DHL" en el header
2. Ingresar el número de tracking en el campo
3. Hacer clic en "🔍 Consultar" o presionar Enter
4. Ver el seguimiento en la ventana embebida

### **Método 2: Desde un Pedido**
1. Expandir los detalles de un pedido que tenga tracking
2. Hacer clic en "🚚 Seguir en DHL"
3. El modal se abrirá automáticamente con el número de tracking del pedido

### **Método 3: Vista Detalle Completo**
1. Abrir la vista de detalle completo de un pedido (botón 👁️)
2. En la sección "Etiquetas Enviadas", hacer clic en "🚚 Seguir en DHL"

## 🔧 **Características Técnicas**

### **URL Base Utilizada**
```
https://www.dhl.com/es-es/home/tracking.html?tracking-id=[NUMERO]
```

### **Validaciones Implementadas**
- ✅ Verificación de campo no vacío
- ✅ Validación de longitud mínima (4 caracteres)
- ✅ Manejo de errores de carga del iframe
- ✅ Opción alternativa con enlace directo

### **Funcionalidades de UX**
- ✅ Auto-focus en el campo de tracking al abrir el modal
- ✅ Soporte para tecla Enter en el campo de entrada
- ✅ Indicador visual del número que se está consultando
- ✅ Instrucciones y consejos para el usuario
- ✅ Limpieza automática del iframe al cerrar el modal

## 🎨 **Elementos Visuales**

### **Colores**
- **Botón principal**: Naranja DHL (#ff6b00)
- **Botones secundarios**: Naranja DHL (#ff6b00)
- **Header del iframe**: Naranja DHL con iconos 🚚 📦

### **Iconografía**
- 🚚 **Camión**: Representa el seguimiento y transporte
- 📦 **Paquete**: Representa el producto a rastrear
- 🔍 **Lupa**: Representa la búsqueda/consulta
- 💡 **Bombilla**: Para consejos e instrucciones

## 📱 **Compatibilidad**

### **Navegadores Soportados**
- ✅ Chrome/Edge/Safari (iframe funciona perfectamente)
- ✅ Firefox (iframe puede tener restricciones, enlace directo disponible)
- ✅ Móviles (responsive design)

### **Limitaciones Conocidas**
- 🔶 Algunos navegadores pueden bloquear iframes de sitios externos
- 🔶 DHL puede implementar medidas anti-iframe en el futuro
- ✅ **Solución implementada**: Enlace directo como alternativa

## 💡 **Consejos de Uso**

### **Formatos de Tracking Válidos**
- **Números estándar**: 1234567890 (10-11 dígitos)
- **Con prefijo**: JD001234567890 (letras + números)  
- **Múltiples paquetes**: Separar con comas (si DHL lo soporta)

### **Solución de Problemas**
1. **Si no se carga el iframe**: Usar "Abrir en nueva pestaña"
2. **Si el tracking no existe**: Verificar el número en el sitio oficial
3. **Si hay errores de conexión**: Verificar la conexión a internet

## 🚀 **Mejoras Futuras Sugeridas**

- [ ] **Historial de trackings**: Guardar números consultados recientemente
- [ ] **Notificaciones**: Alertas automáticas de cambios de estado
- [ ] **Múltiples transportistas**: UPS, FedEx, Correos, etc.
- [ ] **API integrada**: Consultas directas sin iframe (requiere API key)
- [ ] **Exportar información**: PDF con estado del seguimiento

---

## ✅ **Estado del Sistema**

🟢 **FUNCIONAL** - Sistema completamente operativo y listo para usar

El seguimiento DHL está perfectamente integrado en el gestor de pedidos y proporciona una experiencia fluida para consultar el estado de los envíos directamente desde la aplicación.

---

*Última actualización: 4 de agosto de 2025*
