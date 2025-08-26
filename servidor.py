import socket
import threading

SERVIDOR_CENTRAL = socket.gethostbyname(socket.gethostname())
PORTA = 1998
SERVIDOR_PORTA = (SERVIDOR_CENTRAL, PORTA)
FORMATO_CODIFICACAO = 'utf-8'

# Tabela de usuários: apelido -> (ip, porta)
usuarios = {}
lock = threading.Lock()

def tratar_cliente(conexao, servidor_porta):
    print(f"[CONECTADO] {servidor_porta}")
    r = conexao.makefile('r', encoding=FORMATO_CODIFICACAO)
    w = conexao.makefile('w', encoding=FORMATO_CODIFICACAO)
    try:
        for linha in r:
            partes = linha.strip().split()
            if not partes:
                continue
            comando = partes[0].upper()

            if comando == 'REGISTRAR' and len(partes) == 4:
                apelido, ip, porta = partes[1], partes[2], int(partes[3])
                with lock:
                    usuarios[apelido] = (ip, porta)
                print(f"[REGISTRAR] {apelido} -> {ip}:{porta}")
                w.write('OK\n'); w.flush()

            elif comando == 'LISTAR':
                with lock:
                    itens = list(usuarios.items())
                w.write(f'USUARIOS {len(itens)}\n')
               
                for ap, (ip, pt) in itens:
                    w.write(f'USUARIO {ap} {ip} {pt}\n')
                w.write('END\n'); w.flush()

            elif comando == 'RETORNAR' and len(partes) == 2:
                ap = partes[1]
                with lock:
                    dados = usuarios.get(ap)
                if dados:
                    ip, pt = dados
                    w.write(f'ENCONTRADO {ip} {pt}\n')
                else:
                    w.write('NAO ENCONTRADO\n')
                w.flush()

            elif comando == 'CANCELAR_REGISTRO' and len(partes) == 2:
                ap = partes[1]
                with lock:
                    usuarios.pop(ap, None)
                print(f"[CANCELAR_REGISTRO] {ap}")
                w.write('OK\n'); w.flush()

            else:
                w.write('ERROR\n'); w.flush()
    except Exception as e:
        print(f"[ERRO] {servidor_porta} -> {e}")
    finally:
        conexao.close()
        print(f"[DESCONECTADO] {servidor_porta}")

# Função principal para iniciar o servidor
def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(SERVIDOR_PORTA)
    servidor.listen()
    print(f'[REGISTRO] Servidor em {SERVIDOR_CENTRAL}:{PORTA}')
    while True:
        c, a = servidor.accept()
        threading.Thread(target=tratar_cliente, args=(c, a), daemon=True).start()

if __name__ == '__main__':
    main()
