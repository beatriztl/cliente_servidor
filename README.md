# Chat Simples com Sockets TCP e Tkinter
### Trabalho Prático da disciplina de Redes de Computadores 1

## 📖 Sobre o Projeto

Este projeto foi desenvolvido com o objetivo de exercitar a programação para comunicação em redes de computadores utilizando Sockets. Trata-se de uma aplicação de chat simples composta por dois módulos principais: o servidor (`servidor.py`) e o cliente (`cliente.py`).

Ambos os módulos foram implementados em **Python**, utilizando a biblioteca `socket` para a comunicação TCP e a biblioteca `Tkinter` para a construção da interface gráfica do cliente.

O uso de sockets TCP possibilita a comunicação confiável entre processos em diferentes máquinas da rede, estabelecendo um canal de troca de mensagens que garante a ordem e a entrega dos dados.

## 🏗️ Arquitetura da Aplicação

A aplicação segue o modelo cliente-servidor, onde as responsabilidades são divididas da seguinte forma:

* **Servidor (`servidor.py`)**:
    * Atua como intermediário da comunicação entre todos os clientes.
    * Gerencia os usuários conectados, armazenando uma lista com suas informações (apelido, endereço IP e porta).
    * Recebe mensagens de um cliente e as repassa para o destinatário correto.

* **Cliente (`cliente.py`)**:
    * Conecta-se ao servidor para poder interagir com outros usuários.
    * Possui uma interface gráfica (GUI) para que o usuário possa se conectar, ver a lista de usuários online e trocar mensagens.
    * Envia comandos para o servidor para registrar-se, listar, buscar ou remover usuários.

## ✨ Funcionalidades

* **Comunicação em Tempo Real**: Troca de mensagens instantâneas entre dois clientes conectados.
* **Gerenciamento Centralizado**: O servidor gerencia a lista de usuários ativos.
* **Interface Gráfica Intuitiva**: Interface construída com Tkinter para facilitar a interação do usuário.
* **Identificação de Mensagens**: Cada mensagem é identificada com o apelido do remetente e do destinatário.

## 🚀 Como Usar

Para validar e utilizar a aplicação, siga os passos abaixo.

### Pré-requisitos

* Python 3.x
* A biblioteca Tkinter (geralmente já vem instalada com o Python no Windows. Em sistemas baseados em Debian/Ubuntu, pode ser instalada com `sudo apt-get install python3-tk`).

### Execução

1.  **Inicie o Servidor**
    Execute o programa `servidor.py` em um terminal. Ele ficará aguardando por conexões de clientes.
    ```bash
    python servidor.py
    ```

2.  **Execute o Cliente**
    Em outro terminal (no mesmo computador ou em outra máquina na mesma rede), execute o programa `cliente.py`.
    ```bash
    python cliente.py
    ```

3.  **Conecte-se ao Chat**
    * Ao iniciar o cliente, uma janela gráfica será aberta.
    * Informe o **endereço IP do servidor** (se estiver na mesma máquina, use `127.0.0.1`).
    * Escolha um **Apelido** (nome de usuário).
    * Clique no botão **“Conectar”**.

4.  **Inicie uma Conversa**
    * Após se conectar, clique em **“Atualizar Lista”** para ver os usuários online.
    * Selecione um usuário da lista.
    * Clique em **“Iniciar Chat”** para abrir a janela de bate-papo.

5.  **Envie Mensagens**
    * Na janela de conversa, digite sua mensagem no campo de texto inferior e clique em **“Enviar”**.
    * O histórico da conversa será exibido no painel superior.

6.  **Encerre a Sessão**
    * Para encerrar o chat ou a conexão com o servidor, basta fechar a janela da aplicação clicando no **“X”**.

## 🏁 Conclusão

A aplicação demonstra de forma prática como funciona a comunicação em redes utilizando sockets TCP em Python. O servidor centraliza o gerenciamento de usuários e o encaminhamento de mensagens, enquanto os clientes interagem por meio de uma interface gráfica Tkinter, tornando a experiência mais intuitiva e próxima de aplicativos reais de mensagens instantâneas.

## 👨‍💻 Autores


[<img loading="lazy" src="https://avatars.githubusercontent.com/u/130513027?v=4" width="75">](https://github.com/beatriztl)

