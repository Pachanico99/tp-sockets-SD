import socket
import selectors
import types
import re
import os

COMMAND_PATTERN = re.compile(r'(ls|get|exit)(?:\s+([a-zA-Z0-9_-]+\.txt))?')
BUFFER_SIZE = 1024
sel = selectors.DefaultSelector()
HOST = '127.0.0.1'
PORT = 65432

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"[+] Conexión aceptada de {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(BUFFER_SIZE)
        if recv_data:
            cmd = recv_data.decode().strip()
            print(f"[{data.addr}] Comando recibido: {cmd}")
            response = handle_command(cmd)
            data.outb = response if isinstance(response, bytes) else response.encode()
        else:
            print(f"[-] Cerrando conexión con {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

def format_response(status, message):
    if isinstance(message, str):
        encoded_msg = message.encode()
    else:
        encoded_msg = message
    header = f"{len(encoded_msg)}:{status}:".encode()
    return header + encoded_msg


def handle_command(cmd):
    if cmd == "ls":
        try:
            files = '\n'.join(os.listdir("Z:\\Users\\Pacheco\\Desktop\\Python-Projects\\tp-sockets-SD\\server\\repo"))
            if files:
                return format_response("ok", files)
            else:
                return format_response("ok", "Empty: No hay archivos en el repositorio.")
        except Exception as e:
            return format_response("error", str(e))

    elif cmd.startswith("get"):
        _, filename = cmd.split(" ", 1)
        filepath = os.path.join("Z:\\Users\\Pacheco\\Desktop\\Python-Projects\\tp-sockets-SD\\server\\repo", filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                return format_response("ok", content)
            except Exception as e:
                return format_response("error", f"Error al leer archivo: {str(e)}")
        else:
            return format_response("error", "Archivo no encontrado.")

    elif cmd == "exit":
        return format_response("ok", "EXIT")

    return format_response("error", "Comando no reconocido.")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
        lsock.bind((HOST, PORT))
        lsock.listen()
        print(f"[[SERVER ON]]\nListening on {(HOST, PORT)}")
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
        except KeyboardInterrupt:
            print("[[SERVER OFF]]\nClosing server...")
        finally:
            sel.close()

if __name__ == "__main__":
    main()
