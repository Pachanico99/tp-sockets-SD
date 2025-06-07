import socket
import select
import os

# https://realpython.com/python-sockets/#echo-client-and-server

HOST = '127.0.0.1'  # IP local del servidor (localhost).
PORT = 2121         # Debe coincidir con el puerto del cliente.
BUFFER_SIZE = 4096  # Tamaño máximo del buffer.

def format_response(status, content):
    # Creamos el mensaje que se envía al cliente.
    encoded = content.encode()
    length = len(encoded)
    return f"{length}:{status}:{content}"

def process_command(command):
    # Procesamos el comando recibido del cliente.
    command = command.strip()
    if command == "ls":
        # El servidor le envía al cliente los nombres de archivos y directorios del directorio actual.
        files = "\n".join(os.listdir("."))
        return format_response("OK", files)

    elif command.startswith("get "):
        # El servidor le envía al cliente el archivo solicitado.
        _, filename = command.split(maxsplit=1)
        if os.path.exists(filename) and os.path.isfile(filename):
            try:
                with open(filename, "r") as f:
                    content = f.read()
                return format_response("OK", content)
            except Exception as e:
                return format_response("ERROR", f"No se pudo leer el archivo: {e}")
        else:
            return format_response("ERROR", "Archivo inexistente")
    
    else:
        return format_response("ERROR", "Comando inválido")

def start_server():
    # Iniciamos el servidor.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setblocking(False)

    sockets_list = [server_socket]
    clients = {}

    print(f"[+] Servidor FTP escuchando en {HOST}:{PORT}")

    while True:
        # Recibimos y procesamos los mensajes de los clientes.
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            # Si el socket notificado es el del servidor, aceptamos una nueva conexión.
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                client_socket.setblocking(False)
                sockets_list.append(client_socket)
                clients[client_socket] = b""
                print(f"[+] Nueva conexión desde {client_address}")
            else:
                # Si el socket notificado no es el del servidor, es un cliente.
                try:
                    data = notified_socket.recv(BUFFER_SIZE) # 
                    # Recibimos el mensaje del cliente.
                    if data:
                        # Si el cliente envía un mensaje, lo procesamos.
                        command = data.decode()
                        print(f"[>] Comando recibido: {command}")
                        response = process_command(command)
                        notified_socket.sendall(response.encode())
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()
                    # Cuando terminamos de procesar el mensaje, cerramos la conexión con el cliente.
                except Exception as e:
                    print(f"[!] Error con cliente: {e}")
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()
                    # Si ocurre un error, cerramos la conexión con el cliente.

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            if notified_socket in clients:
                del clients[notified_socket]
            notified_socket.close()

if __name__ == "__main__":
    start_server()
