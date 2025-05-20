import streamlit as st
import socket
import threading
import json
from collections import deque

SERVER_IP = "10.25.2.231"  # IP do servidor (coloque o correto)
TCP_PORT = 5050
UDP_PORT = 5051
FORMAT = "utf-8"

# Mensagens do servidor TCP
tcp_msgs = deque(maxlen=100)
# Mensagens recebidas via UDP (dicas)
udp_msgs = deque(maxlen=100)
# Ranking recebido do servidor
ranking = {}

# Socket TCP para o jogo
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_client.connect((SERVER_IP, TCP_PORT))

# Socket UDP para receber dicas
udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    udp_client.bind(("", UDP_PORT))
except Exception as e:
    st.warning(f"Erro ao bindar UDP (pode estar em uso): {e}")

def escutar_tcp():
    while True:
        try:
            msg = tcp_client.recv(1024).decode(FORMAT)
            if msg:
                try:
                    r = json.loads(msg)
                    if isinstance(r, dict):
                        global ranking
                        ranking = r
                        continue
                except:
                    pass
                tcp_msgs.append(f"[Servidor] {msg}")
            else:
                tcp_msgs.append("[Servidor] Conexão encerrada.")
                break
        except Exception as e:
            tcp_msgs.append(f"[Erro TCP] {e}")
            break

def escutar_udp():
    while True:
        try:
            msg, _ = udp_client.recvfrom(1024)
            udp_msgs.append(f"[Dica] {msg.decode(FORMAT)}")
        except Exception as e:
            udp_msgs.append(f"[Erro UDP] {e}")
            break

def enviar(msg):
    try:
        tcp_client.send(msg.encode(FORMAT))
    except Exception as e:
        tcp_msgs.append(f"[Erro TCP] {e}")

threading.Thread(target=escutar_tcp, daemon=True).start()
threading.Thread(target=escutar_udp, daemon=True).start()

st.set_page_config(page_title="Quebra de Senha - Hacker Game", layout="centered")
st.title("💻 Quebra de Senha - Hacker Game")

nome = st.text_input("Digite seu nome:", max_chars=20, key="nome")
palpite = st.text_input("Digite seu palpite de senha:", max_chars=50, key="palpite")

if st.button("Entrar / Registrar"):
    if nome.strip() == "":
        st.warning("Por favor digite seu nome para começar.")
    else:
        enviar(f"name:{nome.strip()}")
        st.success(f"Olá, {nome.strip()}! Você está conectado.")

if st.button("Enviar Palpite"):
    if nome.strip() == "":
        st.warning("Por favor digite seu nome antes de enviar o palpite.")
    elif palpite.strip() == "":
        st.warning("Digite um palpite antes de enviar.")
    else:
        enviar(f"guess:{palpite.strip()}")
        st.success(f"Palpite '{palpite.strip()}' enviado!")

if st.button("Ver Ranking Atual"):
    enviar("getranking")

st.subheader("Mensagens do Servidor (TCP)")
for m in list(tcp_msgs)[-20:]:
    if "errou" in m.lower() or "erro" in m.lower():
        st.error(m)
    elif "acertou" in m.lower():
        st.success(m)
    else:
        st.info(m)

st.subheader("Dicas Recebidas (UDP)")
for d in list(udp_msgs)[-10:]:
    st.info(d)

st.subheader("Ranking Atual")
if ranking:
    for jogador, tentativas in ranking.items():
        st.write(f"**{jogador}**: {tentativas} tentativas")
else:
    st.write("Nenhum ranking disponível. Peça para atualizar clicando no botão acima.")
