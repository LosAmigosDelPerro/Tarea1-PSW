from cryptography.fernet import Fernet

# Generate a Fernet key
key = Fernet.generate_key()

# Save the key to a file
with open('.env', 'w') as f:
    f.write(f'KEY = "{key.decode()}"')