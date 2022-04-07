class MateriaPrima:

    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.objetos = {}

    def ayadir_objeto(self, objeto):
        self.objetos[objeto.id] = objeto
