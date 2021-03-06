import csv
import hashlib
import os
import random
import pymysql

import matplotlib.pyplot as plt

from Clases.Compras import Compras
from Clases.Conexion import Conexion
from Clases.Empresa import Empresa
from Clases.MateriaPrima import MateriaPrima
from Clases.Objeto import Objeto
from Clases.Produccion import Produccion
from Clases.Usuario import Usuario
from Clases.Ventas import Ventas
from Enum.Departamentos import Departamentos
from Enum.Estado import Estado
from Enum.Permisos import Permisos

usuario_logueado = Usuario("", "", "")
usuarios = {}
produccion = {}
empresas = {}
materia_prima = {}
objetos = {}
compras = {}
ventas = {}
datos_conexion = Conexion("", "", "", "", 0)


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
    bol = True
    while bol:
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


# Generar_contraseya sirve para poder generar una contrase??a segura y aleatoria
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


# Registro es el sistema para poder registrar los usuarios en la BBDD
def registro_BBDD():
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
            db = conexion()
            cursor = db.cursor()
            sql = """SELECT * from Usuarios where usuario=%s"""
            cursor.execute(sql, usuario)
            if cursor.rowcount != 0:
                print("El usuario ya existe.")
            else:
                print("Creando usuario")
                print("La clave del usuario es: " + clave)
                clave = hashlib.sha224(clave.encode('utf-8')).hexdigest()
                val = (usuario, clave, permisos, departamento)
                guardar_usuarios_BBDD(val)
                confirmacion = input(
                    "Si quiere seguir creando usuarios escriba S: ")
                if confirmacion.upper() != "S":
                    bol_menu = False


# Guardar_usuarios sirve para poder guardar los usuarios en la BBDD
def guardar_usuarios_BBDD(val):
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """INSERT INTO Usuarios (usuario,clave,permisos,departamento) VALUES (%s,%s,%s,%s)"""
        cursor.execute(sql, val)
        db.commit()
        db.close()


# Menu_login es el menu donde puedes acceder al login, registrar un usuario temporal o terminar la aplicacion
def menu_login():
    global menu, departamento, usuario_logueado
    comprobar_csv()
    usuario_logueado = Usuario("", "", "")
    bol_menu_login = True
    while bol_menu_login:
        print(
            "\nMENU PRINCIPAL\n-1 Login.\n-2 Registrar usuario temporal.\n-3 Salir.\n En el informe del programa "
            "estan los usuarios creados por defecto")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 3:
                print("Esa opcion no esta en el menu.")
            else:
                if menu == 1:
                    login_BBDD()
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
                    usuario_logueado = Usuario('temporal', 'Lectura', departamento)
                    menu_lecturas()
                elif menu == 3:
                    print("Guardando los datos, espere un momento.")
                    print("Saliendo del programa.")
                    bol_menu_login = False
        except ValueError:
            print("No ha elegido un numero.")


def cargar_empresas_BBDD():
    empresas.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from Empresas"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            empresas[dato[0]] = Empresa(dato[0])
        db.close()


# Crear_empresa sirve para poder a??adir empresas
def crear_empresa():
    bol_menu = True
    while bol_menu:
        cargar_empresas_BBDD()
        empresa = input("Escriba el nombre de la empresa Escriba Salir si quiere salir: ")
        if empresas.keys().__contains__(empresa):
            print("La empresa ya exite")
        elif empresa == "":
            print("Debe escribir un nombre para la empresa")
        elif empresa.lower().capitalize() == "Salir":
            print("Saliendo")
            bol_menu = False
        else:
            db = conexion()
            if db:
                cursor = db.cursor()
                sql = """INSERT INTO Empresas VALUES (%s)"""
                val = (empresa)
                cursor.execute(sql, val)
                db.commit()
                db.close()
            empresas[empresa] = Empresa(empresa)
            bol_menu = False


