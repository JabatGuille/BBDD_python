class Usuario:

    def __init__(self, usuario, permisos, departamento):
        self.usuario = usuario
        self.permisos = permisos
        self.departamento = departamento

    def cambiar_departamento(self, departamento):
        self.departamento = departamento
