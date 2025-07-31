
def simple_input(prompt, parent=None):
    if parent:
        # Usar la ventana padre si se proporciona
        root = parent
    else:
        # Crear ventana temporal si no hay padre
        root = tk.Tk()
        root.withdraw()
    
    result = simpledialog.askstring("Input", prompt, parent=root)
    
    if not parent:
        root.destroy()
    
    return result


if __name__ == "__main__":
    manager = PedidoManager()
    app = PedidoApp(manager)
    app.mainloop()
