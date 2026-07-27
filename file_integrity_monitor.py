import hashlib
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

DATABASE_FILE = "file_hashes.json"


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            while True:
                data = file.read(4096)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    except OSError as error:
        messagebox.showerror("Hata", f"Dosya okunamadı:\n{error}")
        return None


def load_database():
    if not os.path.exists(DATABASE_FILE):
        return {}

    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_database(database):
    try:
        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(database, file, indent=4, ensure_ascii=False)

    except OSError as error:
        messagebox.showerror("Hata", f"Veritabanı kaydedilemedi:\n{error}")


def select_file():
    file_path = filedialog.askopenfilename()

    if file_path:
        file_path_entry.delete(0, tk.END)
        file_path_entry.insert(0, file_path)


def register_file():
    file_path = file_path_entry.get().strip()

    if not file_path:
        messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin.")
        return

    if not os.path.isfile(file_path):
        messagebox.showerror("Hata", "Seçilen dosya bulunamadı.")
        return

    file_hash = calculate_sha256(file_path)

    if not file_hash:
        return

    database = load_database()

    database[file_path] = {
        "sha256": file_hash,
        "registered_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }

    save_database(database)

    result_text.delete("1.0", tk.END)
    result_text.insert(
        tk.END,
        f"Dosya başarıyla kaydedildi.\n\n"
        f"Dosya:\n{file_path}\n\n"
        f"SHA-256:\n{file_hash}"
    )

    status_label.config(text="Dosya bütünlük kaydı oluşturuldu.")


def verify_file():
    file_path = file_path_entry.get().strip()

    if not file_path:
        messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin.")
        return

    if not os.path.isfile(file_path):
        messagebox.showerror("Hata", "Seçilen dosya bulunamadı.")
        return

    database = load_database()

    if file_path not in database:
        messagebox.showwarning(
            "Kayıt Bulunamadı",
            "Bu dosya daha önce kaydedilmemiş."
        )
        return

    current_hash = calculate_sha256(file_path)

    if not current_hash:
        return

    saved_hash = database[file_path]["sha256"]

    result_text.delete("1.0", tk.END)

    if current_hash == saved_hash:
        result_text.insert(
            tk.END,
            f"DOSYA GÜVENLİ\n\n"
            f"Dosyada herhangi bir değişiklik tespit edilmedi.\n\n"
            f"Dosya:\n{file_path}\n\n"
            f"SHA-256:\n{current_hash}"
        )

        status_label.config(text="Dosya bütünlüğü doğrulandı.")

    else:
        result_text.insert(
            tk.END,
            f"DOSYA DEĞİŞTİRİLMİŞ\n\n"
            f"Dosyanın SHA-256 değeri önceki kayıtla eşleşmiyor.\n\n"
            f"Dosya:\n{file_path}\n\n"
            f"Kayıtlı SHA-256:\n{saved_hash}\n\n"
            f"Güncel SHA-256:\n{current_hash}"
        )

        status_label.config(text="Dosya değişikliği tespit edildi.")


def remove_record():
    file_path = file_path_entry.get().strip()

    if not file_path:
        messagebox.showwarning("Uyarı", "Lütfen bir dosya seçin.")
        return

    database = load_database()

    if file_path not in database:
        messagebox.showwarning("Uyarı", "Bu dosyaya ait kayıt bulunamadı.")
        return

    del database[file_path]
    save_database(database)

    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "Dosyaya ait bütünlük kaydı silindi.")

    status_label.config(text="Kayıt silindi.")


root = tk.Tk()
root.title("File Integrity Monitor")
root.geometry("760x520")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="FILE INTEGRITY MONITOR",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=(20, 5))

description_label = tk.Label(
    root,
    text="SHA-256 kullanarak dosya değişikliklerini kontrol edin.",
    font=("Arial", 11)
)
description_label.pack(pady=(0, 20))

file_frame = tk.Frame(root)
file_frame.pack(fill="x", padx=30)

file_path_entry = tk.Entry(
    file_frame,
    font=("Arial", 11)
)
file_path_entry.pack(side="left", fill="x", expand=True, ipady=7)

select_button = tk.Button(
    file_frame,
    text="Dosya Seç",
    command=select_file,
    width=12
)
select_button.pack(side="left", padx=(10, 0), ipady=4)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

register_button = tk.Button(
    button_frame,
    text="Dosyayı Kaydet",
    command=register_file,
    width=18,
    height=2
)
register_button.grid(row=0, column=0, padx=6)

verify_button = tk.Button(
    button_frame,
    text="Bütünlüğü Kontrol Et",
    command=verify_file,
    width=18,
    height=2
)
verify_button.grid(row=0, column=1, padx=6)

remove_button = tk.Button(
    button_frame,
    text="Kaydı Sil",
    command=remove_record,
    width=18,
    height=2
)
remove_button.grid(row=0, column=2, padx=6)

result_text = tk.Text(
    root,
    height=14,
    font=("Consolas", 10),
    wrap="word"
)
result_text.pack(fill="both", expand=True, padx=30, pady=(0, 15))

status_label = tk.Label(
    root,
    text="Hazır",
    anchor="w",
    font=("Arial", 10)
)
status_label.pack(fill="x", padx=30, pady=(0, 15))

root.mainloop()
