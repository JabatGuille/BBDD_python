class Ventas:

    def __init__(self, id, descripcion, estado):
        self.id = id
        self.descripcion = descripcion
        self.estado = estado
        self.vendedores = {}

    def ayadir_comprador(self, vendedor):
        self.vendedores[vendedor.empresa] = vendedor
