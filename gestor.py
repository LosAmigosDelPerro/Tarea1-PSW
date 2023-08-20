import os
import getpass
import json
import signal
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def printMenu():
    print("\nMenú:")
    print("1. Agregar contraseña")
    print("2. Recuperar contraseña")
    print("3. Actualizar contraseña")
    print("4. Eliminar contraseña")
    print("5. Salir")

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
            print("La contraseña no cumple con los requisitos.")

# Función para encriptar una contraseña
def encrypt_password(password, key):
    cipher_suite = Fernet(key)
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password

# Función para desencriptar una contraseña
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
            f.write(json.dumps({"master_password": encrypt_password(master_password, key).decode()}) + "\n")
            for p in passwords_data:
                f.write(json.dumps(p)+"\n")
    print("\nSaliendo...")
    exit(0)


# Función principal
def main():
    global master_password
    global key
    global passwords_data

    load_dotenv()
    signal.signal(signal.SIGINT, exit_handler)

    if not os.path.exists("passwords.txt"):
        with open("passwords.txt", "w") as f:
            f.write("")

    master_password = None
    key = os.getenv('KEY').encode()
    passwords_data = []
    is_logged = False

    while True:
        if not is_logged:
            if os.path.getsize("passwords.txt") == 0:
                master_password = create_master_password()  
            else:
                with open("passwords.txt", "r") as f:
                    passwords = f.readlines()
                    passwords_data = [json.loads(p) for p in passwords if p.strip()]
                    stored_master_password = passwords_data[0]["master_password"]
                    passwords_data.pop(0) 
                master_password = getpass.getpass("Ingrese la contraseña maestra: ")
                if master_password != decrypt_password(stored_master_password, key):
                    print("Contraseña maestra incorrecta.")
                    continue
                master_password = decrypt_password(stored_master_password, key)
            is_logged = True

        printMenu()

        choice = input("Seleccione una opción: ")

        if choice == "1":
                app_alias = input("Ingrese el alias de la aplicación: ")
                app_password = getpass.getpass("Ingrese la contraseña: ")
                encrypted_password = encrypt_password(app_password, key)
                passwords_data.append({"alias": app_alias, "password": encrypted_password.decode()})
                print("Contraseña agregada exitosamente.")
            
        elif choice == "2":
            if passwords_data:
                print("Aplicaciones disponibles:")
                for i, data in enumerate(passwords_data):
                    app_alias = data["alias"]
                    print(f"{i + 1}. {app_alias}")
                selected_index = int(input("Seleccione el número de la aplicación: ")) - 1
                selected_data = passwords_data[selected_index]
                selected_password = decrypt_password(selected_data["password"], key)
                alias = selected_data["alias"]
                print(f"Aplicacion: {alias}")
                print(f"Contraseña: {selected_password}")
                input("Presione Enter para continuar.")
            else:
                print("No hay contraseñas almacenadas.")
        
        elif choice == "3":
            if passwords_data:
                print("Aplicaciones disponibles:")
                for i, data in enumerate(passwords_data):
                    app_alias = data["alias"]
                    print(f"{i + 1}. {app_alias}")
                selected_index = int(input("Seleccione el número de la aplicación: ")) - 1
                selected_data = passwords_data[selected_index]
                new_password = getpass.getpass("Ingrese la nueva contraseña: ")
                encrypted_new_password = encrypt_password(new_password, key)
                selected_data["password"] = encrypted_new_password.decode()
                print("Contraseña actualizada exitosamente.")
            else:
                print("No hay contraseñas almacenadas.")
        elif choice == "4":
            if passwords_data:
                print("Aplicaciones disponibles:")
                for i, data in enumerate(passwords_data):
                    app_alias = data["alias"]
                    print(f"{i + 1}. {app_alias}")
                selected_index = int(input("Seleccione el número de la aplicación: ")) - 1
                passwords_data.pop(selected_index)
                print("Contraseña eliminada exitosamente.")
            else:
                print("No hay contraseñas almacenadas.")
        
        elif choice == "5":
            with open("passwords.txt", "w") as f:
                f.write(json.dumps({"master_password": encrypt_password(master_password, key).decode()}) + "\n")
                for p in passwords_data:
                    f.write(json.dumps(p)+"\n")
            print("Saliendo...")
            break

        elif choice == "4":
            if passwords_data:
                print("Aplicaciones disponibles:")
                for i, data in enumerate(passwords_data):
                    app_alias = data["alias"]
                    print(f"{i + 1}. {app_alias}")
                selected_index = int(input("Seleccione el número de la aplicación: ")) - 1
                passwords_data.pop(selected_index)
                print("Contraseña eliminada exitosamente.")
            else:
                print("No hay contraseñas almacenadas.")
        
        elif choice == "5":
            with open("passwords.txt", "wb") as f:
                f.write(json.dumps(passwords_data).encode())
            print("Saliendo...")
            break

        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()