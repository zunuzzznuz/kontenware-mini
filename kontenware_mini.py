import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
from datetime import datetime
from openai import AzureOpenAI
from PIL import Image, ImageTk
import io
import base64
import threading
import sys
import os

class KontenwareMini:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kontenware mini v1.0")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f5f7fa")
        
        if sys.platform == "win32":
            self.root.iconbitmap()  
            try:
                temp_icon = os.path.join(os.environ['TEMP'], "empty.ico")
                if not os.path.exists(temp_icon):
                    with open(temp_icon, "wb") as f:
                        f.write(b"")  
                self.root.iconbitmap(temp_icon)
            except:
                pass
        
        self.azure_client = None
        self.scan_history = []
        self.current_image = None
        
        self.setup_azure_client()
        self.buat_widget()
    
    def setup_azure_client(self):
        try:
            self.azure_client = AzureOpenAI(
                api_version="2024-12-01-preview",
                azure_endpoint="https://pinternz-resource.cognitiveservices.azure.com/",
                api_key="G156sQMPz0GS8cWX8TqoG4JazVhrvlreraggDe0caxmMgaglnyaaJQQJ99BFACHYHv6XJ3w3AAAAACOGRAV1"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Koneksi Azure gagal: {str(e)}")
            self.root.destroy()
    
    def buat_widget(self):
        style = ttk.Style()
        style.configure(".", font=("Arial", 10))
        style.configure("TFrame", background="#f5f7fa")
        style.configure("TLabel", background="#f5f7fa")
        style.configure("TButton", padding=5)
        
        title_label = ttk.Label(self.root, 
                              text="Amankan dunia digital anak anda dimulai dari sini...", 
                              font=("Arial", 16, "bold"),
                              foreground="#2c3e50")
        title_label.pack(pady=10)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.buat_tab_analisis_teks(notebook)
        self.buat_tab_analisis_gambar(notebook)
        self.buat_tab_riwayat(notebook)
    
    def buat_tab_analisis_teks(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Analisis Teks")
        
        input_frame = ttk.LabelFrame(tab, text="Masukkan teks untuk diperiksa:", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.input_teks = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.input_teks.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Periksa Sekarang", 
                 command=self.mulai_analisis_teks).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Contoh Teks",
                 command=self.contoh_teks).pack(side=tk.LEFT, padx=5)
        
        self.loading_label_teks = ttk.Label(tab, text="", foreground="green")
        self.loading_label_teks.pack()
        
        hasil_frame = ttk.LabelFrame(tab, text="Hasil Pemeriksaan:", padding=10)
        hasil_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.hasil_analisis_teks = scrolledtext.ScrolledText(hasil_frame, height=10, wrap=tk.WORD)
        self.hasil_analisis_teks.pack(fill=tk.BOTH, expand=True)
    
    def buat_tab_analisis_gambar(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Analisis Gambar")
        
        upload_frame = ttk.Frame(tab)
        upload_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(upload_frame, text="Pilih Gambar", 
                 command=self.pilih_gambar).pack(pady=5)
        
        self.image_frame = ttk.LabelFrame(tab, text="Pratinjau Gambar:", padding=10)
        self.image_frame.pack(padx=10, pady=5)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack()
        
        ttk.Button(tab, text="Analisis Gambar", 
                 command=self.mulai_analisis_gambar).pack(pady=5)
        
        self.loading_label_gambar = ttk.Label(tab, text="", foreground="green")
        self.loading_label_gambar.pack()
        
        hasil_frame = ttk.LabelFrame(tab, text="Hasil Analisis:", padding=10)
        hasil_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.hasil_analisis_gambar = scrolledtext.ScrolledText(hasil_frame, height=10, wrap=tk.WORD)
        self.hasil_analisis_gambar.pack(fill=tk.BOTH, expand=True)
    
    def buat_tab_riwayat(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Riwayat")
        
        frame_riwayat = ttk.Frame(tab)
        frame_riwayat.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(frame_riwayat)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.daftar_riwayat = tk.Listbox(frame_riwayat, font=("Arial", 10),
                                        yscrollcommand=scrollbar.set)
        self.daftar_riwayat.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.daftar_riwayat.yview)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Lihat Detail", 
                 command=self.lihat_detail_riwayat).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hapus Riwayat",
                 command=self.hapus_riwayat).pack(side=tk.LEFT, padx=5)
    
    def pilih_gambar(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                image.thumbnail((400, 400))
                self.current_image = image
                
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo)
                self.image_label.image = photo
                
                self.hasil_analisis_gambar.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat gambar: {str(e)}")
    
    def mulai_analisis_teks(self):
        teks = self.input_teks.get("1.0", tk.END).strip()
        if not teks:
            messagebox.showwarning("Peringatan", "Masukkan teks terlebih dahulu")
            return
        
        self.loading_label_teks.config(text="Sedang menganalisis...")
        self.hasil_analisis_teks.delete("1.0", tk.END)
        
        threading.Thread(target=self.analisis_teks, args=(teks,), daemon=True).start()
    
    def mulai_analisis_gambar(self):
        if not self.current_image:
            messagebox.showwarning("Peringatan", "Pilih gambar terlebih dahulu")
            return
        
        self.loading_label_gambar.config(text="Sedang menganalisis gambar...")
        self.hasil_analisis_gambar.delete("1.0", tk.END)
        
        threading.Thread(target=self.analisis_gambar, daemon=True).start()
    
    def analisis_teks(self, teks):
        try:
            prompt = (
                "Hai, saya orang tua yang ingin memeriksa keamanan konten digital untuk anak. "
                f"Bisa bantu analisis konten berikut dengan bahasa santai:\n\n{teks}\n\n"
                "Tolong berikan pendapat sebagai ahli keamanan anak dengan format paragraf "
                "yang mengalir natural, fokus pada: tingkat keamanan, alasan utama, "
                "dan saran praktis untuk orang tua."
            )
            
            respon = self.azure_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Anda ahli keamanan digital untuk anak. Sampaikan analisis dengan "
                            "bahasa santai seperti ngobrol langsung dengan orang tua. "
                            "Gunakan format paragraf natural tanpa numbering atau bullet points."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            hasil = respon.choices[0].message.content
            self.root.after(0, self.tampilkan_hasil_teks, hasil, teks)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Gagal menganalisis: {str(e)}")
        finally:
            self.root.after(0, self.loading_label_teks.config, {"text": ""})
    
    def analisis_gambar(self):
        try:
            buffered = io.BytesIO()
            self.current_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            respon = self.azure_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Anda ahli keamanan digital untuk anak. Analisis gambar ini dengan "
                            "bahasa santai seperti sedang berbicara langsung dengan orang tua. "
                            "Fokus pada: deskripsi singkat, tingkat keamanan, potensi masalah, "
                            "dan saran praktis. Gunakan format paragraf natural."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Bisa bantu analisis gambar ini untuk keamanan anak? "
                                    "Tolong jelaskan dengan bahasa santai dalam format paragraf."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            hasil = respon.choices[0].message.content
            self.root.after(0, self.tampilkan_hasil_gambar, hasil)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Gagal menganalisis gambar: {str(e)}")
        finally:
            self.root.after(0, self.loading_label_gambar.config, {"text": ""})
    
    def tampilkan_hasil_teks(self, hasil, teks):
        self.hasil_analisis_teks.config(state=tk.NORMAL)
        self.hasil_analisis_teks.delete("1.0", tk.END)
        self.hasil_analisis_teks.insert(tk.END, hasil)
        self.hasil_analisis_teks.config(state=tk.DISABLED)
        self.simpan_ke_riwayat(teks, hasil, "Teks")
    
    def tampilkan_hasil_gambar(self, hasil):
        self.hasil_analisis_gambar.config(state=tk.NORMAL)
        self.hasil_analisis_gambar.delete("1.0", tk.END)
        self.hasil_analisis_gambar.insert(tk.END, hasil)
        self.hasil_analisis_gambar.config(state=tk.DISABLED)
        self.simpan_ke_riwayat("Analisis Gambar", hasil, "Gambar")
    
    def contoh_teks(self):
        contoh = (
            "Anak saya menemukan game online yang memiliki fitur chat dengan pemain lain. "
            "Saya ingin memastikan apakah kontennya aman untuk anak usia 9 tahun. "
            "Game tersebut bernama 'Adventure World' dan memiliki rating untuk usia 12+."
        )
        self.input_teks.delete("1.0", tk.END)
        self.input_teks.insert("1.0", contoh)
    
    def simpan_ke_riwayat(self, konten, hasil, jenis):
        waktu = datetime.now().strftime("%d/%m %H:%M")
        
        self.scan_history.append({
            "waktu": waktu,
            "jenis": jenis,
            "konten": konten[:100] + "..." if len(konten) > 100 else konten,
            "hasil": hasil
        })
        
        self.perbarui_daftar_riwayat()
    
    def perbarui_daftar_riwayat(self):
        self.daftar_riwayat.delete(0, tk.END)
        for item in reversed(self.scan_history[-20:]):
            entry = f"{item['waktu']} [{item['jenis']}] - {item['konten']}"
            self.daftar_riwayat.insert(tk.END, entry)
    
    def lihat_detail_riwayat(self):
        selection = self.daftar_riwayat.curselection()
        if not selection:
            return
            
        item = self.scan_history[-1 - selection[0]]
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Detail Pemeriksaan")
        detail_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, item["hasil"])
        text_area.config(state=tk.DISABLED)
    
    def hapus_riwayat(self):
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat pemeriksaan?"):
            self.scan_history = []
            self.daftar_riwayat.delete(0, tk.END)
    
    def jalankan(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KontenwareMini()
    app.jalankan()