import socket
import threading
import time

# Configurações TCP
SERVER_IP = "26.103.100.48"
TCP_PORT = 5050
TCP_ADDR = (SERVER_IP, TCP_PORT)
FORMAT = "utf-8"

# Configurações UDP
UDP_PORT = 5051
UDP_ADDR = (SERVER_IP, UDP_PORT)

# Configuração dos sockets
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.bind(TCP_ADDR)

udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind(UDP_ADDR)

senha = "4321"

# Ranking
primeiro = None
segundo = None
terceiro = None

# Dicionário para armazenar nomes dos jogadores
nomes_jogadores = {}

# Lista de conexões ativas
conexoes_ativas = []

def tentativa_correta(tentativa):
    acertos = 0
    
    tamanho_comparacao = min(len(senha), len(tentativa))
    for i in range(tamanho_comparacao):
        if tentativa[i] == senha[i]:
            acertos += 1
    return acertos

def broadcast(mensagem):
    for conn in conexoes_ativas:
        try:
            conn.send(mensagem.encode(FORMAT))
        except:
            pass

def handle_client(conn, addr):
    global primeiro, segundo, terceiro, nomes_jogadores
    
    print(f"[NOVA CONEXÃO] um usuário se conectou pelo endereço {addr}")
    
    conexoes_ativas.append(conn)
    
    nome_jogador = f"Jogador-{addr[0]}"  
    
    if primeiro:
        nome_primeiro, ip_primeiro = primeiro
        conn.send(f"[INFO] Primeiro lugar já foi conquistado por {nome_primeiro} ({ip_primeiro})".encode(FORMAT))
    if segundo:
        nome_segundo, ip_segundo = segundo
        conn.send(f"[INFO] Segundo lugar já foi conquistado por {nome_segundo} ({ip_segundo})".encode(FORMAT))
    if terceiro:
        nome_terceiro, ip_terceiro = terceiro
        conn.send(f"[INFO] Terceiro lugar já foi conquistado por {nome_terceiro} ({ip_terceiro})".encode(FORMAT))
    
    while True:
        try:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:  
                print(f"[DESCONECTADO] {addr} - Mensagem vazia")
                break
            
            if msg.startswith("name:"):
                nome_jogador = msg[5:].strip()
                if not nome_jogador:  
                    nome_jogador = f"Jogador-{addr[0]}"
                
                nomes_jogadores[addr[0]] = nome_jogador
                print(f"[NOME] {addr[0]} se identificou como '{nome_jogador}'")
                
                conn.send(f"[INFO] Seu nome foi registrado como '{nome_jogador}'".encode(FORMAT))
                continue
                
            elif msg.startswith("guess:"):
                tentativa = msg[6:]
                
                if len(tentativa) != len(senha):
                    conn.send(f"Erro: A senha tem {len(senha)} dígitos. Sua tentativa tem {len(tentativa)} dígitos.".encode(FORMAT))
                else:
                    corretos = tentativa_correta(tentativa)
                    
                    if tentativa == senha:
                        ip = addr[0]
                        if (primeiro and ip == primeiro[1]) or (segundo and ip == segundo[1]) or (terceiro and ip == terceiro[1]):
                            conn.send("Você já acertou anteriormente!".encode(FORMAT))
                        else:
                            if primeiro is None:
                                primeiro = (nome_jogador, ip)
                                mensagem = f"Acertou! Você venceu e ficou em PRIMEIRO LUGAR!"
                                broadcast(f"[RANKING] {nome_jogador} de IP {ip} acertou a senha e conquistou o PRIMEIRO lugar!")
                            elif segundo is None:
                                segundo = (nome_jogador, ip)
                                mensagem = f"Acertou! Você venceu e ficou em SEGUNDO LUGAR!"
                                broadcast(f"[RANKING] {nome_jogador} de IP {ip} acertou a senha e conquistou o SEGUNDO lugar!")
                            elif terceiro is None:
                                terceiro = (nome_jogador, ip)
                                mensagem = f"Acertou! Você venceu e ficou em TERCEIRO LUGAR!"
                                broadcast(f"[RANKING] {nome_jogador} de IP {ip} acertou a senha e conquistou o TERCEIRO lugar!")
                            else:
                                mensagem = f"Acertou! Você venceu, mas o pódio já está completo!"
                                broadcast(f"[INFO] {nome_jogador} de IP {ip} acertou a senha, mas o pódio já está completo!")
                            
                            conn.send(mensagem.encode(FORMAT))
                            
                            print("\n[RANKING ATUAL]")
                            if primeiro:
                                nome_primeiro, ip_primeiro = primeiro
                                print(f"1º Lugar: {nome_primeiro} ({ip_primeiro})")
                            if segundo:
                                nome_segundo, ip_segundo = segundo
                                print(f"2º Lugar: {nome_segundo} ({ip_segundo})")
                            if terceiro:
                                nome_terceiro, ip_terceiro = terceiro
                                print(f"3º Lugar: {nome_terceiro} ({ip_terceiro})")
                            
                            ranking = "\n[RANKING ATUAL]"
                            if primeiro:
                                nome_primeiro, ip_primeiro = primeiro
                                ranking += f"\n1º Lugar: {nome_primeiro} ({ip_primeiro})"
                            if segundo:
                                nome_segundo, ip_segundo = segundo
                                ranking += f"\n2º Lugar: {nome_segundo} ({ip_segundo})"
                            if terceiro:
                                nome_terceiro, ip_terceiro = terceiro
                                ranking += f"\n3º Lugar: {nome_terceiro} ({ip_terceiro})"
                            
                            broadcast(ranking)
                    else:
                        conn.send(f"{corretos} dígitos certos".encode(FORMAT))
            else:
                conn.send("Formato inválido. Use 'guess:XXXX' para tentar a senha ou 'name:SeuNome' para definir seu nome.".encode(FORMAT))
                
        except Exception as e:
            print(f"[ERRO] {addr}: {str(e)}")
            print(f"[DESCONECTADO] {addr}")
            break
    
    if conn in conexoes_ativas:
        conexoes_ativas.remove(conn)