# Crear_orden sirve para poder crear una orden de venta
def crear_orden(objeto):
    global Nempresa, bol, descripcion, empresa
    cargar_empresas_BBDD()
    if len(empresas) == 0:
        print("No existen empresas debe a??adir")
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
            descripcion = input("Escriba una descripci??n de la " + objeto + ": ")
            if descripcion != "":
                bol = False
            else:
                print("Debe escribir una descripci??n.")
        estado = enum_estado(objeto)
        if cancelar():
            print("Cancelando operacion y redirigiendo al menu.")
            bol = False
        else:
            if objeto == "venta":
                ventas[len(ventas)] = Ventas(len(ventas), descripcion, estado, Nempresa)
                empresas[Nempresa].ayadir_ventas(ventas[len(ventas) - 1])
                venta = ventas[len(ventas) - 1]
                guardar_orden_BBDD('venta', venta)
            else:
                compras[len(compras)] = Compras(len(compras), descripcion, estado, Nempresa)
                empresas[Nempresa].ayadir_compras(compras[len(compras) - 1])
                compra = compras[len(compras) - 1]
                guardar_orden_BBDD('compra', compra)
            opcion = input("Si quiere seguir creando ordendes de compra escriba S: ").upper()
            if opcion != "S":
                print("Saliendo al menu")


def guardar_orden_BBDD(departamento, objeto):
    db = conexion()
    if db:
        cursor = db.cursor()
        if departamento == "venta":
            sql = """INSERT INTO ventas (descripcion,estado,empresa) VALUES (%s,%s,%s)"""
            val = (objeto.descripcion, objeto.estado, objeto.vendedor)
            cursor.execute(sql, val)
        else:
            sql = """INSERT INTO compras (descripcion,estado,empresa) VALUES (%s,%s,%s)"""
            val = (objeto.descripcion, objeto.estado, objeto.proveedor)
            cursor.execute(sql, val)
        db.commit()
        db.close()


