import cv2
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from ur.ur_decoder import URDecoder
from embit.psbt import PSBT
import binascii

class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin PSBT Scanner")
        self.root.geometry("600x750")
        self.root.configure(bg="#1e1e1e")

        # --- Elementos da Interface ---
        
        # Título
        tk.Label(root, text="Aponte para o QR Code Animado", 
                 bg="#1e1e1e", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Área do Vídeo
        self.video_frame = tk.Label(root, bg="black", text="Iniciando Câmera...", fg="white")
        self.video_frame.pack(padx=10, pady=10)

        # Barra de Progresso
        tk.Label(root, text="Progresso de Leitura:", bg="#1e1e1e", fg="#aaaaaa").pack(pady=(10,0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=50, pady=5)
        
        self.status_lbl = tk.Label(root, text="Aguardando...", bg="#1e1e1e", fg="#00ff88", font=("Consolas", 10))
        self.status_lbl.pack(pady=5)

        # Área de Resultado (Invisível no início)
        self.result_frame = tk.Frame(root, bg="#1e1e1e")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.result_frame, text="TXID Encontrado (Copie abaixo):", 
                 bg="#1e1e1e", fg="white").pack(anchor="w")
        
        self.entry_txid = tk.Entry(self.result_frame, font=("Consolas", 11), bg="#333", fg="#00ff88")
        self.entry_txid.pack(fill=tk.X, pady=5, ipady=5)

        self.btn_copy = tk.Button(self.result_frame, text="COPIAR TXID", 
                                  command=self.copy_to_clipboard, 
                                  bg="#007acc", fg="white", font=("Segoe UI", 10, "bold"), state="disabled")
        self.btn_copy.pack(fill=tk.X, pady=10)

        self.btn_reset = tk.Button(root, text="Escanear Novamente", command=self.reset_scanner, bg="#444", fg="white")
        self.btn_reset.pack(side=tk.BOTTOM, pady=20)

        # --- Lógica do Scanner ---
        self.decoder = URDecoder()
        self.cap = None
        self.stop_event = threading.Event()
        self.is_running = False

        # Iniciar Câmera
        self.start_camera()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.video_loop, daemon=True)
        self.thread.start()

    def video_loop(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                # 1. Tentar ler QR Codes na imagem
                decoded_objects = decode(frame) # Usa pyzbar (mais rápido que cv2 puro)

                for obj in decoded_objects:
                    # Desenhar retângulo verde
                    (x, y, w, h) = obj.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    try:
                        qr_data = obj.data.decode('utf-8')

                        # Se for parte do UR:CRYPTO-PSBT
                        if "ur:" in qr_data.lower():
                            self.decoder.receive_part(qr_data)
                            
                            # Atualizar Progresso na Interface
                            percent = self.decoder.estimated_percent_complete() * 100
                            self.root.after(0, self.update_progress, percent)

                            # Se terminou
                            if self.decoder.is_complete():
                                self.stop_event.set()
                                self.root.after(0, self.process_result)
                    except Exception:
                        pass

                # Converter imagem para Tkinter
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.root.after(0, self.update_video_label, imgtk)
            else:
                break
        
        if self.cap:
            self.cap.release()

    def update_video_label(self, imgtk):
        if self.is_running:
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

    def update_progress(self, val):
        self.progress_var.set(val)
        self.status_lbl.config(text=f"Lendo partes... {int(val)}%")

    def process_result(self):
        self.is_running = False
        self.video_frame.config(image='', text="Leitura Concluída!", height=15)
        self.status_lbl.config(text="✅ SUCESSO!", fg="#00ff00")

        try:
            # Lógica de Decodificação (Do seu código original)
            if hasattr(self.decoder, 'resolve'):
                decoded_ur = self.decoder.resolve()
            else:
                decoded_ur = self.decoder.result
            
            raw_payload = decoded_ur.cbor
            psbt_magic = b'psbt\xff'
            start_index = raw_payload.find(psbt_magic)

            if start_index != -1:
                clean_psbt = raw_payload[start_index:]
                psbt = PSBT.parse(clean_psbt)
                txid = binascii.hexlify(psbt.tx.txid()).decode()

                # Mostrar no Front
                self.entry_txid.delete(0, tk.END)
                self.entry_txid.insert(0, txid)
                self.btn_copy.config(state="normal")
            else:
                messagebox.showerror("Erro", "Bytes mágicos do PSBT não encontrados.")

        except Exception as e:
            messagebox.showerror("Erro de Parse", str(e))

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.entry_txid.get())
        messagebox.showinfo("Copiado", "TXID copiado para a área de transferência!")

    def reset_scanner(self):
        if self.is_running: return
        self.entry_txid.delete(0, tk.END)
        self.btn_copy.config(state="disabled")
        self.progress_var.set(0)
        self.status_lbl.config(text="Aguardando...")
        self.decoder = URDecoder()
        self.start_camera()

    def on_closing(self):
        self.stop_event.set()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()