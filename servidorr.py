import socket
import threading
import time

SERVER_IP = "10.25.2.228"
PORT = 5050
ADDR = (SERVER_IP, PORT)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

senha = "4321"

# Estrutura para armazenar os vencedores (nome, IP)
primeiro = None
segundo = None
terceiro = None

# Dicionário para armazenar os nomes dos jogadores por IP
nomes_jogadores = {}

# Lista para armazenar todas as conexões ativas
conexoes_ativas = []

def tentativa_correta(tentativa):
    acertos = 0
    # Verificar se a tentativa tem o mesmo tamanho da senha
    tamanho_comparacao = min(len(senha), len(tentativa))
    for i in range(tamanho_comparacao):
        if tentativa[i] == senha[i]:
            acertos += 1
    return acertos

# Função para enviar mensagem para todos os clientes conectados
def broadcast(mensagem):
    for conn in conexoes_ativas:
        try:
            conn.send(mensagem.encode(FORMAT))
        except:
            # Se não conseguir enviar, provavelmente o cliente desconectou
            pass

def handle_client(conn, addr):
    global primeiro, segundo, terceiro, nomes_jogadores
    
    print(f"[NOVA CONEXÃO] um usuário se conectou pelo endereço {addr}")
    
    # Adicionar conexão à lista de conexões ativas
    conexoes_ativas.append(conn)
    
    # Nome do jogador (será definido quando o cliente enviar)
    nome_jogador = f"Jogador-{addr[0]}"  # Nome padrão até que o cliente envie seu nome
    
    # Informar ao cliente sobre o estado atual do jogo
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
            if not msg:  # Se a mensagem estiver vazia, o cliente desconectou
                print(f"[DESCONECTADO] {addr} - Mensagem vazia")
                break
            
            # Processar mensagem de nome
            if msg.startswith("name:"):
                nome_jogador = msg[5:].strip()
                if not nome_jogador:  # Se o nome estiver vazio, usar o padrão
                    nome_jogador = f"Jogador-{addr[0]}"
                
                # Armazenar o nome do jogador
                nomes_jogadores[addr[0]] = nome_jogador
                print(f"[NOME] {addr[0]} se identificou como '{nome_jogador}'")
                
                # Informar ao jogador que seu nome foi registrado
                conn.send(f"[INFO] Seu nome foi registrado como '{nome_jogador}'".encode(FORMAT))
                continue
                
            # Processar tentativa de senha
            elif msg.startswith("guess:"):
                tentativa = msg[6:]
                
                # Verificar se a tentativa tem o tamanho correto
                if len(tentativa) != len(senha):
                    conn.send(f"Erro: A senha tem {len(senha)} dígitos. Sua tentativa tem {len(tentativa)} dígitos.".encode(FORMAT))
                else:
                    corretos = tentativa_correta(tentativa)
                    
                    if tentativa == senha:
                        # Verificar se este IP já está no ranking
                        ip = addr[0]
                        if (primeiro and ip == primeiro[1]) or (segundo and ip == segundo[1]) or (terceiro and ip == terceiro[1]):
                            conn.send("Você já acertou anteriormente!".encode(FORMAT))
                        else:
                            # Atribuir posição no ranking
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
                            
                            # Mostrar o ranking atual
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
                            
                            # Enviar ranking atualizado para todos
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
    
    # Remover conexão da lista de conexões ativas
    if conn in conexoes_ativas:
        conexoes_ativas.remove(conn)

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