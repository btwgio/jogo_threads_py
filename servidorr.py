import socket
import threading
import time

SERVER_IP = "26.103.100.48"
PORT= 5050
ADDR= (SERVER_IP, PORT)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

senha = "4321"

def tentativa_correta(tentativa):
    acertos = 0
    for i in range(len(senha)):
        if tentativa[i] == senha[i]:
            acertos += 1
    return acertos
    

def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] um usuário se conectou pelo endereço {addr}")
    while True:
        try:
            msg = conn.recv(1024).decode(FORMAT)
            if msg.startswith("guess:"):
                tentativa = msg[6:]
                corretos = tentativa_correta(tentativa)
                if tentativa==senha:
                    conn.send("Acertou! Você venceu!".encode(FORMAT))
                else:
                    conn.send(f"{corretos} dígitos certos".encode(FORMAT))
        except:
            print(f"[DESCONECTADO] {addr}")
            break



def start():
    print("Servidor iniciado")
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()       
