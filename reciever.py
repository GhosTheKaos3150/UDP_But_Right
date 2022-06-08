from encodings import utf_8
import sys
import socket, threading
from json import dumps, loads
from random import randint

class Receptor(threading.Thread):

    def __init__(self, host='127.0.0.1', port=8080, sml_lose=False) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))

        self.sml_lose = sml_lose

        print('RECEPTOR CONECTADO')

    def run(self) -> None:
        inc_data = ''

        while True:
            data, addr = self.sock.recvfrom(1028)

            if self.sml_lose and randint(1, 100) <= 95:
                # Pacote se perdeu (95% de Perda)
                continue

            json = loads(data.decode('utf8'))

            print(json["ack"])

            if json["ack"] == -1:
                print("ACK -1 Recebido. Encerrando...")
                inc_data = inc_data.replace("_", " ")

                with open("./src/incoming.txt", "w") as img:
                    img.write(inc_data)
            else:
                print(json["msg"])
                inc_data += json["msg"]

            res = dumps({"ack": json["ack"]}).encode("utf-8")

            self.sock.sendto(res, addr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["True", "true", "False", "false"]:
            sml_lose = sys.argv[1].capitalize()
        else:
            sml_lose = False
    else:
        sml_lose = False

    print(f"Iniciando com Lose Artificial: {sml_lose}")

    recv = Receptor(sml_lose=sml_lose)
    recv.run()
