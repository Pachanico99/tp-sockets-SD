import socket
import os
import re

os.makedirs('client/repos', exist_ok=True)
BUFFER_SIZE = 1024

HOST = '127.0.0.1'
PORT = 65432

NUMBER_PATTERN = re.compile(r'^\d+$')

def local_ls_execute(dir):
    files = '\n'.join(os.listdir(dir))
    if files:
        return files
    else:
        return "Empty: No hay archivos en el repositorio."

def get_id_dir():
    while True:
        id_dir = int(input("Ingrese el ID del directorio: "))
        if NUMBER_PATTERN.match(str(id_dir)):
            return f"Z:\\Users\\Pacheco\\Desktop\\Python-Projects\\tp-sockets-SD\\client\\repos\\repo_{id_dir}"
        else:
            print("ID inválido. Intente de nuevo.")

def receive_full_message(sock):
    header = b""
    while b":" not in header or header.count(b":") < 2:
        header += sock.recv(1)
    parts = header.split(b":", 2)
    total_length = int(parts[0])
    status = parts[1].decode()
    prefix = b":".join(parts[:2]) + b":"
    content = parts[2]

    while len(content) < total_length:
        content += sock.recv(BUFFER_SIZE)

    return status, content

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        dir = get_id_dir()
        os.makedirs(dir, exist_ok=True)
        print(f"[[CLIENT ON]]\nConnected to {(HOST, PORT)}")

        while True:
            cmd = input(">>> ")
            if not cmd:
                continue

            if cmd == "!ls":
                print(local_ls_execute(dir))
                continue

            sock.sendall(cmd.encode())
            status, content = receive_full_message(sock)

            if cmd.startswith("get") and status == "ok":
                filename = cmd.split(" ", 1)[1]
                filepath = os.path.join(dir, filename)
                with open(filepath, "wb") as f:
                    f.write(content)
                print(f"[+] Archivo guardado como {filepath}")
            elif status == "ok":
                msg = content.decode(errors="ignore")
                if msg == "EXIT":
                    print("[*] Conexión cerrada por el servidor.")
                    break
                print(msg)
            else:
                print(f"[ERROR] {content.decode(errors='ignore')}")

if __name__ == "__main__":
    main()

