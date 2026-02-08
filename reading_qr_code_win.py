import cv2
import binascii
from qreader import QReader
from ur.ur_decoder import URDecoder
from embit.psbt import PSBT

def main():
    cap = cv2.VideoCapture(0)
    decoder = URDecoder()
    # Initialize the modern reader
    qreader = QReader()
    
    is_complete = False
    print("\nScanner Active. Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            # QReader returns the string directly
            # It works with a simple pip install
            decoded_text = qreader.detect_and_decode(image=frame)

            for qr_data in decoded_text:
                if qr_data and "UR:CRYPTO-PSBT" in qr_data.upper():
                    if not is_complete:
                        decoder.receive_part(qr_data)
                        
                        progress = decoder.estimated_percent_complete() * 100
                        print(f"Progress: {progress:.0f}%", end="\r")

                        if decoder.is_complete():
                            is_complete = True
                            decoded_ur = decoder.resolve()
                            raw_payload = decoded_ur.cbor
                            
                            psbt_magic = b'psbt\xff'
                            start_index = raw_payload.find(psbt_magic)

                            if start_index != -1:
                                clean_psbt = raw_payload[start_index:]
                                try:
                                    psbt = PSBT.parse(clean_psbt)
                                    txid = binascii.hexlify(psbt.tx.txid()).decode()
                                    print(f"\n[SUCCESS] TXID: {txid}")
                                except Exception as e:
                                    print(f"\n[-] Error: {e}")

            cv2.imshow("Clean Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
