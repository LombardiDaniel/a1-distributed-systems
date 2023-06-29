import threading

import cv2
import numpy as np
import zmq


def publisher(endereco):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:" + endereco)  # Define o endereço para publicação

    
    #operacao para abrir o video e enviar os frames para o 'cliente'
    webcam = cv2.VideoCapture(0)
    while webcam.isOpened():
        validacao, frame = webcam.read()
        if not validacao:
            break
        encoded_frame = cv2.imencode('.webp', frame)[1]  # Codifica o frame como 
        
        socket.send(encoded_frame.tobytes()) #envia o frame em bytes
        
        cv2.imshow("Enviando video 1...", frame) #exibe o frame enviado (video)
        if cv2.waitKey(5) == 27: #pressiona esc para sair
            break
    webcam.release() #encerra conexao com a webcam
    cv2.destroyAllWindows()

def subscriber(endereco):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:" + endereco)  # Conecta ao endereço do publicador
    socket.setsockopt(zmq.SUBSCRIBE, b"")  # Subscreve em todos os tópicos

    while True:
        frame_bytes = socket.recv()
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)# Converte os bytes recebidos para um array NumPy
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)  # Decodifica o array para obter o frame
        
        cv2.imshow("Recebendo video 2...", frame) #exibe o frame recebido
        if cv2.waitKey(5) == 27: #pressiona esc para sair
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
#    my_port = input("Insira seu endereco: ")
#    other_port = input("Insira o endereco de destino: ")
    my_port, other_port = '6666', '5555'

    pub_thread = threading.Thread(target=publisher, args=(my_port,))
    sub_thread = threading.Thread(target=subscriber, args=(other_port,))
    pub_thread.start() #inicia a thread
    sub_thread.start()
