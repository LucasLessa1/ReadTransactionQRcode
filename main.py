import cv2
import time
import sys
import binascii
import pyperclip  # Library for clipboard
from pyzbar.pyzbar import decode
from ur.ur_decoder import URDecoder
from embit.psbt import PSBT

def main():
    # Initialize Camera
    cap = cv2.VideoCapture(0)
    
    # Decoder Setup
    decoder = URDecoder()
    
    print("\n" + "="*50)
    print(" BITCOIN PSBT SCANNER (Lightweight Mode)")
    print(" Show the animated QR to the camera.")
    print(" The TXID will be COPIED to clipboard automatically.")
    print(" Press 'q' to quit manually.")
    print("="*50 + "\n")

    scanning = True
    found_txid = None

    while scanning:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Decode QR codes
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            (x, y, w, h) = obj.rect
            
            # Visual feedback (Green Box)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            try:
                qr_data = obj.data.decode('utf-8')
                
                # Check for UR Crypto
                if "ur:" in qr_data.lower():
                    decoder.receive_part(qr_data)
                    
                    # Calculate percentage
                    progress = int(decoder.estimated_percent_complete() * 100)
                    
                    # Draw Progress Text on Video
                    text = f"Scanning: {progress}%"
                    cv2.putText(frame, text, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # --- SUCCESS LOGIC ---
                    if decoder.is_complete():
                        print("\n[+] Transfer Complete! Decoding...")
                        
                        decoded_ur = decoder.result
                        raw_payload = decoded_ur.cbor
                        psbt_magic = b'psbt\xff'
                        start_index = raw_payload.find(psbt_magic)

                        if start_index != -1:
                            clean_psbt = raw_payload[start_index:]
                            psbt = PSBT.parse(clean_psbt)
                            
                            # Extract TXID
                            found_txid = binascii.hexlify(psbt.tx.txid()).decode()
                            
                            # COPY TO CLIPBOARD
                            pyperclip.copy(found_txid)
                            
                            print("="*40)
                            print(" SUCCESS! TXID COPIED TO CLIPBOARD:")
                            print(f" {found_txid}")
                            print("="*40)
                            
                            # Draw FINAL Success Message on Screen
                            cv2.rectangle(frame, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
                            cv2.putText(frame, "SUCCESS! COPIED!", (50, 60), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                            
                            # Show the success frame for 3 seconds then close
                            cv2.imshow("Scanner", frame)
                            cv2.waitKey(3000) 
                            scanning = False
                            break
                        else:
                            print("[-] Error: Magic Bytes not found.")
            except Exception as e:
                pass

        # Display Frame
        if scanning:
            cv2.imshow("Scanner", frame)

        # Quit Trigger
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    if found_txid:
        # Keep terminal open to show result if run from CLI
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()