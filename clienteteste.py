import socket
import threading
import time

PORT= 5050
SERVER_IP = "26.103.100.48"
ADDR= (SERVER_IP, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def handle_messages():
    while True:
        try:
            mensagem = client.recv(1024).decode(FORMAT)
            if mensagem:
                print(f"[SERVER] {mensagem}")
            else:
                break
        except:
            print("Erro ao receber a mensagem do servidor.")
            break

def enviar(mensagem):
    client.send(mensagem.encode(FORMAT))

def enviar_mensagem():
    mensagem = input("Digite a senha: ")
    enviar(f"guess:{mensagem}")


def iniciar_envio():
    while True:
        enviar_mensagem()
        time.sleep(0.1)

def iniciar():
    thread1= threading.Thread(target=handle_messages)
    thread2= threading.Thread(target=iniciar_envio)
    thread1.start()
    thread2.start()
    pass

iniciar()
