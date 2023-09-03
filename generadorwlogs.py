import random
import string
import os
import time
import logging

def generar_contrasena():
    print("Generador de Contraseñas Seguras")
    print("=================================")
    
    # Pedir la longitud deseada por el usuario
    while True:
        try:
            longitud = int(input("Ingrese la longitud deseada (entre 8 y 32 caracteres): "))
            if 8 <= longitud <= 32:
                break
            else:
                print("La longitud debe estar entre 8 y 32 caracteres.")
        except ValueError:
            logging.warning("No se ha ingresado un numero valido")
            print("Ingrese un número válido.")

    
    logging.info("Se ha solicitado generar una contraseña segura de longitud " + str(longitud) + ".")
    
    var_ascii = string.ascii_letters
    mayus = var_ascii[26:]
    mini = var_ascii[:26]
    digitos = string.digits
    especiales = '*?!@#$/()=.,;:'

    min_mayus = random.sample(mayus, 1)
    min_minus = random.sample(mini, 1)
    min_digitos = random.sample(digitos, 1)
    min_especiales = random.sample(especiales, 1)

    # Pedir los tipos de caracteres permitidos
    opciones = {
        '1': string.ascii_letters,
        '2': string.digits + string.digits,
        '3': '*?!@#$/()=.,;:',
    }
    tipos_permitidos = []
    while True:
        print("Seleccione los tipos de caracteres permitidos:\n")
        print("1. Letras")
        print("2. Números")
        print("3. Caracteres especiales")
        seleccion = input("Ingrese los números de opciones separados por espacios: ")
        tipos_seleccionados = seleccion.split()
        
        for opcion in tipos_seleccionados:
            if opcion in opciones:
                tipos_permitidos.extend(opciones[opcion])
        
        if tipos_permitidos:
            break
        else:
            logging.warning("No se ha seleccionado ningun tipo de caracteres validos")
            print("\n***Seleccione al menos un tipo de caracteres.***\n")

    # Asegurar que la longitud mínima sea 12 si no hay caracteres especiales
    if '3' not in tipos_seleccionados and longitud < 12:
        longitud = 12
        logging.info("Se modifico la longitud de la contraseña a 12 caracteres.")
    
    
    # Generar la contraseña
    contrasena = random.sample(tipos_permitidos, longitud)
    random.shuffle(contrasena)
    contrasena = ''.join(contrasena)

    ubicaciones = random.sample(range(longitud), 4)
    auxiliar_cont = list(contrasena)
    
    # Asegurar que la contraseña cumple con los criterios de seguridad

    if '1' in tipos_seleccionados and '3' not in tipos_seleccionados and '2' not in tipos_seleccionados: #solo letras
        auxiliar_cont[ubicaciones[0]] = min_mayus[0]
        auxiliar_cont[ubicaciones[1]] = min_minus[0]
    elif '1' in tipos_seleccionados and '3' in tipos_seleccionados and '2' not in tipos_seleccionados: #letras y especiales
        auxiliar_cont[ubicaciones[0]] = min_mayus[0]
        auxiliar_cont[ubicaciones[1]] = min_minus[0]
        auxiliar_cont[ubicaciones[2]] = min_especiales[0]
    elif '1' in tipos_seleccionados and '3' not in tipos_seleccionados and '2' in tipos_seleccionados: #letras y numeros
        auxiliar_cont[ubicaciones[0]] = min_mayus[0]
        auxiliar_cont[ubicaciones[1]] = min_minus[0]
        auxiliar_cont[ubicaciones[2]] = min_digitos[0]
    elif '1' not in tipos_seleccionados and '3' in tipos_seleccionados and '2' in tipos_seleccionados: #numeros y especiales
        auxiliar_cont[ubicaciones[0]] = min_digitos[0]
        auxiliar_cont[ubicaciones[1]] = min_especiales[0]
    elif '1' in tipos_seleccionados and '3' in tipos_seleccionados and '2' in tipos_seleccionados: #todos
        auxiliar_cont[ubicaciones[0]] = min_mayus[0]
        auxiliar_cont[ubicaciones[1]] = min_minus[0]
        auxiliar_cont[ubicaciones[2]] = min_digitos[0]
        auxiliar_cont[ubicaciones[3]] = min_especiales[0]      

    

    contrasena_segura = ''.join(auxiliar_cont)
    logging.info("Se genero una contraseña segura.")
    print("Contraseña segura generada:", contrasena_segura)
    print("La contraseña será visible durante 15 segundos...")
    time.sleep(15)
    ocultar_contrasena(len(contrasena))

def ocultar_contrasena(length):
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

    # Mostrar una "contraseña" oculta de la misma longitud
    hidden_password = '*' * length
    print("Contraseña generada:", hidden_password)
    print("La contraseña ha sido ocultada.")


