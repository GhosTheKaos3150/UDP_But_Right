from encodings import utf_8
import sys, os
import socket, threading
from json import dumps, loads
from random import randint
from hashlib import md5

class Receptor(threading.Thread):

    def __init__(self, host='127.0.0.1', port=8080, sml_lose=False) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))

        self.sml_lose = sml_lose
        self.prev_ack = -1

        print('RECEPTOR CONECTADO')

    def run(self) -> None:
        inc_data = ''

        while True:
            data, addr = self.sock.recvfrom(1028)

            if self.sml_lose and randint(1, 100) <= 75:
                # Pacote se perdeu (95% de Perda)
                continue

            json = loads(data.decode('utf8'))

            print(json["ack"]) 

            if self.prev_ack != json["ack"]:
                if json["ack"] == -1:
                    print("ACK -1 Recebido. Encerrando...")
                    inc_data = inc_data.replace("_", " ")

                    fac = 0
                    while True:
                        if os.path.exists(f"./incoming_{fac}.txt"):
                            fac += 1
                        else:
                            break

                    with open(f"./incoming_{fac}.txt", "w") as img:
                        img.write(inc_data)
                    
                    inc_data = ""
                else:
                    if json["checksum"] != md5(json["msg"].encode("utf8")).hexdigest():
                        print("PACOTE CORROMPIDO")
                        continue
                    else:
                        if self.sml_lose and randint(1, 100) <= 75:
                            # Pacote se corrompeu (95% de Perda)
                            print("PACOTE CORROMPIDO")
                            continue

                    print(json["msg"])
                    inc_data += json["msg"]
            
            self.prev_ack = json["ack"]

            if self.sml_lose and randint(1, 100) <= 75:
                res = dumps({"ack": json["ack"], "checksum": md5("FINE".encode("utf8")).hexdigest()}).encode("utf-8")
            else:
                res = dumps({"ack": json["ack"], "checksum": md5("F1N3".encode("utf8")).hexdigest()}).encode("utf-8")

            if self.sml_lose and randint(1, 100) <= 75:
                # Pacote se perdeu (95% de Perda)
                continue

            self.sock.sendto(res, addr)
        
        # def findChecksum(msg, n):


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
