import cv2
from pyzbar import pyzbar

def scan_crypto_qrcodes():
    # Inicializa a captura de vídeo (0 é geralmente a webcam integrada)
    cap = cv2.VideoCapture(0)
    
    # Conjunto para armazenar hashes já capturados e evitar duplicatas rápidas
    captured_hashes = set()

    print("Scanning for Crypto Hashes... Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detecta e decodifica QR codes no frame atual
            qrcodes = pyzbar.decode(frame)

            for qr in qrcodes:
                # Decodifica os dados binários para string
                tx_hash = qr.data.decode('utf-8')
                
                # Se for um hash novo, processamos
                if tx_hash not in captured_hashes:
                    print(f"New Hash Detected: {tx_hash}")
                    captured_hashes.add(tx_hash)
                    
                    # Opcional: Salvar em um arquivo txt imediatamente
                    with open("captured_hashes.txt", "a") as f:
                        f.write(f"{tx_hash}\n")

                # Desenha um retângulo ao redor do QR Code na tela
                (x, y, w, h) = qr.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "HASH DETECTED", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Mostra o feedback da câmera
            cv2.imshow("Crypto QR Scanner", frame)

            # Sai se pressionar a tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_crypto_qrcodes()