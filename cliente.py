import socket
import threading
import time

PORT = 5050
SERVER_IP = "26.103.100.48"
ADDR = (SERVER_IP, PORT)
FORMAT = "utf-8"

# configurações do socket TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# configurações do socket UDP
UDP_PORT = 5051
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("", UDP_PORT))

nome_jogador = ""

def handle_messages():
    while True:
        try:
            mensagem = client.recv(1024).decode(FORMAT)
            if mensagem:
                print(f"[SERVER] {mensagem}")
            else:
                print("[DESCONECTADO] Conexão com o servidor foi encerrada.")
                break
        except:
            print("[ERRO] Erro ao receber a mensagem do servidor.")
            break

def escutar_udp():
    while True:
        try:
            data, _ = udp_socket.recvfrom(1024)
            print(f"[UDP] {data.decode(FORMAT)}")
        except:
            print("[ERRO] Erro ao receber mensagem UDP.")
            break

def enviar(mensagem):
    try:
        client.send(mensagem.encode(FORMAT))
    except:
        print("[ERRO] Não foi possível enviar a mensagem para o servidor.")

def enviar_mensagem():
    while True:
        mensagem = input("Digite a senha (4 dígitos): ")

        if len(mensagem) != 4:
            print("[ERRO] A senha deve ter exatamente 4 dígitos.")
            continue

        if not mensagem.isdigit():
            print("[ERRO] A senha deve conter apenas números.")
            continue

        enviar(f"guess:{mensagem}")
        break

def iniciar_envio():
    try:
        while True:
            enviar_mensagem()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Cliente está sendo desligado...")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {str(e)}")

def iniciar():
    global nome_jogador
    
    print(f"[CONECTANDO] Conectando ao servidor em {SERVER_IP}:{PORT}...")
    
    
    while True:
        nome_jogador = input("Digite seu nome: ").strip()
        if nome_jogador:
            break
        print("[ERRO] O nome não pode estar vazio.")
    
    
    enviar(f"name:{nome_jogador}")
    print(f"[BEM-VINDO] Olá, {nome_jogador}! Você está conectado ao jogo.")
    
    try:
        
        thread1 = threading.Thread(target=handle_messages)
        thread1.daemon = True  
        thread1.start()
        
    
        thread2 = threading.Thread(target=iniciar_envio)
        thread2.daemon = True  
        thread2.start()
        
        
        thread1.join()
        thread2.join()
        
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Cliente está sendo desligado...")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {str(e)}")
    finally:
        client.close()
        print("[DESCONECTADO] Conexão encerrada.")

if __name__ == "__main__":
    iniciar()
