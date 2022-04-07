import csv
import hashlib
import os
import random
import pymysql
from os import path
from os import remove

import matplotlib.pyplot as plt

from Clases.Compras import Compras
from Clases.Empresa import Empresa
from Clases.MateriaPrima import MateriaPrima
from Clases.Objeto import Objeto
from Clases.Produccion import Produccion
from Clases.Usuario import Usuario
from Clases.Ventas import Ventas
from Enum.Departamentos import Departamentos
from Enum.Estado import Estado
from Enum.Permisos import Permisos

usuario_logueado = Usuario("", "", "", "")
usuarios = {}
produccion = {}
empresas = {}
materia_prima = {}
objetos = {}
compras = {}
ventas = {}


# Enum_departamentos funciona para poder elegir el departamento del usuario y devuelve el departamento
def enum_departamento():
    global departamento
    bol_submenu = True
    while bol_submenu:
        departamento = input("Indica el departamento del empleado (Compras,Ventas,Produccion,RRHH): ").lower()
        if str.capitalize(departamento) == Departamentos.COMPRAS.value:
            bol_submenu = False
        elif str.capitalize(departamento) == Departamentos.VENTAS.value:
            bol_submenu = False
        elif str.capitalize(departamento) == Departamentos.PRODUCCION.value:
            bol_submenu = False
        elif str.upper(departamento) == Departamentos.RRHH.value:
            bol_submenu = False
        else:
            print("El departamento elegido no esta en la lista")
    return departamento.capitalize()


# Cancelar sirve para poder cancelar en cualquier momento devuelve un booleano
def cancelar():
    cancelar = input("Si desea cancelar la operacion escriba Cancelar: ").lower()
    if cancelar == "cancelar":
        return True
    else:
        return False


# Enum_permisos funciona para poder elegir los permisos del usuario y devuelve el permiso
def enum_permisos():
    global permisos
    bol_submenu = True
    while bol_submenu:
        permisos = input("Indica los permisos (Empleado,Jefe,Admin): ").lower()
        if str.capitalize(permisos) == Permisos.EMPLEADO.value:
            bol_submenu = False
        elif str.capitalize(permisos) == Permisos.JEFE.value:
            bol_submenu = False
        elif str.capitalize(permisos) == Permisos.ADMIN.value:
            bol_submenu = False
        else:
            print("El permiso elegido no esta en la lista")
    return permisos.capitalize()


# Enum_estado funciona para poder elegir el estado de la orden y devuelve el estado
def enum_estado(objeto):
    global estado
    bol_submenu = True
    while bol_submenu:
        if objeto == "compra":
            estado = input("Indica el estado (Comprado, En espera, Cancelada): ").lower().capitalize()
            if estado == Estado.COMPRADO.value:
                bol_submenu = False
        else:
            estado = input("Indica el estado (Vendido, En espera, Cancelada): ").lower().capitalize()
            if estado == Estado.VENDIDO.value:
                bol_submenu = False
        if estado != "Comprado":
            if estado != "Vendido":
                if estado == Estado.ESPERA.value:
                    bol_submenu = False
                elif estado == Estado.CANCELADA.value:
                    bol_submenu = False
                else:
                    print("El estado elegido no esta en la lista")
    return estado


# Login es el sistema para poder loggear el usuario
def login():
    global usuario_logueado
    bol_menu = True
    while bol_menu:
        usuario = input("Indique el usuario: ")
        clave = input("Indique la clave del usuario: ")
        if usuarios.keys().__contains__(usuario):
            if usuarios[usuario].clave == clave:
                print("Accediendo al programa")
                usuario_logueado = usuarios[usuario]
                bol_menu = False
            else:
                print("Contraseña incorrecta")
        else:
            print("El usuario no existe")


# Generar_contraseya sirve para poder generar una contraseña segura y aleatoria
def generar_contraseya():
    numeros = list("0123456789")
    mayusculas = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    minusculas = list("abcdefghijklmnopqrstuvwxyz")

    password = ''
    alfabeto = []
    alfabeto = alfabeto + numeros
    alfabeto = alfabeto + mayusculas
    alfabeto = alfabeto + minusculas

    while len(password) < 6:
        i = random.randint(0, len(alfabeto) - 1)
        letra = str(alfabeto[i])
        password = password + letra
    return password


# Registro es el sistema para poder registrar los usuarios
def registro():
    if usuario_logueado.usuario == "":
        print("No hay usuario logueado, redirigiendo al apartado de logueo")
        login()
    if usuario_logueado.permisos == Permisos.JEFE.value or usuario_logueado.permisos == Permisos.ADMIN.value or usuario_logueado.departamento == Departamentos.RRHH.value:
        global usuario, clave, permisos, departamento
        bol_menu = True
        while bol_menu:
            bol_submenu = True
            while bol_submenu:
                usuario = input("Escriba el nombre de usuario: ")
                if usuarios.keys().__contains__(usuario):
                    print("El usuario ya exite")
                else:
                    bol_submenu = False
            clave = generar_contraseya()
            permisos = enum_permisos()
            departamento = enum_departamento()
            if cancelar():
                print("Cancelando operacion y redirigiendo al menu.")
            else:
                print("Creando usuario")
                print("La clave del usuario es: " + clave)
                usuarios[usuario] = Usuario(usuario, clave, permisos, departamento)
                confirmacion = input(
                    "Si quiere seguir creando usuarios escriba S: ")
                if confirmacion.upper() != "S":
                    bol_menu = False


