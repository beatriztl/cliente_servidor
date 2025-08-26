import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

FORMATO_CODIFICACAO = 'utf-8'

# ------------------ Comunicação com servidor de registro ------------------
class Registro:
    def __init__(self, hospedeiro, porta):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((hospedeiro, porta))
        self.r = self.sock.makefile('r', encoding=FORMATO_CODIFICACAO)
        self.w = self.sock.makefile('w', encoding=FORMATO_CODIFICACAO)

    def registrar(self, apelido, ip, porta):
        self.w.write(f'REGISTRAR {apelido} {ip} {porta}\n')
        self.w.flush()
        return self.r.readline().strip() == 'OK'

    def listar(self):
        self.w.write('LISTAR\n')
        self.w.flush()
        linha = self.r.readline().strip()
        usuarios = []
        if linha.startswith('USUARIOS'):
            while True:
                l = self.r.readline().strip()
                if l == 'END':
                    break
                # Espera 'USUARIO ap ip pt' (singular) — compatível com o servidor corrigido
                if l.startswith('USUARIO'):
                    _, ap, ip, pt = l.split()
                    usuarios.append((ap, ip, int(pt)))
        return usuarios

    def resolver(self, apelido):
        self.w.write(f'RETORNAR {apelido}\n')
        self.w.flush()
        resp = self.r.readline().strip()
        if resp.startswith('ENCONTRADO'):
            _, ip, pt = resp.split()
            return ip, int(pt)
        return None

    def cancelar_registro(self, apelido):
        self.w.write(f'CANCELAR_REGISTRO {apelido}\n')
        self.w.flush()
        self.r.readline()
        try:
            self.r.close()
            self.w.close()
            self.sock.close()
        except:
            pass

# ------------------ Sessão de Chat P2P ------------------
class SessaoChat:
    def __init__(self, apelido_local, apelido_remoto, sock, interface):
        self.apelido_local = apelido_local
        self.apelido_remoto = apelido_remoto
        self.sock = sock
        self.interface = interface
        self.r = sock.makefile('r', encoding=FORMATO_CODIFICACAO)
        self.w = sock.makefile('w', encoding=FORMATO_CODIFICACAO)

        self.receber_ativo = True
        self.viva = True

        self.janela = tk.Toplevel()
        self.janela.title(f"Chat [{apelido_local} ↔ {apelido_remoto}]")
        self.texto = scrolledtext.ScrolledText(self.janela, width=50, height=15, state=tk.DISABLED)
        self.texto.pack(padx=10, pady=10)
        self.entrada = tk.Entry(self.janela, width=40)
        self.entrada.pack(side=tk.LEFT, padx=10, pady=5)
        btn = tk.Button(self.janela, text="Enviar", command=self._enviar)
        btn.pack(side=tk.LEFT, padx=5)

        self.entrada.bind("<Return>", lambda event: self._enviar())
        self.janela.protocol("WM_DELETE_WINDOW", self.fechar_janela)

        threading.Thread(target=self._loop_receber, daemon=True).start()

    def fechar_janela(self):
        self.receber_ativo = False
        self.viva = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)  # força finalização da conexão
            self.sock.close()
        except:
            pass
        try:
            if self.apelido_remoto in self.interface.sessoes:
                del self.interface.sessoes[self.apelido_remoto]
        except:
            pass
        self.janela.destroy()


    def _loop_receber(self):
        while self.receber_ativo:
            try:
                linha = self.r.readline()
                if linha == '':
                    break  # conexão encerrada
                msg = linha.strip()
                if msg.startswith("MSG "):
                    conteudo = msg[4:]
                    self._mostrar(f"[{self.apelido_remoto}]: {conteudo}")
                else:
                    self._mostrar(msg)
            except:
                break
        self.viva = False
        self._mostrar("[Conexão encerrada]" + "\n" +self.apelido_remoto + " desconectou.")


    def _mostrar(self, msg):
        def inserir():
            if self.texto.winfo_exists():
                self.texto.config(state=tk.NORMAL)
                self.texto.insert(tk.END, msg + "\n")
                self.texto.see(tk.END)
                self.texto.config(state=tk.DISABLED)
        self.texto.after(0, inserir)

    def _enviar(self):
        msg = self.entrada.get().strip()
        if msg and self.viva:
            try:
                self.w.write(f"MSG {msg}\n")
                self.w.flush()
                self._mostrar(f"[Eu]: {msg}")
            except:
                self.viva = False
                self._mostrar("[Falha ao enviar]")
        self.entrada.delete(0, tk.END)

