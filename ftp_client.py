import socket
import os

# https://realpython.com/python-sockets/#echo-client-and-server

SERVER_HOST = '127.0.0.1'  # IP local del servidor (localhost).
SERVER_PORT = 2121         # Puerto del servidor.
BUFFER_SIZE = 4096         # Tamaño máximo del buffer.

def main():
    while True:
        try:
            command = input("> ").strip()
            if not command:
                continue

            if command == "exit":
                # Finaliza la sesión.
                break

            elif command == "!ls":
                # Muestra el contenido del directorio local del cliente.
                for f in os.listdir("."):
                    print(f)

            elif command == "ls":
                # Muestra el contenido del directorio remoto.
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((SERVER_HOST, SERVER_PORT))
                    s.sendall(command.encode())
                    response = s.recv(BUFFER_SIZE).decode()
                    length, status, content = parse_response(response)
                    if status == "OK":
                        print(content)
                    else:
                        print("Error:", content)

            elif command.startswith("get "):
                # Copia un archivo del directorio remoto en el directorio local.
                _, filename = command.split(maxsplit=1)     # Separamos el nombre del archivo
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((SERVER_HOST, SERVER_PORT))
                    s.sendall(command.encode())
                    response = s.recv(BUFFER_SIZE).decode()
                    length, status, content = parse_response(response)
                    if status == "OK":
                        with open(filename, "w") as f:
                            f.write(content)
                        print(f"Archivo '{filename}' descargado correctamente.")
                    else:
                        print("Error:", content)

            else:
                print("Error: Comando inválido.")

        except Exception as e:
            print("Error:", e)

def parse_response(response):
    # Parseamos o dividimos la respuesta del servidor en tres partes <long>:<status>:<texto>.
    try:
        length_str, status, text = response.split(":", 2)
        length = int(length_str)
        return length, status, text
    except ValueError:
        return 0, "ERROR", "Respuesta malformada del servidor."

if __name__ == "__main__":
    main()