# Menu_compras es el menu al que acceden los empleados del departamento de compras
def menu_compras():
    global menu
    bol_menu_compras = True
    while bol_menu_compras:
        print(
            "\n-1 Crear orden de compra.\n-2 Editar orden de compra.\n-3 Anular orden de compra.\n-4 Crear "
            "vendedores.\n-5 Mostrar ??rdenes de compra.\n-6 Crear Grafico.\n-7 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 7:
                print("Esa opcion no esta en el menu.")
            else:
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
                    bol_menu_compras = False
        except ValueError:
            print("No ha elegido un numero.")


# Editar_orden_compra sirve para editar las ordenes de compra
def editar_orden_compra():
    global compra_id, menu, Nempresa
    compras.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        val = Estado.CANCELADA.value
        sql = """SELECT * from compras where not estado=%s"""
        cursor.execute(sql, val)
        datos = cursor.fetchall()
        for dato in datos:
            compras[dato[0]] = Compras(dato[0], dato[1], dato[2], dato[3])
        db.close()
    if len(compras) == 0:
        print("No hay ordenes de compra, redirigiendo a la creacion de ordendes")
        crear_orden("compra")
    else:
        bol = True
        while bol:
            for compra in compras.values():
                print("ID: " + str(compra.id))
                print("Descripcion: " + compra.descripcion)
                print("Estado: " + compra.estado)
                print("Empresa en la orden de compra.")
                print(compra.proveedor)
            try:
                compra_id = int(input("Escriba el id de la compra que quiere editar: "))
                if compras.keys().__contains__(compra_id):
                    bol = False
                else:
                    print("El id seleccionado no existe")
            except ValueError:
                print("Debe escribir un numero")
        print("??Quiere cambiar la descripcion?")
        opcion = input("Escriba S: ").upper()
        if opcion == "S":
            bol = True
            while bol:
                descripcion = input("Escriba la descripcion: ")
                if descripcion != "":
                    compras[compra_id].descripcion = descripcion
                    db = conexion()
                    cursor = db.cursor()
                    val = (descripcion, compra_id)
                    sql = """UPDATE compras set descripcion=%s where id=%s"""
                    cursor.execute(sql, val)
                    db.commit()
                    db.close()
                    bol = False
                else:
                    print("La descripcion no puede estar vacia")
        print("??Quiere cambiar el estado?")
        opcion = input("Escriba S: ").upper()
        if opcion == "S":
            estado = enum_estado("compra")
            compras[compra_id].estado = estado
            db = conexion()
            if db:
                cursor = db.cursor()
                val = (estado, compra_id)
                sql = """UPDATE compras set estado=%s where id=%s"""
                cursor.execute(sql, val)
                db.commit()
                db.close()
        print("??Quiere a??adir o quitar compradores?")
        opcion = input("Escriba S: ").upper()
        if opcion == "S":
            bol_submenu = True
            while bol_submenu:
                print("\n-1 cambiar comprador. \n-2 Terminar de editar la orden de compra.")
                try:
                    menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
                    if menu < 1 or menu > 2:
                        print("Esa opcion no esta en el menu.")
                    else:
                        if menu == 1:
                            bol = True
                            while bol:
                                cargar_empresas_BBDD()
                                print("Empresas a seleccionar.")
                                for empresa in empresas.values():
                                    print("Nombre: " + empresa.empresa)
                                Nempresa = input("Escriba el nombre de la empresa, escriba Salir si quiere salir: ")
                                if empresas.keys().__contains__(Nempresa):
                                    if compras[compra_id].proveedor == Nempresa:
                                        print("La empresa ya se encuentra en la orden de compra")
                                    else:
                                        bol = False
                                        if cancelar():
                                            print("Cancelando operacion.")
                                        else:
                                            Nempresa_antigua = compras[compra_id].proveedor
                                            empresas[Nempresa_antigua].quitar_compra(compra_id)
                                            compras[compra_id].proveedor = Nempresa
                                            empresas[Nempresa].ayadir_compras(compras[compra_id])
                                            db = conexion()
                                            if db:
                                                cursor = db.cursor()
                                                val = (Nempresa, compra_id)
                                                sql = """UPDATE compras set empresa=%s where id=%s"""
                                                cursor.execute(sql, val)
                                                db.commit()
                                                db.close()
                                elif Nempresa.lower().capitalize() == "Salir":
                                    print("Saliendo")
                                    bol = False
                                else:
                                    print("La empresa no se encuentra en la lista")
                        if menu == 2:
                            print("Saliendo.")
                            bol_submenu = False
                except ValueError:
                    print("No ha elegido un numero.")

            print("Terminando operacion.")


# Anular_orden_compra sirve para anular las ordenes de compra
def anular_orden_compra():
    global compra_id
    bol = True
    while bol:
        compras.clear()
        db = conexion()
        if db:
            cursor = db.cursor()
            val = Estado.CANCELADA.value
            sql = """SELECT * from compras where not estado=%s"""
            cursor.execute(sql, val)
            datos = cursor.fetchall()
            for dato in datos:
                compras[dato[0]] = Compras(dato[0], dato[1], dato[2], dato[3])
            db.close()
        for compra in compras.values():
            print("ID: " + str(compra.id))
            print("Descripcion: " + compra.descripcion)
            print("Estado: " + compra.estado)
            print("Empresa en la compra.")
            print(compra.proveedor)
        if len(compras) != 0:
            try:
                compra_id = int(input("Escriba el id de la compra que quiere anular: "))
                if compras.keys().__contains__(compra_id):
                    bol = False
                    if cancelar():
                        print("Cancelando operacion")
                    else:
                        db = conexion()
                        if db:
                            cursor = db.cursor()
                            val = (Estado.CANCELADA.value, compra_id)
                            sql = """UPDATE compras SET estado=%s WHERE id=%s"""
                            cursor.execute(sql, val)
                            db.commit()
                            db.close()
                            compras[compra_id].estado = Estado.CANCELADA.value
                else:
                    print("El id seleccionado no existe")

            except ValueError:
                print("Debe escribir un numero")

        else:
            bol = False
            print("No hay ordendes de compra para poder anular")


# Mostrar_ordenes_compra sirve para mostrar las ordenes de compra
def mostrar_ordenes_compra():
    compras.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from compras"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            compras[dato[0]] = Compras(dato[0], dato[1], dato[2], dato[3])
        db.close()
    if len(compras) > 0:
        for compra in compras.values():
            print("Orden de compra.")
            print("ID: " + str(compra.id))
            print("Descripci??n: " + compra.descripcion)
            print("Estado: " + compra.estado)
            print("Empresa en la orden.")
            print(compra.proveedor)
    else:
        print("No hay ordenes de compra")


# Menu_ventas es el menu al que acceden los empleados con el departamento de ventas
def menu_ventas():
    global menu
    bol_menu_ventas = True
    while bol_menu_ventas:
        print(
            "\n-1 Crear orden de venta.\n-2 Editar orden de venta.\n-3 Anular orden de venta.\n-4 Crear "
            "compradores.\n-5 Mostrar ??rdenes de venta.\n-6 Crear Grafico.\n-7 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 7:
                print("Esa opcion no esta en el menu.")
            else:
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
                    bol_menu_ventas = False
        except ValueError:
            print("No ha elegido un numero.")


# Editar_orden_venta sirve para editar las ordenes de venta
def editar_orden_venta():
    global venta_id, menu, Nempresa
    ventas.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        val = Estado.CANCELADA.value
        sql = """SELECT * from ventas where not estado=%s"""
        cursor.execute(sql, val)
        datos = cursor.fetchall()
        for dato in datos:
            ventas[dato[0]] = Ventas(dato[0], dato[1], dato[2], dato[3])
        db.close()
    if len(ventas) == 0:
        print("No hay ordenes de venta, redirigiendo a la creacion de ordendes")
        crear_orden("venta")
    else:
        bol = True
        while bol:
            for venta in ventas.values():
                print("ID: " + str(venta.id))
                print("Descripcion: " + venta.descripcion)
                print("Estado: " + venta.estado)
                print("Empresa en la orden de compra.")
                print(venta.vendedor)
            try:
                venta_id = int(input("Escriba el id de la venta que quiere editar: "))
                if ventas.keys().__contains__(venta_id):
                    bol = False
                else:
                    print("El id seleccionado no existe")
            except ValueError:
                print("Debe escribir un numero")
        print("??Quiere cambiar la descripcion?")
        opcion = input("Escriba S: ").upper()
        if opcion == "S":
            bol = True
            while bol:
                descripcion = input("Escriba la descripcion: ")
                if descripcion != "":
                    ventas[venta_id].descripcion = descripcion
                    db = conexion()
                    if db:
                        cursor = db.cursor()
                        val = (descripcion, venta_id)
                        sql = """UPDATE ventas set descripcion=%s where id=%s"""
                        cursor.execute(sql, val)
                        db.commit()
                        db.close()
                    bol = False
                else:
                    print("La descripcion no puede estar vacia")
        print("??Quiere cambiar el estado?")
        opcion = input("Escriba S: ").upper()
        if opcion == "S":
            estado = enum_estado("venta")
            ventas[venta_id].estado = estado
            db = conexion()
            if db:
                cursor = db.cursor()
                val = (estado, venta_id)
                sql = """UPDATE ventas set estado=%s where id=%s"""
                cursor.execute(sql, val)
                db.commit()
                db.close()
        print("??Quiere a??adir o quitar vendedores?")
        opcion = input("Escriba S: ").upper()
        if opcion == "S":
            bol_submenu = True
            while bol_submenu:
                print("\n-1 cambiar vendedor. \n-2 Terminar de editar la orden de compra.")
                try:
                    menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
                    if menu < 1 or menu > 2:
                        print("Esa opcion no esta en el menu.")
                    else:
                        if menu == 1:
                            bol = True
                            while bol:
                                empresas.clear()
                                cargar_empresas_BBDD()
                                print("Empresas a seleccionar.")
                                for empresa in empresas.values():
                                    print("Nombre: " + empresa.empresa)
                                Nempresa = input(
                                    "Escriba el nombre de la empresa, escriba Salir si quiere salir: ")
                                if empresas.keys().__contains__(Nempresa):
                                    if ventas[venta_id].vendedor == Nempresa:
                                        print("La empresa ya se encuentra en la orden de compra")
                                    else:
                                        bol = False
                                        if cancelar():
                                            print("Cancelando operacion.")
                                        else:
                                            Nempresa_antigua = ventas[venta_id].proveedor
                                            empresas[Nempresa_antigua].quitar_venta(compra_id)
                                            ventas[venta_id].proveedor = Nempresa
                                            empresas[Nempresa].ayadir_ventas(compras[compra_id])
                                            db = conexion()
                                            if db:
                                                cursor = db.cursor()
                                                val = (Nempresa, venta_id)
                                                sql = """UPDATE ventas set empresa=%s where id=%s"""
                                                cursor.execute(sql, val)
                                                db.commit()
                                                db.close()
                                elif Nempresa.lower().capitalize() == "Salir":
                                    print("Saliendo")
                                    bol = False
                                else:
                                    print("La empresa no se encuentra en la lista")
                        if menu == 2:
                            print("Saliendo.")
                            bol_submenu = False
                except ValueError:
                    print("No ha elegido un numero.")
        print("Terminando operacion.")


# Anular_orden_venta sirve para anular las ordenes de venta
def anular_orden_venta():
    global venta_id
    bol = True
    while bol:
        ventas.clear()
        db = conexion()
        if db:
            cursor = db.cursor()
            val = Estado.CANCELADA.value
            sql = """SELECT * from ventas where not estado=%s"""
            cursor.execute(sql, val)
            datos = cursor.fetchall()
            for dato in datos:
                ventas[dato[0]] = Ventas(dato[0], dato[1], dato[2], dato[3])
                db.close()
        for venta in ventas.values():
            print("ID: " + str(venta.id))
            print("Descripcion: " + venta.descripcion)
            print("Estado: " + venta.estado)
            print("Empresa en la compra.")
            print(venta.vendedor)
        if len(ventas) != 0:
            try:
                venta_id = int(input("Escriba el id de la venta que quiere anular: "))
                if ventas.keys().__contains__(venta_id):
                    bol = False
                    if cancelar():
                        print("Cancelando operacion")
                    else:
                        db = conexion()
                        if db:
                            cursor = db.cursor()
                            val = (Estado.CANCELADA.value, venta_id)
                            sql = """UPDATE ventas set estado=%s where id=%s"""
                            cursor.execute(sql, val)
                            db.commit()
                            db.close()
                            ventas[venta_id].estado = Estado.CANCELADA.value
                else:
                    print("El id seleccionado no existe")
            except ValueError:
                print("Debe escribir un numero")
        else:
            bol = False
            print("No hay ordendes de venta para poder anular")


# Mostrar_ordenes_venta sirve para mostrar las ordenes de venta
def mostrar_ordenes_venta():
    ventas.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from ventas"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            ventas[dato[0]] = Ventas(dato[0], dato[1], dato[2], dato[3])
        db.close()
    if len(ventas) > 0:
        for venta in ventas.values():
            print("Orden de venta.")
            print("ID: " + str(venta.id))
            print("Descripci??n: " + venta.descripcion)
            print("Estado: " + venta.estado)
            print("Empresa en la orden.")
            print(venta.vendedor)
    else:
        print("No hay ordenes de venta")


# Menu_produccion es el menu al que acceden los empleados con el departamento de produccion
def menu_produccion():
    global menu
    bol_menu_produccion = True
    while bol_menu_produccion:
        print(
            "\n-1 Crear orden de producci??n.\n-2 Borrar orden de producci??n.\n-3 A??adir materia prima.\n-4 A??adir "
            "objetos.\n-5 Ver ordenes de producci??n.\n-6 Crear Grafico.\n-7 Salir.")
        try:
            menu = int(input("Escriba el numero de la opcion que quiere elegir: "))
            if menu < 1 or menu > 7:
                print("Esa opcion no esta en el menu.")
            else:
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
                    bol_menu_produccion = False
        except ValueError:
            print("No ha elegido un numero.")


# Crear_orden_produccion sirve para crear las ordenes de produccion
def crear_orden_produccion():
    global descripcion, cantidad, objeto_id
    objetos.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from objetos"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])
        db.close()
    bol = True
    while bol:
        if len(objetos) > 0:
            bol_submenu = True
            while bol_submenu:
                descripcion = input("Inserte la descripcion de la orden de producci??n: ")
                if descripcion != "":
                    bol_submenu = False
                else:
                    print("La descripci??n no puede estar vacia")
            bol_submenu = True
            while bol_submenu:
                try:
                    cantidad = int(input("Inserte la cantidad de la orden de producci??n: "))
                    if cantidad > 0:
                        bol_submenu = False
                    else:
                        print("Debe escribir un numero mayor a 0.")
                except ValueError:
                    print("No has escrito un numero.")
            bol_submenu = True
            while bol_submenu:
                objetos.clear()
                db = conexion()
                if db:
                    cursor = db.cursor()
                    sql = """SELECT * from objetos"""
                    cursor.execute(sql)
                    datos = cursor.fetchall()
                    for dato in datos:
                        objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])
                    db.close()
                for objeto in objetos.values():
                    print("ID: " + str(objeto.id))
                    print("Nombre: " + objeto.nombre)
                    print("Descripci??n: " + objeto.descripcion)
                try:
                    objeto_id = int(input("Inserte el id del objeto que quiere a??adir: "))
                    if objetos.keys().__contains__(objeto_id):
                        bol_submenu = False
                        if cancelar():
                            print("Cancelando operaci??n.")
                        else:
                            produccion[len(produccion)] = Produccion(len(produccion), descripcion, cantidad, objeto_id)
                            db = conexion()
                            if db:
                                cursor = db.cursor()
                                sql = """INSERT INTO Produccion (descripcion,cantidad,objeto_id) VALUES (%s,%s,%s)"""
                                val = (descripcion, cantidad, objeto_id)
                                cursor.execute(sql, val)
                                db.commit()
                                db.close()
                    else:
                        print("El id no esta en la lista")
                except ValueError:
                    print("No has escrito un id correcto")
            opcion = input("Quiere seguir creando ordenes de produccion, escriba S: ")
            if opcion.upper() != "S":
                bol = False
        else:
            print("No hay objetos almacenados, debe crear uno")
            crear_objetos()