def handle_udp():
    print(f"[UDP] Servidor UDP iniciado em {SERVER_IP}:{UDP_PORT}")
    
    while True:
        try:
            data, addr = udp_server.recvfrom(1024)
            mensagem = data.decode(FORMAT)
            
            # Formato esperado: "tempo:XXXX:123" onde XXXX é a tentativa e 123 é o tempo em ms
            if mensagem.startswith("tempo:"):
                partes = mensagem.split(":")
                if len(partes) == 3:
                    tentativa = partes[1]
                    tempo_ms = partes[2]
                    ip_cliente = addr[0]
                    nome = nomes_jogadores.get(ip_cliente, f"Jogador-{ip_cliente}")
                    
                    print(f"[UDP] {nome} ({ip_cliente}): Tentativa '{tentativa}' realizada com {tempo_ms} ms")
                    
                    # Enviar confirmação de volta para o cliente
                    udp_server.sendto(f"tempo_recebido:{tempo_ms}".encode(FORMAT), addr)
                
        except Exception as e:
            print(f"[UDP] Erro: {str(e)}")

def start():
    print("[INICIANDO] Servidor iniciado")
    tcp_server.listen()
    print(f"[ESCUTANDO] Servidor TCP está escutando em {SERVER_IP}:{TCP_PORT}")
    print(f"[ESCUTANDO] Servidor UDP está escutando em {SERVER_IP}:{UDP_PORT}")
    
    # Iniciar thread para o servidor UDP
    udp_thread = threading.Thread(target=handle_udp)
    udp_thread.daemon = True
    udp_thread.start()
    
    try:
        while True:
            conn, addr = tcp_server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("[ENCERRANDO] Servidor está sendo desligado")
        tcp_server.close()
        udp_server.close()
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        tcp_server.close()
        udp_server.close()

if __name__ == "__main__":
    start()
