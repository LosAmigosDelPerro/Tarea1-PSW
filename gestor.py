import os
import getpass
import json
import signal
import logging
from generadorwlogs import generar_contrasena
from datetime import datetime
from dotenv import load_dotenv
from time import sleep
from cryptography.fernet import Fernet

def print_menu():
    print("\nMenú:")
    print("1. Agregar contraseña")
    print("2. Recuperar contraseña")
    print("3. Actualizar contraseña")
    print("4. Eliminar contraseña")
    print("5. Generar contraseña")
    print("6. Salir")

def sub_menu():
    print("\n1. Mostrar todas las contraseñas")
    print("2. Buscar por alias")
    print("3. Volver")

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def check_master_password(master_password):
    return (len(master_password) >= 8
            and len(master_password) <= 32
            and any(c.isupper() for c in master_password)
            and any(c.islower() for c in master_password)
            and any(c.isdigit() for c in master_password)
            and any(c in "*?!@#$/(){\}=.,;:" for c in master_password))

def create_master_password():
    while True:
        master_password = getpass.getpass("Ingrese la contraseña maestra: ")
        if check_master_password(master_password):
            return master_password
        else:
            logging.warning("La contraseña maestra no cumple con los requisitos.")
            print("La contraseña no cumple con los requisitos.")

def encrypt_password(password, key):
    cipher_suite = Fernet(key)
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password, key):
    cipher_suite = Fernet(key)
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode())
    return decrypted_password.decode()

def exit_handler(signum, frame):
    global master_password
    global key
    global passwords_data
    
    if master_password is not None:
        with open("passwords.txt", "w") as f:
            f.write(json.dumps({"master_password": encrypt_password(master_password, key).decode()}))
            f.write("\n"+json.dumps(passwords_data))
    print("\nSaliendo...")
    logging.info("Se ejecuto Ctrl+C para salir del programa.")
    exit(0)

def index_input(len):
    while True:
        try:
            index = int(input("Ingrese el número de la opción: "))
            if index >= 1 and index <= len:
                return index
            else:
                print("El número ingresado no es válido.")
        except ValueError:
            print("El valor ingresado no es válido.")

def filter_passwords(keyword):
    filtered_passwords = []
    for data in passwords_data:
        if keyword in data:
            filtered_passwords.append(data)
    return filtered_passwords

def list_passwords(choice):
    if choice == "1":
        print("Aplicaciones disponibles:")
        list_passwords = []
        for i, alias in enumerate(passwords_data):
            list_passwords.append(alias)
            print(f"{i + 1}. {alias}")
        selected_index = index_input(len(passwords_data)) - 1
        selected_data = list_passwords[selected_index]
    elif choice == "2":
        keyword = input("Ingrese el alias de la aplicación: ")
        filtered_passwords = filter_passwords(keyword)
        if filtered_passwords:
            list_passwords = []
            for i, alias in enumerate(filtered_passwords):
                list_passwords.append(alias)
                print(f"{i + 1}. {alias}")
            selected_index = index_input(len(filtered_passwords)) - 1
            selected_data = list_passwords[selected_index]
        else:
            print("No se encontraron aplicaciones con ese alias.")
            return None
    else:
        print("Opción no válida.")
        return None
    return selected_data


def add_password():
    app_alias = input("Ingrese el alias de la aplicación: ")
    app_password = getpass.getpass("Ingrese la contraseña: ")
    encrypted_password = encrypt_password(app_password, key)
    if app_alias in passwords_data:
        logging.warning("Ya existe una contraseña con ese alias.")
        print("Ya existe una contraseña con ese alias.")
        return
    passwords_data[app_alias] = encrypted_password.decode()
    logging.info(f"Se creó la contraseña de {app_alias}")
    print("Contraseña agregada exitosamente.")

def get_password(choice):
    if passwords_data:
        selected_data = list_passwords(choice)
        if selected_data is None:
            logging.warning("No se encontraron aplicaciones con ese alias.")
            print("No se encontraron aplicaciones con ese alias.")
            return
        selected_password = decrypt_password(passwords_data[selected_data], key)
        print(f"Aplicacion: {selected_data}")
        print(f"Contraseña: {selected_password}")
        logging.info(f"Se obtuvo la contraseña de {selected_data}")
        print("Volviendo al menu en 5 segundos...")
        sleep(5)
        clear()
    else:
        print("No hay contraseñas almacenadas.")