# ------------------ Cliente P2P ---------------------
class ClienteInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente P2P")

        tk.Label(root, text="Servidor IP:").grid(row=0, column=0)
        self.servidor_ip = tk.Entry(root)
        self.servidor_ip.grid(row=0, column=1)

        tk.Label(root, text="Apelido:").grid(row=1, column=0)
        self.apelido = tk.Entry(root)
        self.apelido.grid(row=1, column=1)

        self.btn_conectar = tk.Button(root, text="Conectar", command=self.conectar)
        self.btn_conectar.grid(row=2, column=0, columnspan=2, pady=5)

        self.lista = tk.Listbox(root, width=40)
        self.lista.grid(row=3, column=0, columnspan=2, pady=5)

        self.btn_atualizar = tk.Button(root, text="Atualizar lista", command=self.atualizar_lista, state=tk.DISABLED)
        self.btn_atualizar.grid(row=4, column=0, pady=5)
        self.btn_chat = tk.Button(root, text="Iniciar Chat", command=self.iniciar_chat, state=tk.DISABLED)
        self.btn_chat.grid(row=4, column=1, pady=5)

        self.reg = None
        self.listen_sock = None
        self.sessoes = {}
        self.apelido_local = None

        # Encerramento limpo da aplicação
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_app)

    def conectar(self):
        ip_serv = self.servidor_ip.get().strip()
        apelido = self.apelido.get().strip()
        if not ip_serv or not apelido:
            messagebox.showerror("Erro", "Informe IP do servidor e apelido")
            return

        # abre servidor P2P local
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.bind((socket.gethostbyname(socket.gethostname()), 0))
        self.listen_sock.listen()
        self.p2p_port = self.listen_sock.getsockname()[1]

        # conecta no servidor central
        try:
            self.reg = Registro(ip_serv, 1998)
            ok = self.reg.registrar(apelido, socket.gethostbyname(socket.gethostname()), self.p2p_port)
            if not ok:
                raise Exception("Falha no registro")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {e}")
            try:
                self.listen_sock.close()
            except:
                pass
            self.listen_sock = None
            return

        self.apelido_local = apelido
        self.btn_atualizar.config(state=tk.NORMAL)
        self.btn_chat.config(state=tk.NORMAL)
        self.btn_conectar.config(state=tk.DISABLED)
        threading.Thread(target=self._aceitar_conexoes, daemon=True).start()
        self.atualizar_lista()
        messagebox.showinfo("Conectado", f"Registrado como {apelido}")

    def atualizar_lista(self):
        if not self.reg:
            return
        self.lista.delete(0, tk.END)
        usuarios = self.reg.listar()
        for ap, ip, pt in usuarios:
            if ap != self.apelido_local:
                self.lista.insert(tk.END, ap)

    def iniciar_chat(self):
        if not self.reg:
            return
        sel = self.lista.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário")
            return
        alvo = self.lista.get(sel[0])
        if alvo in self.sessoes:
            messagebox.showinfo("Info", f"Já existe uma janela de chat com {alvo}")
            return
        ip_port = self.reg.resolver(alvo)
        if not ip_port:
            messagebox.showerror("Erro", "Usuário não encontrado")
            return
        ip, porta = ip_port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, porta))
            w = sock.makefile('w', encoding=FORMATO_CODIFICACAO)
            w.write(f"HELLO {self.apelido_local}\n")
            w.flush()
            sess = SessaoChat(self.apelido_local, alvo, sock, self)
            self.sessoes[alvo] = sess
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar a {alvo}: {e}")

    def _aceitar_conexoes(self):
        while True:
            try:
                conn, addr = self.listen_sock.accept()
                r = conn.makefile('r', encoding=FORMATO_CODIFICACAO)
                linha = r.readline().strip()
                if not linha.startswith("HELLO "):
                    conn.close()
                    continue
                apelido_remoto = linha.split()[1]
                if apelido_remoto not in self.sessoes:
                    sess = SessaoChat(self.apelido_local, apelido_remoto, conn, self)
                    self.sessoes[apelido_remoto] = sess
                else:
                    # Já existe: fecha conexão duplicada
                    try:
                        conn.close()
                    except:
                        pass
            except:
                break

    def fechar_app(self):
        # Cancela registro e fecha sockets
        try:
            if self.reg and self.apelido_local:
                self.reg.cancelar_registro(self.apelido_local)
        except:
            pass
        try:
            if self.listen_sock:
                self.listen_sock.close()
        except:
            pass
        # Fecha janelas de chat
        for sess in list(self.sessoes.values()):
            try:
                sess.fechar_janela()
            except:
                pass
        self.root.destroy()

# ------------------ Main ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteInterface(root)
    root.mainloop()