# Borrar_orden_produccion sirve para borrar las ordenes de produccion
def borrar_orden_produccion():
    produccion.clear()
    objetos.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from Produccion"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            produccion[dato[0]] = Produccion(dato[0], dato[1], dato[2], dato[3])
        sql = """SELECT * from objetos"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])
        db.close()
    if len(produccion) > 0:
        for producto in produccion.values():
            print("ID: " + str(producto.id))
            print("Descripci??n: " + producto.descripcion)
            print("Cantidad: " + str(producto.cantidad))
            print("Objeto de la orden")
            print("ID: " + str(objetos[producto.objeto_id].id))
            print("Nombre: " + objetos[producto.objeto_id].nombre)
            print("Descripcion: " + objetos[producto.objeto_id].descripcion)
        try:
            producto_id = int(input("Escriba el id de la orden de produccion: "))
            if produccion.keys().__contains__(producto_id):
                if cancelar():
                    print("Cancelando operacion")
                else:
                    db = conexion()
                    if db:
                        cursor = db.cursor()
                        sql = """DELETE FROM Produccion where id=%s"""
                        val = producto_id
                        cursor.execute(sql, val)
                        db.commit()
                        db.close()
                    produccion.pop(producto_id)
            else:
                print("El id indicado no esta en la lista")
        except ValueError:
            print("No has escrito un id correcto")
    else:
        print("No hay ordenes de produccion.")


# Crear_materia_prima sirve para poder crear las materias primas necesarias para los objetos
def crear_materia_prima():
    materia_prima.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from materia_prima"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            materia_prima[dato[0]] = MateriaPrima(dato[0], dato[1], dato[2])
        db.close()
    global nombre, descripcion
    bol = True
    while bol:
        bol_submenu = True
        while bol_submenu:
            nombre = input("Inserte el nombre de la materia prima: ")
            if nombre != "":
                bol_submenu = False
                for materia in materia_prima.values():
                    if materia.nombre == nombre:
                        print("La materia indicada ya existe")
                    else:
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
            db = conexion()
            if db:
                cursor = db.cursor()
                sql = """INSERT INTO materia_prima (nombre,descripcion) VALUES (%s,%s)"""
                val = (nombre, descripcion)
                cursor.execute(sql, val)
                db.commit()
                db.close()
        bol = False


# Crear_objetos sirve para poder crear objetos
def crear_objetos():
    global nombre, descripcion
    objetos.clear()
    materia_prima.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from materia_prima"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            materia_prima[dato[0]] = MateriaPrima(dato[0], dato[1], dato[2])

        cursor = db.cursor()
        sql = """SELECT * from objetos"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])

        sql = """SELECT * from materia_objetos"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            objetos[dato[0]].ayadir_materia_prima(materia_prima[dato[1]])
            materia_prima[dato[1]].ayadir_objeto(objetos[dato[0]])
        db.close()
    if len(materia_prima) == 0:
        print("No hay materias prima a??ada una nueva materia prima.")
        crear_materia_prima()
    else:
        objetos.clear()
        db = conexion()
        if db:
            cursor = db.cursor()
            sql = """SELECT * from objetos"""
            cursor.execute(sql)
            datos = cursor.fetchall()
            for dato in datos:
                objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])
            db.close()
        bol = True
        while bol:
            bol_submenu = True
            while bol_submenu:
                nombre = input("Inserte el nombre del objeto: ")
                if nombre != "":
                    conf = True
                    for objeto in objetos.values():
                        if objeto.nombre == nombre:
                            print("El objeto ya existe")
                            conf = False
                    if conf:
                        bol_submenu = False
                else:
                    print("El nombre no puede estar vacio.")
            bol_submenu = True
            while bol_submenu:
                descripcion = input("Inserte una descripci??n del objeto: ")
                if descripcion != "":
                    bol_submenu = False
                else:
                    print("La descripci??n no puede estar vacia.")
            if cancelar():
                print("Cancelando operacion.")
            else:
                objeto_id = len(objetos)
                objetos[objeto_id] = Objeto(objeto_id, nombre, descripcion)
                print("A??ada la materia prima")
                bol_submenu = True
                while bol_submenu:
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
                                    db = conexion()
                                    if db:
                                        objeto = objetos[objeto_id]
                                        cursor = db.cursor()
                                        sql = """INSERT INTO objetos (nombre,descripcion) VALUES (%s,%s)"""
                                        val = (objeto.nombre, objeto.descripcion)
                                        cursor.execute(sql, val)
                                        db.commit()
                                        cursor = db.cursor()
                                        val = objeto.nombre
                                        sql = """SELECT * from objetos where nombre=%s"""
                                        cursor.execute(sql, val)
                                        dato = cursor.fetchone()
                                        objeto = Objeto(dato[0], dato[1], dato[2])
                                        cursor = db.cursor()
                                        sql = """INSERT INTO materia_objetos (objeto_id, materia_id) VALUES (%s,%s)"""
                                        val = (objeto.id, materia_id)
                                        cursor.execute(sql, val)
                                        db.commit()
                                        db.close()
                        else:
                            print("El id indicado no esta en la lista")
                    except ValueError:
                        print("No has escrito un id correcto")
                    if input(
                            "Escriba salir si no quiere seguir a??adiendo materias primas: ").lower().capitalize() == "Salir":
                        bol_submenu = False
                        bol = False


# Mostrar_produccion sirve para mostrar las ordenes de produccion
def mostrar_produccion():
    produccion.clear()
    objetos.clear()
    materia_prima.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        sql = """SELECT * from Produccion"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            produccion[dato[0]] = Produccion(dato[0], dato[1], dato[2], dato[3])
        sql = """SELECT * from objetos"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])
        sql = """SELECT * from materia_prima"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            materia_prima[dato[0]] = MateriaPrima(dato[0], dato[1], dato[2])
        sql = """SELECT * from materia_objetos"""
        cursor.execute(sql)
        datos = cursor.fetchall()
        for dato in datos:
            objetos[dato[0]].ayadir_materia_prima(materia_prima[dato[1]])
            materia_prima[dato[1]].ayadir_objeto(objetos[dato[0]])
        db.close()
    if len(produccion) > 0:
        for producto in produccion.values():
            print("ID: " + str(producto.id))
            print("Descripci??n: " + producto.descripcion)
            print("Cantidad: " + str(producto.cantidad))
            print("Objeto de la orden")
            print("ID: " + str(objetos[producto.objeto_id].id))
            print("Nombre: " + objetos[producto.objeto_id].nombre)
            print("Descripcion: " + objetos[producto.objeto_id].descripcion)
            for materiaprima in objetos[producto.objeto_id].materiales.values():
                print("ID: " + str(materiaprima.id))
                print("Nombre: " + materiaprima.nombre)
                print("Descripci??n: " + materiaprima.descripcion)
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
            else:
                if menu == 1:
                    mostrar_empleados()
                elif menu == 2:
                    registro_BBDD()
                elif menu == 3:
                    borrar_usuario()
                elif menu == 4:
                    print("Moviendo al menu principal")
                    bol_menu_RRHH = False
        except ValueError:
            print("No ha elegido un numero.")


