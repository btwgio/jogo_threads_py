import socket
import threading
import time
import json

SERVER_IP = "10.25.2.231"  # escuta todas interfaces
TCP_PORT = 5050
UDP_PORT = 5051
FORMAT = "utf-8"

# Senha secreta (fixa)
senha_secreta = "luke1999"

clientes = []  # lista nomes conectados
ranking = {}   # dict nome -> tentativas
mensagens_log = []  # histórico de mensagens e eventos
lock = threading.Lock()

# Thread para enviar dicas via UDP broadcast periodicamente
def enviar_dicas():
    dicas = [
        "Nasceu em 1999",
        "Seu gato se chama Luke",
        "Adora programação",
        "Ama café forte",
        "Seu time é o Flamengo"
    ]
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        for dica in dicas:
            msg = f"Dica: {dica}"
            udp.sendto(msg.encode(FORMAT), ('<broadcast>', UDP_PORT))
            time.sleep(5)

# Função que manipula um cliente TCP
def handle_cliente(conn, addr):
    global clientes, ranking, mensagens_log

    nome = None
    with conn:
        try:
            # Recebe o nome do cliente primeiro
            data = conn.recv(1024).decode(FORMAT)
            if data.startswith("name:"):
                nome = data.split("name:", 1)[1].strip()
                with lock:
                    if nome not in clientes:
                        clientes.append(nome)
                    if nome not in ranking:
                        ranking[nome] = 0
                mensagens_log.append(f"[CONEXÃO] {nome} ({addr}) conectou.")
            else:
                nome = f"{addr[0]}:{addr[1]}"
                with lock:
                    clientes.append(nome)
                    if nome not in ranking:
                        ranking[nome] = 0
                mensagens_log.append(f"[CONEXÃO] {nome} ({addr}) conectou.")

            while True:
                dados = conn.recv(1024).decode(FORMAT)
                if not dados:
                    break

                if dados.startswith("guess:"):
                    palpite = dados.split("guess:", 1)[1].strip()
                    with lock:
                        ranking[nome] += 1
                    if palpite == senha_secreta:
                        msg = f"{nome} acertou! Quebrando códigos hahaha 🎉"
                        mensagens_log.append(msg)
                        conn.send(msg.encode(FORMAT))
                    else:
                        msg = f"{nome} chutou que a senha era '{palpite}' mas errou! Não é hacker o suficiente! ahaha"
                        mensagens_log.append(msg)
                        conn.send(msg.encode(FORMAT))

                elif dados == "getranking":
                    with lock:
                        rnk_json = json.dumps(ranking)
                    conn.send(rnk_json.encode(FORMAT))

                else:
                    # Ignorar outras mensagens
                    pass

        except Exception as e:
            mensagens_log.append(f"[ERRO] {nome} desconectou com erro: {e}")
        finally:
            mensagens_log.append(f"[DESCONECTOU] {nome} saiu.")
            with lock:
                if nome in clientes:
                    clientes.remove(nome)

# Thread principal TCP que aceita conexões
def servidor_tcp():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind((SERVER_IP, TCP_PORT))
    tcp.listen()
    print(f"[TCP] Servidor TCP escutando em {SERVER_IP}:{TCP_PORT}")

    while True:
        conn, addr = tcp.accept()
        print(f"[TCP] Nova conexão de {addr}")
        thread = threading.Thread(target=handle_cliente, args=(conn, addr), daemon=True)
        thread.start()

# Interface para mostrar log e ranking (pode ser via Streamlit separado)
def servidor_interface():
    import streamlit as st
    st.set_page_config(page_title="Servidor Quebra de Senha", layout="wide")
    st.title("Servidor Quebra de Senha - Dicas + Ranking")

    while True:
        st.subheader("Mensagens do Jogo")
        with lock:
            for msg in mensagens_log[-20:]:
                st.write(msg)

        st.subheader("Ranking Atual")
        with lock:
            for jogador, tentativas in ranking.items():
                st.write(f"**{jogador}**: {tentativas} tentativas")

        time.sleep(3)
        st.experimental_rerun()

if __name__ == "__main__":
    # Start thread UDP para enviar dicas
    thread_dicas = threading.Thread(target=enviar_dicas, daemon=True)
    thread_dicas.start()

    # Start thread TCP para aceitar clientes
    thread_tcp = threading.Thread(target=servidor_tcp, daemon=True)
    thread_tcp.start()

    # Rodar interface servidor (streamlit)
    servidor_interface()
