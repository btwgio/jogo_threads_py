import socket
import threading
import time

# Configurações TCP
PORT = 5050
SERVER_IP = "26.103.100.48"
ADDR = (SERVER_IP, PORT)
FORMAT = "utf-8"

# Configurações UDP
UDP_PORT = 5051
UDP_ADDR = (SERVER_IP, UDP_PORT)

# Configuração dos sockets
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

def handle_udp():
    udp_client.settimeout(0.5)  # Timeout de 0.5 segundos
    while True:
        try:
            data, _ = udp_client.recvfrom(1024)
            mensagem = data.decode(FORMAT)
            
            # Não precisamos fazer nada com a confirmação, mas podemos imprimir para debug
            # print(f"[UDP] {mensagem}")
            
        except socket.timeout:
            # Timeout é normal, continua o loop
            pass
        except Exception as e:
            print(f"[ERRO UDP] {str(e)}")
            time.sleep(1)

def enviar(mensagem):
    try:
        client.send(mensagem.encode(FORMAT))
    except:
        print("[ERRO] Não foi possível enviar a mensagem para o servidor.")

def enviar_udp(mensagem):
    try:
        udp_client.sendto(mensagem.encode(FORMAT), UDP_ADDR)
    except Exception as e:
        print(f"[ERRO UDP] {str(e)}")

def enviar_mensagem():
    while True:
        mensagem = input("Digite a senha (4 dígitos): ")
        
        if len(mensagem) != 4:
            print("[ERRO] A senha deve ter exatamente 4 dígitos.")
            continue
        
        if not mensagem.isdigit():
            print("[ERRO] A senha deve conter apenas números.")
            continue
        
        # Registrar o tempo de início
        tempo_inicio = time.time()
        
        # Enviar a tentativa via TCP
        enviar(f"guess:{mensagem}")
        
        # Calcular o tempo que levou para enviar
        tempo_fim = time.time()
        tempo_ms = int((tempo_fim - tempo_inicio) * 1000)
        
        # Enviar informações de tempo via UDP
        enviar_udp(f"tempo:{mensagem}:{tempo_ms}")
        
        print(f"Tentativa realizada com {tempo_ms} ms")
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
        # Thread para receber mensagens TCP
        thread_tcp = threading.Thread(target=handle_messages)
        thread_tcp.daemon = True
        thread_tcp.start()
        
        # Thread para receber confirmações UDP
        thread_udp = threading.Thread(target=handle_udp)
        thread_udp.daemon = True
        thread_udp.start()
        
        # Thread para enviar tentativas
        thread_envio = threading.Thread(target=iniciar_envio)
        thread_envio.daemon = True
        thread_envio.start()
        
        # Manter o programa rodando
        thread_tcp.join()
        
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Cliente está sendo desligado...")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {str(e)}")
    finally:
        client.close()
        udp_client.close()
        print("[DESCONECTADO] Conexão encerrada.")

if __name__ == "__main__":
    iniciar()
