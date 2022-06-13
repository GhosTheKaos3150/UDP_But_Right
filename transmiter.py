from dataclasses import replace
from operator import le
from textwrap import wrap
from json import dumps, loads
import socket,threading
from hashlib import md5

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# msg = 'OLÁ MUNDO - RECV'.encode('utf8')
# sock.sendto(msg, ('127.0.0.1', 8080))

# data, addr = sock.recvfrom(4096)
# print(str(data.decode('utf8')))

# sock.close()

class Transmissor(threading.Thread):
    
    def __init__(self, msg: str) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.01)

        self.msg = msg.replace(" ", "_")
        print("Transmissor Iniciado".upper())

    def run(self) -> None:
        # msg = self.separate_as_binary(self.msg)
        factor = 4
        while True:
            
            msg = wrap(self.msg, round(len(self.msg)/factor))

            if len(msg[0].encode("utf8")) >= 1024:
                factor += factor
            else:
                break

        print(f"Mensagem dividida em {factor} partes!")
        ack = 0

        for m in msg:
            while True:
                try:
                    sd_data = dumps({"ack": ack, "msg": m, "checksum": md5(m.encode("utf8")).hexdigest()}).encode("utf8")

                    self.sock.sendto(sd_data, ('127.0.0.1', 8080))
                    data, addr = self.sock.recvfrom(1028)

                    json = loads(data.decode("utf8"))
                    if json["ack"] != ack:
                        print("ACK conflitante. Reenviando...")
                        continue
                        
                    if json["checksum"] != md5("FINE".encode("utf8")).hexdigest():
                        print("PACOTE CORROMPIDO. Reenviando")
                        continue

                    print("ACK Recebido. Enviando Prox. Pacote")
                except socket.timeout:
                    print("Timeout. Reenviando...")
                    continue
                
                if ack == 0:
                    ack = 1
                else:
                    ack = 0
                
                break
        
        while True:
            try:
                sd_data = dumps({"ack": -1}).encode("utf8")

                self.sock.sendto(sd_data, ('127.0.0.1', 8080))
                data, addr = self.sock.recvfrom(1028)

                json = loads(data.decode("utf8"))

                if json["ack"] == -1:
                    break
            except:
                print("Finalização não Retornada. Reenviando...")
                continue

        self.sock.close()
    
    def separate_as_binary(self, msg):
        bin_msg_array = []
        msg_array = wrap(msg, round(len(msg)/4))

        for ma in msg_array:
            bin_msg_array.append(ma.encode('utf8'))
        
        return bin_msg_array
    

if __name__ == "__main__":
    trns = Transmissor(str(open("./src/Lorem Ipsum.txt", "r").read()))
    trns.run()
    