# Lector_ficheros sirve para poder leer los ficheros.csv y cargar los datos en memoria
def lector_ficheros(rutas_unitarias, rutas_parecidas):
    rutas_relacionadas = ["./Ficheros/Relaciones/compras_empresas.csv", "./Ficheros/Relaciones/ventas_empresas.csv",
                          "./Ficheros/Relaciones/objetos_materiaprima.csv"]
    with open(rutas_unitarias[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            usuarios[row['usuario']] = Usuario(row['usuario'], row['clave'], row['permisos'], row['departamento'])
    with open(rutas_unitarias[2]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            empresas[row['empresa']] = Empresa(row['empresa'])
    with open(rutas_parecidas[0]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            materia_prima[int(row['id'])] = MateriaPrima(int(row['id']), row['nombre'], row['descripcion'])
    with open(rutas_parecidas[1]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            objetos[int(row['id'])] = Objeto(int(row['id']), row['nombre'], row['descripcion'])
    with open(rutas_parecidas[2]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            compras[int(row['id'])] = Compras(int(row['id']), row['descripcion'], row['estado'])
    with open(rutas_parecidas[3]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ventas[int(row['id'])] = Ventas(int(row['id']), row['descripcion'], row['estado'])
    with open(rutas_unitarias[1]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            produccion[int(row['id'])] = Produccion(int(row['id']), row['descripcion'], row['cantidad'],
                                                    objetos[int(row['objeto'])])
    try:
        with open(rutas_relacionadas[0], 'r') as f:
            if os.stat(rutas_relacionadas[0]).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    except IOError as e:
        bol_fichero = True
    if bol_fichero:
        archivo = open(rutas_relacionadas[0], 'w')
        archivo.close()
        with open(rutas_relacionadas[0], 'r+') as csvfile:
            fieldnames = ['compras_id', 'empresa']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    else:
        with open(rutas_relacionadas[0]) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                compras[int(row['compra_id'])].ayadir_comprador(empresas[row['empresa']])
                empresas[row['empresa']].ayadir_compras(compras[int(row['compra_id'])])
    try:
        with open(rutas_relacionadas[1], 'r') as f:
            if os.stat(rutas_relacionadas[1]).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    except IOError as e:
        bol_fichero = True
    if bol_fichero:
        archivo = open(rutas_relacionadas[1], 'w')
        archivo.close()
        with open(rutas_relacionadas[1], 'r+') as csvfile:
            fieldnames = ['ventas_id', 'empresa']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    else:
        with open(rutas_relacionadas[1]) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ventas[int(row['ventas_id'])].ayadir_comprador(empresas[row['empresa']])
                empresas[row['empresa']].ayadir_ventas(ventas[int(row['ventas_id'])])
    try:
        with open(rutas_relacionadas[2], 'r') as f:
            if os.stat(rutas_relacionadas[2]).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    except IOError as e:
        bol_fichero = True
    if bol_fichero:
        archivo = open(rutas_relacionadas[2], 'w')
        archivo.close()
        with open(rutas_relacionadas[2], 'r+') as csvfile:
            fieldnames = ['objetos_id', 'materiaprima_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    else:
        with open(rutas_relacionadas[2]) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                objetos[int(row['objetos_id'])].ayadir_materia_prima(materia_prima[int(row['materiaprima_id'])])
                materia_prima[int(row['materiaprima_id'])].ayadir_objeto(objetos[int(row['objetos_id'])])


# Comprobar_csv sirve para poder comprobar que existan los ficheros necesarios o si no crearlos
def comprobar_csv():
    if not os.path.exists('Ficheros/Relaciones'):
        os.mkdir('Ficheros')
        os.mkdir('Ficheros/Relaciones')
    if not os.path.exists('Graficos'):
        os.mkdir('Graficos')
    rutas_unitarias = ["./Ficheros/usuarios.csv", "./Ficheros/produccion.csv", "./Ficheros/empresas.csv"]
    rutas_parecidas = ["./Ficheros/materia_prima.csv", "./Ficheros/objetos.csv", "./Ficheros/compras.csv",
                       "./Ficheros/ventas.csv"]
    try:
        with open(rutas_unitarias[0], 'r') as f:
            if os.stat(rutas_unitarias[0]).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    except IOError as e:
        bol_fichero = True
    if bol_fichero:
        archivo = open(rutas_unitarias[0], 'w')
        archivo.close()
        with open(rutas_unitarias[0], 'r+') as csvfile:
            fieldnames = ['usuario', 'clave', 'permisos', 'departamento']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(
                {'usuario': 'Admin', 'clave': hashlib.sha224('Admin'.encode('utf-8')).hexdigest(), 'permisos': 'Admin',
                 'departamento': 'Jefe'})
            writer.writerow({'usuario': 'Jefe', 'clave': 'Jefe', 'permisos': 'Jefe', 'departamento': 'Jefe'})
            writer.writerow(
                {'usuario': 'Compras', 'clave': 'Compras', 'permisos': 'Empleado', 'departamento': 'Compras'})
            writer.writerow({'usuario': 'Ventas', 'clave': 'Ventas', 'permisos': 'Empleado', 'departamento': 'Ventas'})
            writer.writerow(
                {'usuario': 'Produccion', 'clave': 'Produccion', 'permisos': 'Empleado', 'departamento': 'Produccion'})
            writer.writerow({'usuario': 'RRHH', 'clave': 'RRHH', 'permisos': 'Empleado', 'departamento': 'RRHH'})

    try:
        with open(rutas_unitarias[1], 'r') as f:
            if os.stat(rutas_unitarias[1]).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    except IOError as e:
        bol_fichero = True
    if bol_fichero:
        archivo = open(rutas_unitarias[1], 'w')
        archivo.close()
        with open(rutas_unitarias[1], 'r+') as csvfile:
            fieldnames = ['id', 'descripcion', 'cantidad', 'objeto']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    try:
        with open(rutas_unitarias[2], 'r') as f:
            if os.stat(rutas_unitarias[2]).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    except IOError as e:
        bol_fichero = True
    if bol_fichero:
        archivo = open(rutas_unitarias[2], 'w')
        archivo.close()
        with open(rutas_unitarias[2], 'r+') as csvfile:
            fieldnames = ['empresa']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    for i in range(4):
        try:
            with open(rutas_parecidas[i], 'r') as f:
                if os.stat(rutas_parecidas[i]).st_size == 0:
                    bol_fichero = True
                else:
                    bol_fichero = False
        except FileNotFoundError as e:
            bol_fichero = True
        except IOError as e:
            bol_fichero = True
        if bol_fichero:
            archivo = open(rutas_parecidas[i], 'w')
            archivo.close()
        if i < 2:
            with open(rutas_parecidas[i], 'r+') as csvfile:
                fieldnames = ['id', 'nombre', 'descripcion']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        else:
            with open(rutas_parecidas[i], 'r+') as csvfile:
                fieldnames = ['id', 'descripcion', 'estado']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
    lector_ficheros(rutas_unitarias, rutas_parecidas)


# Guardar_usuarios sirve para poder guardar los usuarios en el csv
def guardar_usuarios():
    with open("./Ficheros/usuarios.csv", 'r+') as csvfile:
        fieldnames = ['usuario', 'clave', 'permisos', 'departamento']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for usuario in usuarios.values():
            writer.writerow({'usuario': usuario.usuario, 'clave': usuario.clave, 'permisos': usuario.permisos,
                             'departamento': usuario.departamento})


# Guardar_empresas sirve para poder guardar las empresas en el csv
def guardar_empresas():
    with open("./Ficheros/empresas.csv", 'r+') as csvfile:
        fieldnames = ['empresa']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for empresa in empresas.values():
            writer.writerow({'empresa': empresa.empresa})


# Guardar_compras sirve para poder guardar las compras en el csv
def guardar_compras():
    with open("./Ficheros/compras.csv", 'r+') as csvfile:
        fieldnames = ['id', 'descripcion', 'estado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for compra in compras.values():
            writer.writerow({'id': compra.id, 'descripcion': compra.descripcion, 'estado': compra.estado})
    with open("./Ficheros/Relaciones/compras_empresas.csv", 'r+') as csvfile:
        fieldnames = ['compra_id', 'empresa']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for compra in compras.values():
            for empresa in compra.proveedores.values():
                writer.writerow({'compra_id': compra.id, 'empresa': empresa.empresa})


# Guardar_ventas sirve para poder guardar las ventas en el csv
def guardar_ventas():
    with open("./Ficheros/ventas.csv", 'r+') as csvfile:
        fieldnames = ['id', 'descripcion', 'estado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for venta in ventas.values():
            writer.writerow({'id': venta.id, 'descripcion': venta.descripcion, 'estado': venta.estado})
    with open("./Ficheros/Relaciones/ventas_empresas.csv", 'r+') as csvfile:
        fieldnames = ['ventas_id', 'empresa']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for venta in ventas.values():
            for empresa in venta.vendedores.values():
                writer.writerow({'ventas_id': venta.id, 'empresa': empresa.empresa})


# Guardar_produccion sirve para poder guardar la produccion en el csv
def guardar_produccion():
    if path.exists("./Ficheros/produccion.csv"):
        remove("./Ficheros/produccion.csv")
        archivo = open("./Ficheros/produccion.csv", 'w')
        archivo.close()
    with open("./Ficheros/produccion.csv", 'r+') as csvfile:
        fieldnames = ['id', 'descripcion', 'cantidad', 'objeto']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for producto in produccion.values():
            writer.writerow({'id': producto.id, 'descripcion': producto.descripcion,
                             'cantidad': producto.cantidad, 'objeto': producto.objeto.id})


# Guardar_objetos_materia_prima sirve para poder guardar los objetos y la materia prima en el csv
def guardar_objetos_materia_prima():
    fieldnames = ['id', 'nombre', 'descripcion']
    with open("./Ficheros/objetos.csv", 'r+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for objeto in objetos.values():
            writer.writerow({'id': objeto.id, 'nombre': objeto.nombre, 'descripcion': objeto.descripcion})
    with open("./Ficheros/materia_prima.csv", 'r+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for materia in materia_prima.values():
            writer.writerow({'id': materia.id, 'nombre': materia.nombre, 'descripcion': materia.descripcion})
    with open("./Ficheros/Relaciones/objetos_materiaprima.csv", 'r+') as csvfile:
        fieldnames = ['objetos_id', 'materiaprima_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for objeto in objetos.values():
            for materia in objeto.materiales.values():
                writer.writerow({'objetos_id': objeto.id, 'materiaprima_id': materia.id})


# Guardar_csv sirve para acceder a todos los guardados de csv
def guardar_csv():
    guardar_usuarios()
    guardar_compras()
    guardar_ventas()
    guardar_empresas()
    guardar_produccion()
    guardar_objetos_materia_prima()


# Menu_login es el menu donde puedes acceder al login, registrar un usuario temporal o terminar la aplicacion
def menu_login():
    guardar_csv()
    global menu, departamento, usuario_logueado
    usuario_logueado = Usuario("", "", "", "")
    bol_menu_login = True
    while bol_menu_login:
        print(
            "\nMENU PRINCIPAL\n-1 Login.\n-2 Registrar usuario temporal.\n-3 Salir.\n En el informe del programa "
            "estan los usuarios creados por defecto")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 3:
                print("Esa opcion no esta en el menu.")
        except ValueError:
            print("No ha elegido un numero.")
        if menu == 1:
            login()
            if usuario_logueado.permisos == "Admin" or usuario_logueado.permisos == "Jefe":
                menu_completo()
            elif usuario_logueado.permisos == "Empleado":
                if usuario_logueado.departamento == "Compras":
                    menu_compras()
                elif usuario_logueado.departamento == "Ventas":
                    menu_ventas()
                elif usuario_logueado.departamento == "Produccion":
                    menu_produccion()
                elif usuario_logueado.departamento == "RRHH":
                    menu_RRHH()
        elif menu == 2:
            departamento = enum_departamento()
            usuario_logueado = Usuario('temporal', 'temporal', 'Lectura', departamento)
            menu_lecturas()
        elif menu == 3:
            print("Guardando los datos, espere un momento.")
            guardar_csv()
            print("Saliendo del programa.")
            bol_menu_login = False


# Crear_empresa sirve para poder añadir empresas
def crear_empresa():
    bol_menu = True
    while bol_menu:
        empresa = input("Escriba el nombre de la empresa: ")
        if empresas.keys().__contains__(empresa):
            print("La empresa ya exite")
        else:
            empresas[empresa] = Empresa(empresa)
            bol_menu = False


# Crear_orden sirve para poder crear una orden de venta
def crear_orden(objeto):
    global Nempresa, bol, descripcion, empresa
    if len(empresas) == 0:
        print("No existen empresas debe añadir")
        crear_empresa()
    else:
        bol = True
        while bol:
            print("Empresas disponibles.")
            for empresa in empresas.values():
                print(empresa.empresa)
            Nempresa = input("Escriba el nombre de la empresa con la que quiere crear la orden de " + objeto + ": ")
            if empresas.keys().__contains__(Nempresa):
                bol = False
            else:
                print("La empresa elegida no esta en la lista.")
        bol = True
        while bol:
            descripcion = input("Escriba una descripción de la " + objeto + ": ")
            if descripcion != "":
                bol = False
            else:
                print("Debe escribir una descripción.")
        estado = enum_estado(objeto)
        if cancelar():
            print("Cancelando operacion y redirigiendo al menu.")
            bol = False
        else:
            if objeto == "venta":
                ventas[len(ventas)] = Ventas(len(ventas), descripcion, estado)
                ventas[len(ventas) - 1].ayadir_comprador(empresas[Nempresa])
                empresas[Nempresa].ayadir_ventas(ventas[len(ventas) - 1])
            else:
                compras[len(compras)] = Compras(len(compras), descripcion, estado)
                compras[len(compras) - 1].ayadir_comprador(empresas[Nempresa])
                empresas[Nempresa].ayadir_compras(compras[len(compras) - 1])
            opcion = input("Si quiere seguir creando ordendes de compra escriba S: ").upper()
            if opcion != "S":
                print("Saliendo al menu")


# Menu_compras es el menu al que acceden los empleados del departamento de compras
def menu_compras():
    global menu
    bol_menu_compras = True
    while bol_menu_compras:
        print(
            "\n-1 Crear orden de compra.\n-2 Editar orden de compra.\n-3 Anular orden de compra.\n-4 Crear "
            "vendedores.\n-5 Mostrar òrdenes de compra.\n-6 Crear Grafico.\n-7 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 7:
                print("Esa opcion no esta en el menu.")
        except ValueError:
            print("No ha elegido un numero.")
        if menu == 1:
            crear_orden("compra")
        elif menu == 2:
            editar_orden_compra()
        elif menu == 3:
            anular_orden_compra()
        elif menu == 4:
            crear_empresa()
        elif menu == 5:
            mostrar_ordenes_compra()
        elif menu == 6:
            crear_graficos("Compras")
        elif menu == 7:
            print("Moviendo al menu principal")
            guardar_empresas()
            guardar_compras()
            bol_menu_compras = False


# Editar_orden_compra sirve para editar las ordenes de compra
def editar_orden_compra():
    global compra_id, menu, Nempresa
    if len(compras) == 0:
        print("No hay ordenes de compra, redirigiendo a la creacion de ordendes")
        crear_orden("compra")
    else:
        bol = True
        while bol:
            cont = 0
            for compra in compras.values():
                if compra.estado != "Cancelada":
                    print("ID: " + str(compra.id))
                    print("Descripcion: " + compra.descripcion)
                    print("Estado: " + compra.estado)
                    print("Empresas en la compra.")
                    for empresa in compra.proveedores.values():
                        print("Nombre: " + empresa.empresa)
                else:
                    cont += 1
            if cont != len(compras):
                try:
                    compra_id = int(input("Escriba el id de la compra que quiere editar: "))
                except ValueError:
                    print("Debe escribir un numero")
                if compras.keys().__contains__(compra_id):
                    if compras[compra_id].estado == "Cancelada":
                        print("Ese id no es valido")
                    else:
                        bol = False
                else:
                    print("El id seleccionado no existe")
                print("¿Quiere cambiar la descripcion?")
                opcion = input("Escriba S: ").upper()
                if opcion == "S":
                    bol = True
                    while bol:
                        descripcion = input("Escriba la descripcion: ")
                        if descripcion != "":
                            compras[compra_id].descripcion = descripcion
                            bol = False
                        else:
                            print("La descripcion no puede estar vacia")
                print("¿Quiere cambiar el estado?")
                opcion = input("Escriba S: ").upper()
                if opcion == "S":
                    estado = enum_estado("compra")
                    compras[compra_id].estado = estado
                print("¿Quiere añadir o quitar compradores?")
                opcion = input("Escriba S: ").upper()
                if opcion == "S":
                    bol_submenu = True
                    while bol_submenu:
                        print("\n-1 Añadir comprador.\n-2 Quitar comprador.\n-3 Terminar de editar la orden de compra.")
                        try:
                            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
                            if menu < 1 or menu > 3:
                                print("Esa opcion no esta en el menu.")
                        except ValueError:
                            print("No ha elegido un numero.")
                        if menu == 1:
                            bol = True
                            while bol:
                                print("Empresas en la compra.")
                                for empresa in empresas.values():
                                    print("Nombre: " + empresa.empresa)
                                Nempresa = input("Escriba el nombre de la empresa, escriba Salir si quiere salir: ")
                                if empresas.keys().__contains__(Nempresa):
                                    if compras[compra_id].proveedores.keys().__contains__(Nempresa):
                                        print("La empresa ya se encuentra en la orden de compra")
                                    else:
                                        bol = False
                                elif Nempresa.lower().capitalize() == "Salir":
                                    print("Saliendo")
                                    bol = False
                                else:
                                    print("La empresa no se encuentra en la lista")
                            if Nempresa.lower().capitalize() != "Salir":
                                if cancelar():
                                    print("Cancelando operacion.")
                                else:
                                    compras[compra_id].ayadir_comprador(empresas[Nempresa])
                                    empresas[Nempresa].ayadir_compras(compras[compra_id])
                        if menu == 2:
                            bol = True
                            while bol:
                                print("Empresas en la compra.")
                                for empresa in compras[compra_id].proveedores.values():
                                    print("Nombre: " + empresa.empresa)
                                Nempresa = input("Escriba el nombre de la empresa, escriba Salir si quiere salir: ")
                                if empresas.keys().__contains__(Nempresa):
                                    if compras[compra_id].proveedores.keys().__contains__(Nempresa):
                                        bol = False
                                    else:
                                        print("La empresa no se encuentra en la orden de compra")
                                elif Nempresa.lower().capitalize() == "Salir":
                                    print("Saliendo")
                                    bol = False
                                else:
                                    print("La empresa no se encuentra en la lista")
                                if Nempresa.lower().capitalize() != "Salir":
                                    if cancelar():
                                        print("Cancelando operacion.")
                                    else:
                                        compras[compra_id].proveedores.pop(Nempresa)
                                        empresas[Nempresa].compras.pop(compra_id)
                        if menu == 3:
                            print("Saliendo.")
                            bol_submenu = False
            else:
                print("No hay ordenes de compra para editar.")
            print("Terminando operacion.")
            bol = False


# Anular_orden_compra sirve para anular las ordenes de compra
def anular_orden_compra():
    global compra_id
    bol = True
    while bol:
        cont = 0
        for compra in compras.values():
            if compra.estado != "Cancelada":
                print("ID: " + str(compra.id))
                print("Descripcion: " + compra.descripcion)
                print("Estado: " + compra.estado)
                print("Empresas en la compra.")
                for empresa in compra.proveedores.values():
                    print("Nombre: " + empresa.empresa)
            else:
                cont += 1
        if cont != len(compras):
            try:
                compra_id = int(input("Escriba el id de la compra que quiere anular: "))
            except ValueError:
                print("Debe escribir un numero")
            if compras.keys().__contains__(compra_id):
                if compras[compra_id].estado == "Cancelada":
                    print("Ese id no es valido")
                else:
                    bol = False
            else:
                print("El id seleccionado no existe")
            if cancelar():
                print("Cancelando operacion")
            else:
                compras[compra_id].estado = Estado.CANCELADA.value
        else:
            bol = False
            print("No hay ordendes de compra para poder anular")


# Mostrar_ordenes_compra sirve para mostrar las ordenes de compra
def mostrar_ordenes_compra():
    if len(compras) > 0:
        for compra in compras.values():
            print("Orden de compra.")
            print("ID: " + str(compra.id))
            print("Descripción: " + compra.descripcion)
            print("Estado: " + compra.estado)
            print("Empresas en la orden.")
            for empresa in compra.proveedores.values():
                print("Empresa: " + empresa.empresa)
    else:
        print("No hay ordenes de compra")


# Menu_ventas es el menu al que acceden los empleados con el departamento de ventas
def menu_ventas():
    global menu
    bol_menu_ventas = True
    while bol_menu_ventas:
        print(
            "\n-1 Crear orden de venta.\n-2 Editar orden de venta.\n-3 Anular orden de venta.\n-4 Crear "
            "compradores.\n-5 Mostrar òrdenes de venta.\n-6 Crear Grafico.\n-7 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 7:
                print("Esa opcion no esta en el menu.")
        except ValueError:
            print("No ha elegido un numero.")
        if menu == 1:
            crear_orden("venta")
        elif menu == 2:
            editar_orden_venta()
        elif menu == 3:
            anular_orden_venta()
        elif menu == 4:
            crear_empresa()
        elif menu == 5:
            mostrar_ordenes_venta()
        elif menu == 6:
            crear_graficos("Ventas")
        elif menu == 7:
            print("Moviendo al menu principal")
            guardar_empresas()
            guardar_ventas()
            bol_menu_ventas = False


# Editar_orden_venta sirve para editar las ordenes de venta
def editar_orden_venta():
    global venta_id, menu, Nempresa
    if len(ventas) == 0:
        print("No hay ordenes de venta, redirigiendo a la creacion de ordendes")
        crear_orden("venta")
    else:
        bol = True
        while bol:
            cont = 0
            for venta in ventas.values():
                if venta.estado != "Cancelada":
                    print("ID: " + str(venta.id))
                    print("Descripcion: " + venta.descripcion)
                    print("Estado: " + venta.estado)
                    print("Empresas en la compra.")
                    for empresa in venta.vendedores.values():
                        print("Nombre: " + empresa.empresa)
                else:
                    cont += 1
            if cont != len(ventas):
                try:
                    venta_id = int(input("Escriba el id de la venta que quiere editar: "))
                except ValueError:
                    print("Debe escribir un numero")
                if ventas.keys().__contains__(venta_id):
                    if ventas[venta_id].estado == "Cancelada":
                        print("Id no valido.")
                    else:
                        bol = False
                else:
                    print("El id seleccionado no existe")
                print("¿Quiere cambiar la descripcion?")
                opcion = input("Escriba S: ").upper()
                if opcion == "S":
                    bol = True
                    while bol:
                        descripcion = input("Escriba la descripcion: ")
                        if descripcion != "":
                            ventas[venta_id].descripcion = descripcion
                            bol = False
                        else:
                            print("La descripcion no puede estar vacia")
                print("¿Quiere cambiar el estado?")
                opcion = input("Escriba S: ").upper()
                if opcion == "S":
                    estado = enum_estado("venta")
                    ventas[venta_id].estado = estado
                print("¿Quiere añadir o quitar compradores?")
                opcion = input("Escriba S: ").upper()
                if opcion == "S":
                    bol_submenu = True
                    while bol_submenu:
                        print("\n-1 Añadir comprador.\n-2 Quitar comprador.\n-3 Terminar de editar la orden de venta.")
                        try:
                            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
                            if menu < 1 or menu > 3:
                                print("Esa opcion no esta en el menu.")
                        except ValueError:
                            print("No ha elegido un numero.")
                        if menu == 1:
                            bol = True
                            while bol:
                                print("Empresas en la compra.")
                                for empresa in empresas.values():
                                    print("Nombre: " + empresa.empresa)
                                Nempresa = input("Escriba el nombre de la empresa, escriba Salir si quiere salir: ")
                                if empresas.keys().__contains__(Nempresa):
                                    if ventas[venta_id].vendedores.keys().__contains__(Nempresa):
                                        print("La empresa ya se encuentra en la orden de compra")
                                    else:
                                        bol = False
                                elif Nempresa.lower().capitalize() == "Salir":
                                    print("Saliendo")
                                    bol = False
                                else:
                                    print("La empresa no se encuentra en la lista")
                            if Nempresa.lower().capitalize() != "Salir":
                                if cancelar():
                                    print("Cancelando operacion.")
                                else:
                                    ventas[venta_id].ayadir_comprador(empresas[Nempresa])
                                    empresas[Nempresa].ayadir_ventas(ventas[venta_id])
                        if menu == 2:
                            bol = True
                            while bol:
                                print("Empresas en la venta.")
                                for empresa in ventas[venta_id].vendedores.values():
                                    print("Nombre: " + empresa.empresa)
                                Nempresa = input("Escriba el nombre de la empresa, escriba Salir si quiere salir: ")
                                if empresas.keys().__contains__(Nempresa):
                                    if ventas[venta_id].vendedores.keys().__contains__(Nempresa):
                                        bol = False
                                    else:
                                        print("La empresa no se encuentra en la orden de compra")
                                elif Nempresa.lower().capitalize() == "Salir":
                                    print("Saliendo")
                                    bol = False
                                else:
                                    print("La empresa no se encuentra en la lista")
                                if Nempresa.lower().capitalize() != "Salir":
                                    if cancelar():
                                        print("Cancelando operacion.")
                                else:
                                    ventas[venta_id].vendedores.pop(Nempresa)
                                    empresas[Nempresa].ventas.pop(venta_id)
                        if menu == 3:
                            print("Saliendo.")
                            bol_submenu = False
            else:
                print("No hay ordenes de venta para editar.")
            print("Terminando operacion.")
            bol = False


# Anular_orden_venta sirve para anular las ordenes de venta
def anular_orden_venta():
    global venta_id
    bol = True
    while bol:
        cont = 0
        for venta in ventas.values():
            if venta.estado != "Cancelada":
                print("ID: " + str(venta.id))
                print("Descripcion: " + venta.descripcion)
                print("Estado: " + venta.estado)
                print("Empresas en la compra.")
                for empresa in venta.vendedores.values():
                    print("Nombre: " + empresa.empresa)
            else:
                cont += 1
        if cont != len(ventas):
            try:
                venta_id = int(input("Escriba el id de la venta que quiere anular: "))
            except ValueError:
                print("Debe escribir un numero")
            if ventas.keys().__contains__(venta_id):
                if ventas[venta_id].estado == "Cancelada":
                    print("Ese id no es valido")
                else:
                    bol = False
            else:
                print("El id seleccionado no existe")
            if cancelar():
                print("Cancelando operacion")
            else:
                ventas[venta_id].estado = Estado.CANCELADA.value
        else:
            bol = False
            print("No hay ordendes de venta para poder anular")


# Mostrar_ordenes_venta sirve para mostrar las ordenes de venta
def mostrar_ordenes_venta():
    if len(ventas) > 0:
        for venta in ventas.values():
            print("Orden de venta.")
            print("ID: " + str(venta.id))
            print("Descripción: " + venta.descripcion)
            print("Estado: " + venta.estado)
            print("Empresas en la orden.")
            for empresa in venta.vendedores.values():
                print("Empresa: " + empresa.empresa)
    else:
        print("No hay ordenes de venta")


# Menu_produccion es el menu al que acceden los empleados con el departamento de produccion
def menu_produccion():
    global menu
    bol_menu_produccion = True
    while bol_menu_produccion:
        print(
            "\n-1 Crear orden de producción.\n-2 Borrar orden de producción.\n-3 Añadir materia prima.\n-4 Añadir "
            "objetos.\n-5 Ver ordenes de producción.\n-6 Crear Grafico.\n-7 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 3:
                print("Esa opcion no esta en el menu.")
        except ValueError:
            print("No ha elegido un numero.")
        if menu == 1:
            crear_orden_produccion()
        elif menu == 2:
            borrar_orden_produccion()
        elif menu == 3:
            crear_materia_prima()
        elif menu == 4:
            crear_objetos()
        elif menu == 5:
            mostrar_produccion()
        elif menu == 6:
            crear_graficos("Produccion")
        elif menu == 7:
            print("Moviendo al menu principal")
            guardar_produccion()
            guardar_objetos_materia_prima()
            bol_menu_produccion = False


# Crear_orden_produccion sirve para crear las ordenes de produccion
def crear_orden_produccion():
    global descripcion, cantidad, objeto_id
    bol = True
    while bol:
        if len(objetos) > 0:
            bol_submenu = True
            while bol_submenu:
                descripcion = input("Inserte la descripcion de la orden de producción: ")
                if descripcion != "":
                    bol_submenu = False
                else:
                    print("La descripción no puede estar vacia")
            bol_submenu = True
            while bol_submenu:
                try:
                    cantidad = int(input("Inserte la cantidad de la orden de producción: "))
                    if cantidad > 0:
                        bol_submenu = False
                    else:
                        print("Debe escribir un numero mayor a 0.")
                except ValueError:
                    print("No has escrito un numero.")
            bol_submenu = True
            while bol_submenu:
                for objeto in objetos.values():
                    print("ID: " + str(objeto.id))
                    print("Nombre: " + objeto.nombre)
                    print("Descripción: " + objeto.descripcion)
                try:
                    objeto_id = int(input("Inserte el id del objeto que quiere añadir: "))
                    if objetos.keys().__contains__(objeto_id):
                        bol_submenu = False
                    else:
                        print("El id no esta en la lista")
                except ValueError:
                    print("No has escrito un id correcto")
            if cancelar():
                print("Cancelando operación.")
            else:
                produccion[len(produccion)] = Produccion(len(produccion), descripcion, cantidad, objetos[objeto_id])
            opcion = input("Quiere seguir creando ordenes de produccion, escriba S: ")
            if opcion.upper() != "S":
                bol = False
        else:
            print("No hay objetos almacenados, debe crear uno")
            crear_objetos()


# Borrar_orden_produccion sirve para borrar las ordenes de produccion
def borrar_orden_produccion():
    for producto in produccion.values():
        print("ID: " + str(producto.id))
        print("Descripción: " + producto.descripcion)
        print("Cantidad: " + str(producto.cantidad))
    try:
        producto_id = int(input("Escriba el id de la orden de produccion: "))
        if produccion.keys().__contains__(producto_id):
            if cancelar():
                print("Cancelando operacion")
            else:
                produccion.pop(producto_id)
        else:
            print("El id indicado no esta en la lista")
    except ValueError:
        print("No has escrito un id correcto")


# Crear_materia_prima sirve para poder crear las materias primas necesarias para los objetos
def crear_materia_prima():
    global nombre, descripcion
    bol = True
    while bol:
        bol_submenu = True
        while bol_submenu:
            nombre = input("Inserte el nombre de la materia prima: ")
            if nombre != "":
                bol_submenu = False
            else:
                print("El nombre no puede estar vacio.")
        bol_submenu = True
        while bol_submenu:
            descripcion = input("Inserte la descripcion de la materia prima: ")
            if descripcion != "":
                bol_submenu = False
            else:
                print("La descripcion no puede estar vacio.")
        if cancelar():
            print("Cancelando operacion")
        else:
            materia_prima[len(materia_prima)] = MateriaPrima(len(materia_prima), nombre, descripcion)
        bol = False


# Crear_objetos sirve para poder crear objetos
def crear_objetos():
    global nombre, descripcion
    bol = True
    while bol:
        bol_submenu = True
        while bol_submenu:
            nombre = input("Inserte el nombre del objeto: ")
            if nombre != "":
                bol_submenu = False
            else:
                print("El nombre no puede estar vacio.")
        bol_submenu = True
        while bol_submenu:
            descripcion = input("Inserte una descripción del objeto: ")
            if descripcion != "":
                bol_submenu = False
            else:
                print("La descripción no puede estar vacia.")
        if cancelar():
            print("Cancelando operacion.")
        else:
            objeto_id = len(objetos)
            objetos[objeto_id] = Objeto(objeto_id, nombre, descripcion)
            print("Añada la materia prima")
            bol_submenu = True
            while bol_submenu:
                if len(materia_prima) > 0:
                    print("Materia Prima disponible")
                    for materia in materia_prima.values():
                        print("ID: " + str(materia.id))
                        print("Nombre: " + materia.nombre)
                        print("Descripcion: " + materia.descripcion)
                    try:
                        materia_id = int(input("Escriba el id de la materia prima: "))
                        if materia_prima.keys().__contains__(materia_id):
                            if objetos[objeto_id].materiales.keys().__contains__(materia_id):
                                print("La materia prima ya esta en el objeto.")
                            else:
                                if cancelar():
                                    print("Cancelando operacion")
                                else:
                                    objetos[objeto_id].ayadir_materia_prima(materia_prima[materia_id])
                                    materia_prima[materia_id].ayadir_objeto(objetos[objeto_id])
                            if input(
                                    "Escriba salir si no quiere seguir añadiendo materias primas: ").lower().capitalize() == "Salir":
                                bol_submenu = False
                                bol = False
                        else:
                            print("El id indicado no esta en la lista")
                    except ValueError:
                        print("No has escrito un id correcto")
                else:
                    print("No hay materias prima añada una nueva materia prima.")
                    crear_materia_prima()


# Mostrar_produccion sirve para mostrar las ordenes de produccion
def mostrar_produccion():
    if len(produccion) > 0:
        for orden in produccion.values():
            print("ID: " + str(orden.id))
            print("Descripción: " + orden.descripcion)
            print("cantidad: " + str(orden.cantidad))
            print("Objetos")
            print("ID: " + str(orden.objeto.id))
            print("Nombre: " + orden.objeto.nombre)
            print("Descripción: " + orden.objeto.descripcion)
            print("Materia Prima")
            for materiaprima in orden.objeto.materiales.values():
                print("ID: " + str(materiaprima.id))
                print("Nombre: " + materiaprima.nombre)
                print("Descripción: " + materiaprima.descripcion)
    else:
        print("No hay ordenes de produccion.")


# Menu_RRHH es el menu al que acceden los empleados con el departamento de RRHH
def menu_RRHH():
    global menu
    bol_menu_RRHH = True
    while bol_menu_RRHH:
        print(
            "\n-1 Mostrar lista de trabajadores.\n-2 Dar de alta trabajador.\n-3 Dar de baja trabajador.\n-4 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 4:
                print("Esa opcion no esta en el menu.")
        except ValueError:
            print("No ha elegido un numero.")
        if menu == 1:
            mostrar_empleados()
        elif menu == 2:
            registro()
        elif menu == 3:
            borrar_usuario()
        elif menu == 4:
            print("Moviendo al menu principal")
            guardar_usuarios()
            bol_menu_RRHH = False


# Mostrar_empleados muestra todos los empleados de la empresa
def mostrar_empleados():
    if len(usuarios) > 0:
        for usuario in usuarios.values():
            print("Usuario: " + usuario.usuario)
            print("Permisos: " + usuario.permisos)
            print("Departamento: " + usuario.departamento)
            print("")
    else:
        print("No existen usuarios.")


# Borrar_usuario sirve para borrar usuarios pero no se pueden borrar ni usuarios admin ni usuarios jefe
def borrar_usuario():
    bol = True
    while bol:
        for usuario in usuarios.values():
            if usuario.permisos != Permisos.ADMIN.value or usuario.permisos != Permisos.JEFE.value:
                print("Nombre usuario: " + usuario.usuario)
                print("Permisos: " + usuario.permisos)
                print("Departamento: " + usuario.departamento)
        Nusuario = input("Escribe el nombre del usuario que quieres borrar: ")
        if usuarios.keys().__contains__(Nusuario):
            if usuarios[Nusuario].permisos != Permisos.ADMIN.value or usuarios[Nusuario].permisos \
                    != Permisos.JEFE.value:
                if cancelar():
                    print("Cancelando operación.")
                else:
                    usuarios.pop(Nusuario)
                    if input("Quieres seguir borrando usuarios escribe S: ").upper() != "S":
                        print("Volviendo al menu.")
                        bol = False
            else:
                print("Ese usuario no existe")
        else:
            print("Ese usuario no existe.")


# Menu_completo es el menu que se muestra a los usuarios admin y jefe
def menu_completo():
    global menu, departamento, usuario_logueado
    bol_menu_completo = True
    while bol_menu_completo:
        print(
            "\nMENU ADMIN\n-1 Compras.\n-2 Ventas.\n-3 Produccion.\n-4 RRHH.\n-5 Crear usuarios.\n-6 Salir al login.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 6:
                print("Esa opcion no esta en el menu.")
        except ValueError:
            print("No ha elegido un numero.")
        if menu == 1:
            print("Saliendo al menu compras")
            menu_compras()
        elif menu == 2:
            print("Saliendo al menu ventas")
            menu_ventas()
        elif menu == 3:
            print("Saliendo al menu produccion")
            menu_produccion()
        elif menu == 4:
            print("Saliendo al menu RRHH")
            menu_RRHH()
        elif menu == 5:
            print("Crear usuarios")
            registro()
        elif menu == 6:
            print("Saliendo al menu login")
            bol_menu_completo = False


# Menu_lecturas es el menu que se muestra a los usuarios con permisos de lectura
def menu_lecturas():
    if usuario_logueado.departamento == "Compras":
        mostrar_ordenes_compra()
    if usuario_logueado.departamento == "Ventas":
        mostrar_ordenes_venta()
    if usuario_logueado.departamento == "Produccion":
        mostrar_produccion()
    if usuario_logueado.departamento == "RRHH":
        mostrar_empleados()


# crear_graficos sirve para crear graficos en base al departamento
def crear_graficos(departamento):
    if departamento == "Compras":
        if len(compras) > 0:
            bucle_graficos(departamento, compras)
        else:
            print("No existen compras para crear graficos")
    if departamento == "Ventas":
        if len(ventas) > 0:
            bucle_graficos(departamento, ventas)
        else:
            print("No existen ventas para crear graficos")
    if departamento == "Produccion":
        if len(produccion) > 0:
            bucle_graficos(departamento, produccion)
        else:
            print("No existen ventas para crear graficos")


# Bucle_graficos es el bucle para poder rellenar los graficos
def bucle_graficos(nombre, arrays):
    global nombre_grafico
    eje_x = [Estado.COMPRADO.value, Estado.VENDIDO.value, Estado.ESPERA.value, Estado.CANCELADA.value]
    eje_y = [0, 0, 0, 0]
    if nombre != "Produccion":
        for array in arrays.values():
            if array.estado == Estado.COMPRADO.value:
                eje_y[0] += 1
            elif array.estado == Estado.VENDIDO.value:
                eje_y[1] += 1
            elif array.estado == Estado.ESPERA.value:
                eje_y[2] += 1
            elif array.estado == Estado.CANCELADA.value:
                eje_y[3] += 1
    else:
        eje_x.clear()
        eje_y.clear()
        for producto in produccion.values():
            eje_x.append(producto.objeto.nombre)
            eje_y.append(producto.cantidad)
    plt.bar(eje_x, eje_y)
    plt.ylabel('Cantidad de ' + nombre.lower())
    plt.xlabel('Estados de las ' + nombre.lower())
    plt.title('Grafica de informes de ' + nombre.lower())
    bol = True
    while bol:
        nombre_grafico = input("Indique el nombre que quiere del grafico: ")
        if nombre != "":
            bol = False
        else:
            print("EL nombre del grafico no puede estar vacio")
    plt.savefig("Graficos/" + nombre + "/ " + nombre_grafico + ".pdf")
    plt.show()


def conexion():
    db = pymysql.connect(host="127.0.0.1", user='root', password='root', db='python', port=3306)
    db.close()


comprobar_csv()
menu_login()
