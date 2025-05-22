import socket
import threading

SERVER_IP = "172.21.224.1"
PORT = 5050
ADDR = (SERVER_IP, PORT)
FORMAT = "utf-8"

# configurações do socket TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# configurações do socket UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UDP_PORT_PADRAO = 5051
udp_clientes = set()

senha = "4321"

primeiro = None
segundo = None
terceiro = None

nomes_jogadores = {}
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

def udp_broadcast(mensagem):
    for ip, porta in udp_clientes:
        try:
            udp_socket.sendto(mensagem.encode(FORMAT), (ip, porta))
        except:
            pass

def handle_client(conn, addr):
    global primeiro, segundo, terceiro, nomes_jogadores

    print(f"[NOVA CONEXÃO] um usuário se conectou pelo endereço {addr}")
    conexoes_ativas.append(conn)

    nome_jogador = f"Jogador-{addr[0]}"
    porta_udp = UDP_PORT_PADRAO  # fallback

    while True:
        try:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                print(f"[DESCONECTADO] {addr} - Mensagem vazia")
                break

            if msg.startswith("name:"):
                partes = msg[5:].split(";")
                nome_jogador = partes[0].strip()

                if not nome_jogador:
                    nome_jogador = f"Jogador-{addr[0]}"
                nomes_jogadores[addr[0]] = nome_jogador

                if len(partes) > 1 and partes[1].startswith("udp:"):
                    porta_udp = int(partes[1][4:])
                udp_clientes.add((addr[0], porta_udp))

                print(f"[NOME] {addr[0]} se identificou como '{nome_jogador}' (UDP: {porta_udp})")
                conn.send(f"[INFO] Seu nome foi registrado como '{nome_jogador}'".encode(FORMAT))
                udp_broadcast(f"[NOME] {addr[0]} se identificou como '{nome_jogador}'")
                udp_broadcast(f"[CONEXÕES ATIVAS] {len(conexoes_ativas)}")
                continue

            elif msg.startswith("guess:"):
                tentativa = msg[6:]

                if len(tentativa) != len(senha):
                    conn.send(f"Erro: A senha tem {len(senha)} dígitos. Sua tentativa tem {len(tentativa)} dígitos.".encode(FORMAT))
                else:
                    corretos = tentativa_correta(tentativa)
                    ip = addr[0]

                    if tentativa == senha:
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

                            ranking = "\n[RANKING ATUAL]"
                            if primeiro:
                                ranking += f"\n1º Lugar: {primeiro[0]} ({primeiro[1]})"
                            if segundo:
                                ranking += f"\n2º Lugar: {segundo[0]} ({segundo[1]})"
                            if terceiro:
                                ranking += f"\n3º Lugar: {terceiro[0]} ({terceiro[1]})"
                            broadcast(ranking)
                    else:
                        conn.send(f"{corretos} dígitos certos".encode(FORMAT))
            else:
                conn.send("Formato inválido. Use 'guess:XXXX' ou 'name:SeuNome'.".encode(FORMAT))

        except Exception as e:
            print(f"[ERRO] {addr}: {str(e)}")
            break

    if conn in conexoes_ativas:
        conexoes_ativas.remove(conn)
    udp_broadcast(f"[DESCONECTADO] {addr[0]} saiu. Conexões ativas: {len(conexoes_ativas)}")
    conn.close()

def start():
    print("[INICIANDO] Servidor iniciado")
    server.listen()
    print(f"[ESCUTANDO] Servidor está escutando em {SERVER_IP}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("[ENCERRANDO] Servidor está sendo desligado")
        server.close()
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        server.close()

if __name__ == "__main__":
    start()
