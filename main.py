import cv2
from pyzbar import pyzbar
import sys
import binascii
from ur.ur_encoder import UREncoder
from ur.ur_decoder import URDecoder
import embit
from embit.psbt import PSBT


def main():
    # Initialize Camera
    cap = cv2.VideoCapture(0)
    
    # Initialize the Fountain Code Decoder
    decoder = URDecoder()
    
    # State flags
    is_complete = False
    result_text = "Scanning..."
    result_color = (0, 255, 255) # Yellow initially

    print("\n" + "="*50)
    print(" BITCOIN PSBT SCANNER LAUNCHED")
    print(" Show the animated QR to the camera.")
    print(" Press 'r' to reset, 'q' to quit.")
    print("="*50 + "\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Find QRs in the image
            decoded_objects = pyzbar.decode(frame)

            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                
                # Check if it is a UR Crypto part
                if "UR:CRYPTO-PSBT" in qr_data.upper():
                    
                    # Draw a box around the QR
                    (x, y, w, h) = obj.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    # Only process if we haven't finished yet
                    if not is_complete:
                        decoder.receive_part(qr_data)
                        
                        # Calculate progress
                        progress = decoder.estimated_percent_complete() * 100
                        
                        # Show progress on screen
                        cv2.putText(frame, f"Progress: {progress:.0f}%", (x, y - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                        # --- SUCCESS TRIGGER ---
                        if decoder.is_complete():
                            is_complete = True
                            print("\n[+] Transfer Complete! Decoding...")
                            
                            # 1. Get CBOR Payload
                            decoded_ur = decoder.result
                            raw_payload = decoded_ur.cbor
                            
                            # 2. THE MAGIC BYTE FIX
                            # Find where 'psbt' + 0xff starts
                            psbt_magic = b'psbt\xff'
                            start_index = raw_payload.find(psbt_magic)

                            if start_index != -1:
                                # Extract clean PSBT
                                clean_psbt = raw_payload[start_index:]
                                
                                try:
                                    # Parse and Hash
                                    psbt = PSBT.parse(clean_psbt)
                                    txid = binascii.hexlify(psbt.tx.txid()).decode()
                                    
                                    # Update UI Text
                                    result_text = f"TXID: {txid}"
                                    result_color = (0, 255, 0) # Green
                                    
                                    print("="*40)
                                    print(" SUCCESS - TRANSACTION ID FOUND")
                                    print(f" {txid}")
                                    print("="*40)
                                    
                                except Exception as e:
                                    print(f"[-] PSBT Parsing Error: {e}")
                                    result_text = "Error: Invalid PSBT"
                                    result_color = (0, 0, 255)
                            else:
                                print("[-] Error: Magic Bytes not found in payload.")
                                result_text = "Error: Magic Bytes Missing"
                                result_color = (0, 0, 255)

            # Display the result on the screen if complete
            if is_complete:
                # Background black bar for text readability
                cv2.rectangle(frame, (0, 0), (frame.shape[1], 80), (0, 0, 0), -1)
                
                # Print "SUCCESS"
                cv2.putText(frame, "DECODE SUCCESS!", (20, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Print the TXID (small font)
                cv2.putText(frame, result_text[:40] + "...", (20, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, result_color, 2)
                
                # Instructions
                cv2.putText(frame, "Press 'r' to reset", (20, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

            # Show window
            cv2.imshow("Bitcoin PSBT Scanner", frame)

            # Controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Reset everything to scan a new transaction
                decoder = URDecoder()
                is_complete = False
                result_text = "Scanning..."
                result_color = (0, 255, 255)
                print("\n[+] Scanner Reset. Ready for next transaction.")

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()