import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import random
from sklearn.tree import DecisionTreeClassifier
from gtts import gTTS
import pygame
import os
import time
import speech_recognition as sr

pygame.mixer.init()
data = pd.read_csv("zoo.csv")

feature_map = {
    'hair': 'Memiliki Rambut',
    'feathers': 'Memiliki Bulu',
    'eggs': 'Bertelur',
    'milk': 'Menyusui',
    'airborne': 'Bisa Terbang',
    'aquatic': 'Hidup di Air',
    'toothed': 'Memiliki Gigi',
    'backbone': 'Memiliki Tulang Belakang',
    'breathes': 'Bernapas',
    'venomous': 'Beracun',
    'fins': 'Memiliki Sirip',
    'legs': 'Jumlah Kaki',
    'tail': 'Memiliki Ekor',
    'domestic': 'Hewan Domestik'
}

gui_features = list(feature_map.keys())
model_features = gui_features + ['catsize']
X = data[model_features]
y = data['class_type']

class_mapping = {
    1: "Mamalia", 2: "Burung", 3: "Reptil", 4: "Ikan",
    5: "Amfibi", 6: "Serangga", 7: "Invertebrata"
}

common_animals = [
    "platypus", "penguin", "flamingo", "giraffe", "elephant", "lion",
    "horse", "pike", "herring", "frog", "cobra", "worm", "honeybee", "seal"
]

model = DecisionTreeClassifier()
model.fit(X, y)

root = tk.Tk()
root.title("Game Edukasi Klasifikasi Hewan")
root.geometry("750x1000")
root.configure(bg="white")

main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, bg="white")
scroll_y = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)
canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")

info_label = tk.Label(scrollable_frame, text="Klasifikasi Hewan", font=("Helvetica", 16, "bold"), bg="white", fg="darkgreen")
info_label.pack(pady=10)

image_label = tk.Label(scrollable_frame, bg="white")
image_label.pack(pady=10)
img_ref = None

title_label = tk.Label(scrollable_frame, text="", font=("Helvetica", 14, "bold"), fg="darkblue", bg="white")
title_label.pack(pady=5)

frame = tk.Frame(scrollable_frame, bg="white")
frame.pack(pady=10)

input_vars = {}

for key in gui_features:
    box = tk.LabelFrame(frame, text=feature_map[key], padx=10, pady=5, bg="white", font=("Arial", 10, "bold"), fg="black")
    box.pack(fill="x", padx=80, pady=3)

    row_frame = tk.Frame(box, bg="white")
    row_frame.pack(fill="x")

    var = tk.StringVar()
    options = sorted([str(opt) for opt in data['legs'].unique()]) if key == 'legs' else ["0", "1"]
    combo = ttk.Combobox(row_frame, textvariable=var, values=options, state="readonly", font=("Arial", 10), width=10)
    combo.pack(side="left", padx=(0, 10))
    
    def make_voice_input_callback(v, k):
        def callback():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                messagebox.showinfo("Rekam", f"Ucapkan 'ya' atau 'tidak' untuk: {feature_map[k]}")
                try:
                    audio = r.listen(source, timeout=4)
                    response = r.recognize_google(audio, language="id-ID").lower()
                    print("Kamu mengatakan:", response)

                    if "ya" in response:
                        v.set("1")
                    elif "tidak" in response:
                        v.set("0")
                    else:
                        messagebox.showwarning("Tidak dikenal", "Silakan ucapkan 'ya' atau 'tidak'")
                except sr.WaitTimeoutError:
                    messagebox.showerror("Timeout", "Tidak ada suara terdeteksi.")
                except sr.UnknownValueError:
                    messagebox.showerror("Gagal", "Tidak bisa mengenali suara.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        return callback

    if key != 'legs':  # hanya untuk fitur biner
        voice_button = tk.Button(row_frame, text="🎤", command=make_voice_input_callback(var, key), bg="#f8f9fa", font=("Arial", 10, "bold"))
        voice_button.pack(side="left")

    input_vars[key] = var


result_label = tk.Label(scrollable_frame, text="", font=("Arial", 12), fg="blue", bg="white", justify="left")
result_label.pack(pady=15)

sample = None
animal_name = ""
true_class = ""
true_features = {}

def generate_new_question():
    global sample, animal_name, true_class, true_features, img_ref
    result_label.config(text="")
    image_label.config(image='', text='')

    sample = data[data['animal_name'].isin(common_animals)].sample(1).iloc[0]
    animal_name = sample['animal_name']
    true_class = class_mapping[sample['class_type']]
    true_features = sample.to_dict()
    title_label.config(text=f"Tebak klasifikasi hewan: {animal_name.capitalize()}")

    for var in input_vars.values():
        var.set("")

    img_path = f"image/{animal_name.lower()}.jpeg"
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path).resize((220, 220))
            img_ref = ImageTk.PhotoImage(img)
            image_label.config(image=img_ref, text="")
        except:
            image_label.config(text="(Gagal memuat gambar)", fg="red", font=("Arial", 12))
    else:
        image_label.config(text="(Gambar tidak tersedia)", fg="gray", font=("Arial", 12))

