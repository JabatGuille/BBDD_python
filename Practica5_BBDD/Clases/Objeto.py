class Objeto:

    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.materiales = {}

    def ayadir_materia_prima(self, materia_prima):
        self.materiales[materia_prima.id] = materia_prima
