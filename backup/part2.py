import sys
import binascii

from ur.ur_encoder import UREncoder
from ur.ur_decoder import URDecoder
import embit
from embit.psbt import PSBT

def decode_qr_sequence(parts):
    decoder = URDecoder()
    
    print(f"[*] Processing {len(parts)} QR parts...")
    
    for part in parts:
        decoder.receive_part(part)

    if not decoder.is_complete():
        print(f"[!] Error: Data incomplete.")
        return

    # 1. Get the decoded object (UR)
    decoded_ur = decoder.result
    raw_payload = decoded_ur.cbor

    # 2. THE FIX: Strip the CBOR Wrapper
    # We search for the PSBT "Magic Bytes" (psbt + 0xff) and slice the data from there.
    # This automatically handles different CBOR header sizes (0x58, 0x59, etc.)
    psbt_magic = b'psbt\xff'
    start_index = raw_payload.find(psbt_magic)

    if start_index == -1:
        print("Error: Valid PSBT magic bytes not found in payload.")
        return
        
    # Slice the bytes to get the pure PSBT
    clean_psbt_bytes = raw_payload[start_index:]

    # 3. Parse with embit
    try:
        psbt = PSBT.parse(clean_psbt_bytes)
        
        # Calculate TXID
        tx = psbt.tx
        txid_bytes = tx.txid()
        txid_hex = binascii.hexlify(txid_bytes).decode()
        
        print("\n" + "="*40)
        print(" SUCCESS ")
        print("="*40)
        print(f"Transaction ID: {txid_hex}")
        print("="*40)
        
    except Exception as e:
        print(f"[!] Error parsing PSBT: {e}")

# --- YOUR DATA ---
qr_part_1 = "UR:CRYPTO-PSBT/1-2/LPADAOCFADGSCYJPRSDMRLHDOLHKADGAJOJKIDJYZMADAEJSAOAEAEAEADRPCFTSSBLRRFNETOLKMNMSNSDSGTGDDNCYPTENMOFNOLFGZEIATIMDPEWPNDLTTTAEAEAEAEAEZMZMZMZMAOBEDIAEAEAEAEAEAECMAEBBDWLFLFBSNDONNNCFLUFDROCWINWMFMLTBZLFONCYPMUODWAEAEAEAEAECMAEBBQZCSNTEMJKMDZESRRPAYGDDSFYNNPRUENBTNBYOSAEAEAEAEAEADADCTGWAADPAEAEAEAEAECMAEBBINWEJTKNNTESSRDYOEBBBWFSTNCSFGDABNKPHLLYADAYJEAOFLDYFYKEJLCLEM"
qr_part_2 = "UR:CRYPTO-PSBT/2-2/LPAOAOCFADGSCYJPRSDMRLHDOLAOCXETSAIYLPRYTKCXKGGTCNKIYKBZBWGRRTBZTSAORTWSETYLKNJTMDMDUELRNLISFMAOCXJLMHOXIHHGTLHNATVSPDJSLGYNWLVYMKVWIHUYWSEEDKMWDYVELPJLMUWSUOEOPYADCLAXOSWYKNBTWPAHKGJKAAPTPYLPRSQDHPRLCEJYRFFSVANYCXKSIYIEPMISURWDZCWPAEAECPAOAXGMMSPLOLWLMUDAJLKGURZOFRTYTSAODADTMUAMHDMSMWPAWLDYLYZMBAKGPEPRRYCSAEAEAEAEGHAEAELAAEAEAELAAEAEAELAADAEAEAEAEAEAEAEAECWMTFEFD"

if __name__ == "__main__":
    decode_qr_sequence([qr_part_1, qr_part_2])