def update_password(choice):
    if passwords_data:
        selected_data = list_passwords(choice)
        if selected_data is None:
            logging.warning("No se encontraron aplicaciones con ese alias.")
            print("No se encontraron aplicaciones con ese alias.")
            return
        new_password = getpass.getpass("Ingrese la nueva contraseña: ")
        encrypted_new_password = encrypt_password(new_password, key)
        passwords_data[selected_data] = encrypted_new_password.decode()
        logging.info(f"Se actualizó la contraseña de {selected_data}")
        print("Contraseña actualizada exitosamente.")
        print("Volviendo al menu en 5 segundos...")
        sleep(5)
        clear()
    else:
        print("No hay contraseñas almacenadas.")

def remove_password(choice):
    if passwords_data:
        selected_data = list_passwords(choice)
        if selected_data is None:
            logging.warning("No se encontraron aplicaciones con ese alias.")
            print("No se encontraron aplicaciones con ese alias.")
            return
        logging.info(f"Se eliminó la contraseña de {selected_data}")
        passwords_data.pop(selected_data)
        print("Contraseña eliminada exitosamente.")
        print("Volviendo al menu en 5 segundos...")
        sleep(5)
        clear()
    else:
        print("No hay contraseñas almacenadas.")

def main():
    global master_password
    global key
    global passwords_data

    logging.basicConfig(filename=datetime.now().strftime("%d-%m-%Y %H-%M-%S")+".log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    encoding = "UTF-8")
    load_dotenv()
    signal.signal(signal.SIGINT, exit_handler)

    if not os.path.exists("passwords.txt"):
        with open("passwords.txt", "w") as f:
            f.write("")

    master_password = None
    key = os.getenv('KEY').encode()
    passwords_data = {}
    is_logged = False

    while True:
        if not is_logged:
            if os.path.getsize("passwords.txt") == 0:
                master_password = create_master_password()  
                logging.info("Contraseña maestra creada.")
            else:
                with open("passwords.txt", "r") as f:
                    passwords = f.readlines()
                    passwords_data = [json.loads(p) for p in passwords if p.strip()]
                    stored_master_password = passwords_data[0]["master_password"]
                    if len(passwords_data) > 1:
                        passwords_data = passwords_data[1]
                master_password = getpass.getpass("Ingrese la contraseña maestra: ")
                if master_password != decrypt_password(stored_master_password, key):
                    print("Contraseña maestra incorrecta.")
                    logging.warning("Contraseña maestra incorrecta.")
                    continue
                master_password = decrypt_password(stored_master_password, key)
                logging.info("Contraseña maestra correcta.")
            is_logged = True
            logging.info("Sesión iniciada.")

        clear()
        print_menu()
        choice = input("Seleccione una opción: ")
        if choice == "1":
            logging.info("Se seleccionó la opción 1.")
            add_password()
            
        elif choice == "2":
            logging.info("Se seleccionó la opción 2.")
            sub_menu()
            sub_choice = input("Seleccione una opción: ")
            get_password(sub_choice)
        
        elif choice == "3":
            logging.info("Se seleccionó la opción 3.")
            sub_menu()
            sub_choice = input("Seleccione una opción: ")
            update_password(sub_choice)

        elif choice == "4":
            logging.info("Se seleccionó la opción 4.")
            sub_menu()
            sub_choice = input("Seleccione una opción: ")
            remove_password(sub_choice)

        elif choice == "5":
            generar_contrasena()

        elif choice == "6":
            with open("passwords.txt", "w") as f:
                logging.info("Se seleccionó la opción 5.")
                f.write(json.dumps({"master_password": encrypt_password(master_password, key).decode()}))
                f.write("\n"+json.dumps(passwords_data))
            print("Saliendo...")
            break

        else:
            logging.warning("Se ingresó una opción no válida.")
            print("Opción no válida.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.error("Se ejecuto Ctrl+C dentro de un input.")
    except Exception as e:
        logging.error(e)
        print("Ocurrió un error inesperado.")