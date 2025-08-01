#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo: Creación de un pedido de SESO.SL y manejo de estados
Este script demuestra cómo funciona el sistema de estados del pedido
"""

from main import Eproc, PedidoStatus, ReferenciaPieza
from datetime import datetime

def mostrar_estado_pedido(pedido):
    """Muestra el estado actual del pedido con detalles"""
    print(f"\n{'='*60}")
    print(f"📦 PEDIDO: {pedido.numero_oferta}")
    print(f"🏢 PROVEEDOR: {pedido.proveedor}")
    print(f"📊 ESTADO ACTUAL: {pedido.status}")
    print(f"📈 PROGRESO: {pedido.get_porcentaje_progreso()}% ({pedido.get_posicion_estado()}/{pedido.get_total_estados()})")
    print(f"🕒 CREADO: {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
    
    # Mostrar barra de progreso visual
    total_estados = pedido.get_total_estados()
    posicion_actual = pedido.get_posicion_estado()
    
    print(f"\n📊 BARRA DE PROGRESO:")
    barra = ""
    for i in range(1, total_estados + 1):
        if i <= posicion_actual:
            barra += "●"  # Completado
        else:
            barra += "○"  # Pendiente
    print(f"   {barra} ({posicion_actual}/{total_estados})")
    
    # Mostrar historial de cambios
    if len(pedido.historial) > 1:
        print(f"\n📋 HISTORIAL DE CAMBIOS:")
        for entrada in pedido.historial[-3:]:  # Últimos 3 cambios
            fecha_str = entrada['fecha'].strftime('%d/%m/%Y %H:%M')
            print(f"   • {fecha_str}: {entrada['estado']}")
            if entrada.get('comentario'):
                print(f"     └─ {entrada['comentario']}")

def demo_crear_pedido_seso():
    """Demuestra la creación de un pedido de SESO.SL"""
    print("🚀 DEMO: Creando nuevo pedido de SESO.SL")
    print("="*60)
    
    # Crear referencias de ejemplo
    referencias = [
        ReferenciaPieza("REF001", "Tornillo M8x50", 10, "Proyecto Alpha"),
        ReferenciaPieza("REF002", "Arandela Ø8", 10, "Proyecto Alpha"),
        ReferenciaPieza("REF003", "Tuerca M8", 10, "Proyecto Alpha")
    ]
    
    # Crear pedido de SESO.SL (empieza automáticamente en RECEPCION_OFERTA)
    pedido = Eproc(
        numero_oferta="OF-2025-001",
        proveedor="SESO.SL",
        referencias=referencias
    )
    
    print(f"✅ Pedido creado para {pedido.proveedor}")
    mostrar_estado_pedido(pedido)
    
    return pedido

def demo_avanzar_estados(pedido):
    """Demuestra cómo avanzar por los estados"""
    print(f"\n🔄 DEMO: Avanzando estados del pedido")
    
    input("\n⏸️  Presiona ENTER para avanzar al siguiente estado...")
    
    # 1. Avanzar a PEDIDO_TRAMITACION_EPROC_BORRADOR
    print(f"\n1️⃣ Avanzando a estado de borrador...")
    pedido.avanzar_estado("Iniciando tramitación en ePROC")
    mostrar_estado_pedido(pedido)
    
    input("\n⏸️  Presiona ENTER para continuar...")
    
    # 2. Intentar avanzar sin requisition_id (debería fallar)
    print(f"\n2️⃣ Intentando avanzar sin requisition_id...")
    if not pedido.puede_avanzar_estado():
        print("❌ No se puede avanzar. Campos requeridos:", pedido.get_campos_requeridos())
        print("📝 Agregando requisition_id y OI...")
        pedido.requisition_id = "REQ-2025-001"
        pedido.oi = 12345
        print("✅ Campos completados")
    
    # 3. Ahora sí avanzar
    print(f"\n3️⃣ Avanzando a pedido enviado (no firmado)...")
    pedido.avanzar_estado("Pedido enviado a plataforma ePROC")
    mostrar_estado_pedido(pedido)
    
    input("\n⏸️  Presiona ENTER para continuar...")
    
    # 4. Avanzar a firmado
    print(f"\n4️⃣ Avanzando a pedido firmado...")
    pedido.avanzar_estado("Pedido firmado por el proveedor")
    mostrar_estado_pedido(pedido)
    
    input("\n⏸️  Presiona ENTER para continuar...")
    
    # 5. Simular retroceso
    print(f"\n⬅️  DEMO: Retrocediendo un estado...")
    pedido.retroceder_estado("Corrección necesaria en el pedido")
    mostrar_estado_pedido(pedido)
    
    return pedido

def demo_estados_completo():
    """Demo completo del sistema de estados"""
    print("🎯 DEMO COMPLETO: Sistema de Estados de Pedidos")
    print("="*80)
    
    # Mostrar todos los estados disponibles
    print("\n📋 ESTADOS DISPONIBLES:")
    estados = PedidoStatus.estados_ordenados()
    for i, estado in enumerate(estados, 1):
        print(f"   {i:2d}. {estado}")
    
    # Crear pedido
    pedido = demo_crear_pedido_seso()
    
    # Avanzar estados
    demo_avanzar_estados(pedido)
    
    print(f"\n🎉 DEMO COMPLETADO")
    print(f"El pedido {pedido.numero_oferta} está en estado: {pedido.status}")
    print(f"Progreso: {pedido.get_porcentaje_progreso()}%")
    
    return pedido

if __name__ == "__main__":
    try:
        pedido = demo_estados_completo()
        
        print(f"\n💾 ¿Quieres guardar este pedido de prueba? (s/n): ", end="")
        respuesta = input().lower().strip()
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            print("📁 Para guardar, ejecuta la aplicación principal: python iniciar_gestor.py")
        else:
            print("📝 Demo finalizado sin guardar")
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
