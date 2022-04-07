class Usuario:

    def __init__(self, usuario, clave, permisos, departamento):
        self.usuario = usuario
        self.clave = clave
        self.permisos = permisos
        self.departamento = departamento

    def cambiar_departamento(self, departamento):
        self.departamento = departamento
