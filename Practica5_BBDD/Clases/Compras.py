class Compras:

    def __init__(self, id, descripcion, estado):
        self.id = id
        self.descripcion = descripcion
        self.estado = estado
        self.proveedores = {}

    def ayadir_comprador(self, proveedor):
        self.proveedores[proveedor.empresa] = proveedor
