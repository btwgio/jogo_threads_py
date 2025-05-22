import socket
import threading

SERVER_IP = "10.25.1.69"
PORT = 5050
ADDR = (SERVER_IP, PORT)
FORMAT = "utf-8"

# configurações do socket TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# configurações do socket UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
    udp_broadcast(f"[CONEXÕES ATIVAS] {len(conexoes_ativas)}")

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
                udp_broadcast(f"[NOME] {addr[0]} se identificou como '{nome_jogador}'")
                continue

            elif msg.startswith("udp_port:"):
                porta_udp = int(msg.split(":")[1])
                udp_clientes.add((addr[0], porta_udp))
                print(f"[UDP] Registrado {addr[0]}:{porta_udp}")
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
    udp_broadcast(f"[DESCONECTADO] {addr[0]} saiu. Conexões ativas: {len(conexoes_ativas)}")

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