# Mostrar_empleados muestra todos los empleados de la empresa
def mostrar_empleados():
    usuarios.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        val = "Admin"
        sql = """SELECT usuario,permisos,departamento from Usuarios where not usuario=%s"""
        cursor.execute(sql, val)
        datos = cursor.fetchall()
        for dato in datos:
            usuarios[dato[0]] = Usuario(dato[0], dato[1], dato[2])
        db.close()
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
    usuarios.clear()
    db = conexion()
    if db:
        cursor = db.cursor()
        val = (Permisos.JEFE.value, Permisos.ADMIN.value)
        sql = """SELECT usuario,permisos,departamento from Usuarios where not permisos=%s or permisos=%s"""
        cursor.execute(sql, val)
        datos = cursor.fetchall()
        for dato in datos:
            usuarios[dato[0]] = Usuario(dato[0], dato[1], dato[2])
        db.close()
    bol = True
    while bol:
        for usuario in usuarios.values():
            print("Nombre usuario: " + usuario.usuario)
            print("Permisos: " + usuario.permisos)
            print("Departamento: " + usuario.departamento)
            print("")
        Nusuario = input("Escribe el nombre del usuario que quieres borrar: ")
        if usuarios.keys().__contains__(Nusuario):
            if cancelar():
                print("Cancelando operaci??n.")
            else:
                usuarios.pop(Nusuario)
                db = conexion()
                if db:
                    cursor = db.cursor()
                    sql = """DELETE FROM Usuarios where usuario=%s"""
                    val = Nusuario
                    cursor.execute(sql, val)
                    db.commit()
                    db.close()
                if input("Quieres seguir borrando usuarios escribe S: ").upper() != "S":
                    print("Volviendo al menu.")
                    bol = False
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
            else:
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
                    registro_BBDD()
                elif menu == 6:
                    print("Saliendo al menu login")
                    bol_menu_completo = False
        except ValueError:
            print("No ha elegido un numero.")


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
        compras.clear()
        db = conexion()
        if db:
            cursor = db.cursor()
            sql = """SELECT * from compras"""
            cursor.execute(sql)
            datos = cursor.fetchall()
            for dato in datos:
                compras[dato[0]] = Compras(dato[0], dato[1], dato[2], dato[3])
            db.close()
        if len(compras) > 0:
            bucle_graficos(departamento, compras)
        else:
            print("No existen compras para crear graficos")
    if departamento == "Ventas":
        ventas.clear()
        db = conexion()
        if db:
            cursor = db.cursor()
            sql = """SELECT * from ventas"""
            cursor.execute(sql)
            datos = cursor.fetchall()
            for dato in datos:
                ventas[dato[0]] = Ventas(dato[0], dato[1], dato[2], dato[3])
            db.close()
        if len(ventas) > 0:
            bucle_graficos(departamento, ventas)
        else:
            print("No existen ventas para crear graficos")
    if departamento == "Produccion":
        objetos.clear()
        produccion.clear()
        db = conexion()
        if db:
            cursor = db.cursor()
            sql = """SELECT * from objetos"""
            cursor.execute(sql)
            datos = cursor.fetchall()
            for dato in datos:
                objetos[dato[0]] = Objeto(dato[0], dato[1], dato[2])
            sql = """SELECT * from Produccion"""
            cursor.execute(sql)
            datos = cursor.fetchall()
            for dato in datos:
                produccion[dato[0]] = Produccion(dato[0], dato[1], dato[2], dato[3])
            db.close()
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
            eje_x.append(objetos[producto.objeto_id].nombre)
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


