import socket
import threading
import time

PORT = 5050
SERVER_IP = "10.25.1.243"
ADDR = (SERVER_IP, PORT)
FORMAT = "utf-8"

# configurações do socket TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# configurações do socket UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("", 0))  
udp_porta_local = udp_socket.getsockname()[1]

nome_jogador = ""
ativo = True  

def handle_messages():
    global ativo
    while ativo:
        try:
            mensagem = client.recv(1024).decode(FORMAT)
            if mensagem:
                print(f"[SERVER] {mensagem}")
                if "Acertou!" in mensagem:
                    ativo = False
                    break
            else:
                print("[DESCONECTADO] Conexão com o servidor foi encerrada.")
                ativo = False
                break
        except:
            print("[ERRO] Erro ao receber a mensagem do servidor.")
            ativo = False
            break

def escutar_udp():
    global ativo
    while ativo:
        try:
            data, _ = udp_socket.recvfrom(1024)
            print(f"[UDP] {data.decode(FORMAT)}")
        except:
            break

def enviar(mensagem):
    global ativo
    if not ativo:
        return
    try:
        client.send(mensagem.encode(FORMAT))
    except:
        print("[ERRO] Não foi possível enviar a mensagem para o servidor.")
        ativo = False

def enviar_mensagem():
    global ativo
    while ativo:
        mensagem = input("Digite a senha (4 dígitos): ")
        if not ativo:
            break

        if len(mensagem) != 4:
            print("[ERRO] A senha deve ter exatamente 4 dígitos.")
            continue

        if not mensagem.isdigit():
            print("[ERRO] A senha deve conter apenas números.")
            continue

        enviar(f"guess:{mensagem}")
        break

def iniciar_envio():
    global ativo
    try:
        while ativo:
            enviar_mensagem()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Cliente está sendo desligado...")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {str(e)}")

def iniciar():
    global nome_jogador, ativo
    
    print(f"[CONECTANDO] Conectando ao servidor em {SERVER_IP}:{PORT}...")

    while True:
        nome_jogador = input("Digite seu nome: ").strip()
        if nome_jogador:
            break
        print("[ERRO] O nome não pode estar vazio.")

    enviar(f"name:{nome_jogador}")
    enviar(f"udp_port:{udp_porta_local}")
    print(f"[BEM-VINDO] Olá, {nome_jogador}! Você está conectado ao jogo.")
    print(f"[DICA] A dica é: Terceira copa do Brasil")

    try:
        threads = [
            threading.Thread(target=handle_messages, daemon=True),
            threading.Thread(target=escutar_udp, daemon=True),
            threading.Thread(target=iniciar_envio, daemon=True)
        ]
        for t in threads:
            t.start()

        while ativo:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Cliente está sendo desligado...")
    finally:
        client.close()
        udp_socket.close()
        print("[DESCONECTADO] Conexão encerrada.")

if __name__ == "__main__":
    iniciar()
