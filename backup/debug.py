import sys
import binascii

from ur.ur_encoder import UREncoder
from ur.ur_decoder import URDecoder
import embit
from embit.psbt import PSBT

def debug_qr_sequence(parts):
    decoder = URDecoder()
    print(f"[*] Processing {len(parts)} QR parts...")
    
    for part in parts:
        decoder.receive_part(part)

    if not decoder.is_complete():
        print(f"[!] Error: Data incomplete.")
        return

    # 1. Get the result
    decoded_ur = decoder.result
    raw_payload = decoded_ur.cbor

    # 2. DEBUGGING: Print what we actually got
    print("\n" + "="*30)
    print(" DEBUG INFO ")
    print("="*30)
    print(f"Type of payload: {type(raw_payload)}")
    
    if isinstance(raw_payload, bytes):
        hex_preview = binascii.hexlify(raw_payload[:20]).decode()
        print(f"First 20 bytes (Hex): {hex_preview}")
        
        # CHECK 1: Is it a valid PSBT?
        if hex_preview.startswith("70736274ff"):
            print("STATUS: Looks like a valid PSBT!")
        else:
            print("STATUS: INVALID MAGIC BYTES (Does not start with 70736274ff)")
            # CHECK 2: Is it wrapped in CBOR? (Starts with 58, 59, or 4x)
            if hex_preview.startswith(("58", "59", "4", "a", "d8")):
                print("HINT: The data seems to be still wrapped in CBOR.")
    else:
        print(f"Content: {raw_payload}")

    print("="*30 + "\n")

    # 3. Attempt to parse if it is bytes
    if isinstance(raw_payload, bytes):
        try:
            psbt = PSBT.parse(raw_payload)
            print("SUCCESS: PSBT Parsed correctly!")
            print(f"TXID: {binascii.hexlify(psbt.tx.txid()).decode()}")
        except Exception as e:
            print(f"ERROR Parsing: {e}")

# --- YOUR DATA ---
qr_part_1 = "UR:CRYPTO-PSBT/1-2/LPADAOCFADGSCYJPRSDMRLHDOLHKADGAJOJKIDJYZMADAEJSAOAEAEAEADRPCFTSSBLRRFNETOLKMNMSNSDSGTGDDNCYPTENMOFNOLFGZEIATIMDPEWPNDLTTTAEAEAEAEAEZMZMZMZMAOBEDIAEAEAEAEAEAECMAEBBDWLFLFBSNDONNNCFLUFDROCWINWMFMLTBZLFONCYPMUODWAEAEAEAEAECMAEBBQZCSNTEMJKMDZESRRPAYGDDSFYNNPRUENBTNBYOSAEAEAEAEAEADADCTGWAADPAEAEAEAEAECMAEBBINWEJTKNNTESSRDYOEBBBWFSTNCSFGDABNKPHLLYADAYJEAOFLDYFYKEJLCLEM"
qr_part_2 = "UR:CRYPTO-PSBT/2-2/LPAOAOCFADGSCYJPRSDMRLHDOLAOCXETSAIYLPRYTKCXKGGTCNKIYKBZBWGRRTBZTSAORTWSETYLKNJTMDMDUELRNLISFMAOCXJLMHOXIHHGTLHNATVSPDJSLGYNWLVYMKVWIHUYWSEEDKMWDYVELPJLMUWSUOEOPYADCLAXOSWYKNBTWPAHKGJKAAPTPYLPRSQDHPRLCEJYRFFSVANYCXKSIYIEPMISURWDZCWPAEAECPAOAXGMMSPLOLWLMUDAJLKGURZOFRTYTSAODADTMUAMHDMSMWPAWLDYLYZMBAKGPEPRRYCSAEAEAEAEGHAEAELAAEAEAELAAEAEAELAADAEAEAEAEAEAEAEAECWMTFEFD"

if __name__ == "__main__":
    debug_qr_sequence([qr_part_1, qr_part_2])