# Funcion que sirve para hacer la conexion con la BBDD
def conexion():
    global datos_conexion
    try:
        db = pymysql.connect(host=datos_conexion.host, user=datos_conexion.user, password=datos_conexion.password,
                             db=datos_conexion.db, port=datos_conexion.port)
        return db
    except Exception:
        print("Error de conexion con la BBDD, contacte con el admministrador.")
        return False


# Funcion para poder hacer login usando la  BBDD
def login_BBDD():
    global usuario, clave, usuario_logueado
    usuario = input("Indique el usuario: ")
    clave = input("Indique la clave del usuario: ")
    clave = hashlib.sha224(clave.encode('utf-8')).hexdigest()
    db = conexion()
    if db:
        cursor = db.cursor()
        val = (usuario, clave)
        sql = """SELECT usuario,permisos,departamento from Usuarios where usuario=%s and clave=%s"""
        cursor.execute(sql, val)
        dato = cursor.fetchone()
        if cursor.rowcount != 0:
            usuario_logueado = Usuario(dato[0], dato[1], dato[2])
        db.close()


def comprobar_csv():
    global datos_conexion
    fichero = "BBDD.csv"
    try:
        with open(fichero, 'r') as f:
            if os.stat(fichero).st_size == 0:
                bol_fichero = True
            else:
                bol_fichero = False
    except FileNotFoundError as e:
        bol_fichero = True
    if bol_fichero:
        print("Falta el archivo de configuraci??n de la BBDD.")
    else:
        with open(fichero) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                datos_conexion = Conexion(str(row['host']), str(row['user']), str(row['password']), str(row['db']), int(row['port']))


menu_login()
