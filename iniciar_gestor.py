#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lanzador del Gestor de Pedidos
Este script asegura que la aplicación se ejecute desde el directorio correcto
y maneje correctamente la carga de datos guardados.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        # Cambiar al directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"Directorio de trabajo: {os.getcwd()}")
        
        # Verificar que los archivos necesarios existen
        required_files = ['gestor_pedidos_gui.py', 'main.py']
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Archivos faltantes: {', '.join(missing_files)}")
            root.destroy()
            return
        
        # Verificar si existe el archivo de datos
        data_file = 'pedidos_data.json'
        if os.path.exists(data_file):
            print(f"Archivo de datos encontrado: {data_file}")
        else:
            print("No se encontró archivo de datos. Se creará uno nuevo.")
        
        # Importar e iniciar la aplicación
        from gestor_pedidos_gui import PedidoManager, PedidoApp
        
        print("Iniciando Gestor de Pedidos...")
        manager = PedidoManager()
        
        # Mostrar información de los datos cargados
        num_pedidos = len(manager.pedidos)
        print(f"Datos cargados: {num_pedidos} pedido(s)")
        
        app = PedidoApp(manager)
        
        # Configurar el cierre de la aplicación
        def on_closing():
            try:
                print("Guardando datos antes de cerrar...")
                manager.guardar_datos()
                print("Datos guardados correctamente")
            except Exception as e:
                print(f"Error al guardar: {e}")
            finally:
                app.destroy()
        
        app.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Centrar la ventana en la pantalla
        app.update_idletasks()
        width = app.winfo_width()
        height = app.winfo_height()
        x = (app.winfo_screenwidth() // 2) - (width // 2)
        y = (app.winfo_screenheight() // 2) - (height // 2)
        app.geometry(f"{width}x{height}+{x}+{y}")
        
        print("Aplicación iniciada correctamente")
        app.mainloop()
        
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de Importación", 
                           f"Error al importar módulos:\n{str(e)}\n\n"
                           f"Asegúrate de que todos los archivos estén en la carpeta correcta.")
        root.destroy()
        
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
        root.destroy()
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
