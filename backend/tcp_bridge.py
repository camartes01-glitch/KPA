import socket
import threading
import sys

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        src.close()
        dst.close()

def handle_client(client_socket, target_host, target_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target_host, target_port))
        t1 = threading.Thread(target=forward, args=(client_socket, server_socket), daemon=True)
        t2 = threading.Thread(target=forward, args=(server_socket, client_socket), daemon=True)
        t1.start()
        t2.start()
    except Exception as e:
        client_socket.close()

def run_bridge(listen_host, listen_port, target_host, target_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((listen_host, listen_port))
    server.listen(128)
    print(f"[TCP Bridge] Forwarding {listen_host}:{listen_port} -> {target_host}:{target_port}", flush=True)
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, target_host, target_port), daemon=True).start()

if __name__ == "__main__":
    lh = sys.argv[1]
    lp = int(sys.argv[2])
    th = sys.argv[3]
    tp = int(sys.argv[4])
    run_bridge(lh, lp, th, tp)
