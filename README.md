# Jogo: Quebrando Senhas com TCP e UDP (Simulação de Força Bruta)

Este projeto foi desenvolvido como atividade prática da disciplina de **Desenvolvimento de Sistemas Distribuídos** no **IFRN**. O objetivo é aplicar os conceitos de comunicação via rede usando os protocolos **TCP** e **UDP**, além de simular uma situação real de segurança: uma tentativa de ataque por força bruta para adivinhar senhas.

A linguagem utilizada é o **Python**, devido à sua simplicidade e ao suporte robusto para manipulação de sockets e threads.


## Sobre o Jogo

Neste jogo, os clientes tentam adivinhar uma senha secreta de 4 dígitos gerada no servidor. A ideia é simular uma tentativa de ataque por força bruta, onde o cliente testa diversas combinações até descobrir a correta.

Cada tentativa é enviada ao servidor via protocolo **TCP**, e o servidor responde com dicas (quantos dígitos estão corretos e na posição certa).

O servidor mantém um pódio com os três primeiros jogadores que acertarem a senha, e envia atualizações do ranking para todos os clientes conectados.


## Tecnologias Utilizadas

- Python 3.10+
- socket (TCP e UDP)
- threading (execução paralela)

## Como Executar o Projeto

1. Clone o repositório:

```bash
git clone https://github.com/btwgio/jogo_threads_py
```
2. Inicie o servidor (em uma máquina ou terminal separado):
```bash
python servidor.py
```
3. Em outro terminal ou máquina, execute o cliente:
```bash
python cliente.py
```