def isi_dengan_suara():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Rekam", "Silakan ucapkan 'ya' atau 'tidak'")
        try:
            audio = r.listen(source, timeout=4)
            response = r.recognize_google(audio, language="id-ID").lower()
            print("Kamu mengatakan:", response)

            if "ya" in response:
                value = "1"
            elif "tidak" in response:
                value = "0"
            else:
                messagebox.showwarning("Tidak dikenal", "Silakan ucapkan 'ya' atau 'tidak'")
                return

            for key, var in input_vars.items():
                if key != 'legs':
                    var.set(value)

        except sr.WaitTimeoutError:
            messagebox.showerror("Timeout", "Tidak ada suara terdeteksi.")
        except sr.UnknownValueError:
            messagebox.showerror("Gagal", "Tidak bisa mengenali suara.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def evaluate():
    try:
        for key, var in input_vars.items():
            if var.get() == '':
                messagebox.showwarning("Input Tidak Lengkap", f"Silakan pilih nilai untuk fitur '{feature_map[key]}'!")
                return

        user_input_gui = {k: int(v.get()) for k, v in input_vars.items()}
        correct = sum(user_input_gui[k] == true_features[k] for k in gui_features)
        total = len(gui_features)
        accuracy = correct / total * 100

        wrongs = [k for k in gui_features if user_input_gui[k] != true_features[k]]
        mistake_desc = "\n".join([
            f"- {feature_map[w]}: Anda isi {user_input_gui[w]}, seharusnya {true_features[w]}"
            for w in wrongs
        ]) if wrongs else "Tidak ada kesalahan!"

        user_input_full = user_input_gui.copy()
        user_input_full['catsize'] = true_features['catsize']
        predicted_class_num = model.predict(pd.DataFrame([user_input_full]))[0]
        predicted_class = class_mapping[predicted_class_num]

        result_text = (
            f"✅ Jawaban benar: {true_class}\n"
            f"🧠 Prediksi berdasarkan input Anda: {predicted_class}\n"
            f"🎯 Akurasi jawaban Anda: {accuracy:.2f}%\n"
            f"❗ Kesalahan:\n{mistake_desc}"
        )

        result_label.config(text=result_text)

        summary_speech = (
            f"Jawaban yang benar adalah {true_class}. "
            f"Prediksi berdasarkan input kamu adalah {predicted_class}. "
            f"Akurasi jawaban kamu adalah {int(accuracy)} persen."
        )
        tts = gTTS(text=summary_speech, lang='id')
        tts.save("hasil.mp3")

        pygame.mixer.music.load("hasil.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        time.sleep(0.1)
        os.remove("hasil.mp3")

    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(scrollable_frame, text="✅ Submit Jawaban", command=evaluate, bg="#cce5ff", font=("Arial", 12, "bold")).pack(pady=10)
tk.Button(scrollable_frame, text="🔄 Soal Baru", command=generate_new_question, bg="#d4edda", font=("Arial", 12, "bold")).pack(pady=5)
tk.Button(scrollable_frame, text="🎙️ Isi dengan Suara", command=isi_dengan_suara, bg="#fff3cd", font=("Arial", 12, "bold")).pack(pady=5)

generate_new_question()
root.mainloop()
