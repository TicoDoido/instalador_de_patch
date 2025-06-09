# script_create_patch.py
import os
import zlib
import bsdiff4
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Progressbar

# Temas disponíveis
themes = {
    "dark": {
        "BG": "#2E2E2E",
        "FG": "#FFFFFF",
        "BTN_BG": "#3A3A3A",
        "BTN_FG": "#FFFFFF",
        "ENTRY_BG": "#3A3A3A",
        "ENTRY_FG": "#FFFFFF",
        "TEXT_BG": "#1E1E1E",
        "TEXT_FG": "#FFFFFF",
        "PROGRESS_BG": "#4A4A4A",
        "PROGRESS_FG": "#008000"
    },
    "light": {
        "BG": "#F0F0F0",
        "FG": "#000000",
        "BTN_BG": "#E0E0E0",
        "BTN_FG": "#000000",
        "ENTRY_BG": "#FFFFFF",
        "ENTRY_FG": "#000000",
        "TEXT_BG": "#FFFFFF",
        "TEXT_FG": "#000000",
        "PROGRESS_BG": "#D0D0D0",
        "PROGRESS_FG": "#007700"
    }
}

current_theme = "dark"  # Tema inicial


def apply_theme(root, elements):
    theme = themes[current_theme]
    root.configure(bg=theme["BG"])
    for widget in elements:
        cls = widget.__class__.__name__
        if cls in ("Frame", "LabelFrame"):
            widget.configure(bg=theme["BG"])
        elif cls == "Label":
            widget.configure(bg=theme["BG"], fg=theme["FG"])
        elif cls == "Entry":
            widget.configure(bg=theme["ENTRY_BG"], fg=theme["ENTRY_FG"], insertbackground=theme["FG"])
        elif cls == "Button":
            widget.configure(bg=theme["BTN_BG"], fg=theme["BTN_FG"])
        elif cls == "Text":
            widget.configure(bg=theme["TEXT_BG"], fg=theme["TEXT_FG"])
    # Atualizar progressbar
    style = ttk.Style()
    style.theme_use('default')
    style.configure("green.Horizontal.TProgressbar",
                    background=theme["PROGRESS_FG"],
                    troughcolor=theme["PROGRESS_BG"],
                    bordercolor=theme["BG"],
                    lightcolor=theme["PROGRESS_FG"],
                    darkcolor=theme["PROGRESS_FG"])


def toggle_theme(root, elements):
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    apply_theme(root, elements)


def log_message(text_widget, message):
    text_widget.configure(state=tk.NORMAL)
    text_widget.insert(tk.END, f"{message}\n")
    text_widget.see(tk.END)
    text_widget.configure(state=tk.DISABLED)


def select_folder(entry_widget):
    folder = filedialog.askdirectory()
    if folder:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder)


def select_file(entry_widget):
    file = filedialog.asksaveasfilename(
        defaultextension=".patch",
        initialfile="data.patch",
        filetypes=[("Patch Files", "*.patch")]
    )
    if file:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file)


def create_patch(original_dir, modified_dir, patch_file, log_widget, progress_bar, status_label, button):
    try:
        log_message(log_widget, "Iniciando criação do patch...")

        if not os.path.isdir(original_dir) or not os.path.isdir(modified_dir):
            messagebox.showerror("Erro", "Pastas inválidas.")
            return

        file_list = os.listdir(modified_dir)
        total = len(file_list)
        processed = 0
        arquivos_gerados = 0

        with open(patch_file, 'wb') as patch_output:
            for filename in file_list:
                mod_path = os.path.join(modified_dir, filename)
                orig_path = os.path.join(original_dir, filename)

                if os.path.isfile(mod_path):
                    if os.path.exists(orig_path):
                        with open(orig_path, 'rb') as f_orig, open(mod_path, 'rb') as f_mod:
                            orig_data = f_orig.read()
                            mod_data = f_mod.read()
                            if orig_data != mod_data:
                                patch_data = bsdiff4.diff(orig_data, mod_data)
                                compressed = zlib.compress(patch_data)
                                patch_output.write(len(filename).to_bytes(1, "big"))
                                patch_output.write(filename.encode("utf-8"))
                                patch_output.write(len(compressed).to_bytes(4, "big"))
                                patch_output.write(compressed)
                                log_message(log_widget, f"Patch delta criado: {filename}")
                                arquivos_gerados += 1
                    else:
                        with open(mod_path, 'rb') as f_mod:
                            mod_data = f_mod.read()
                            compressed = zlib.compress(mod_data)
                            patch_output.write(len(filename).to_bytes(1, "big"))
                            patch_output.write(filename.encode("utf-8"))
                            patch_output.write(len(compressed).to_bytes(4, "big"))
                            patch_output.write(compressed)
                            log_message(log_widget, f"Arquivo novo incluído: {filename}")
                            arquivos_gerados += 1

                processed += 1
                progress = int((processed / total) * 100)
                progress_bar["value"] = progress

        status_label.config(text=f"{arquivos_gerados} arquivos adicionados ao patch.", fg=themes[current_theme]["FG"])
        log_message(log_widget, "Patch finalizado com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        log_message(log_widget, f"Erro: {e}")
    finally:
        button.config(state=tk.NORMAL)


def run_thread(original_dir, modified_dir, patch_file, log_widget, progress_bar, status_label, button):
    button.config(state=tk.DISABLED)
    status_label.config(text="Preparando...", fg=themes[current_theme]["FG"])
    threading.Thread(
        target=create_patch,
        args=(original_dir, modified_dir, patch_file, log_widget, progress_bar, status_label, button),
        daemon=True
    ).start()


def build_ui():
    root = tk.Tk()
    root.title("Criador de Patch")
    root.geometry("670x430")
    root.resizable(False, False)

    elements = []

    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    elements.append(main_frame)

    tk.Label(main_frame, text="Pasta Original:").grid(row=0, column=0, pady=5, sticky='e')
    orig_ent = tk.Entry(main_frame, width=40)
    orig_ent.grid(row=0, column=1, padx=5)
    btn1 = tk.Button(main_frame, text="Selecionar", command=lambda: select_folder(orig_ent))
    btn1.grid(row=0, column=2)
    elements += [orig_ent, btn1]

    tk.Label(main_frame, text="Pasta Modificada:").grid(row=1, column=0, pady=5, sticky='e')
    mod_ent = tk.Entry(main_frame, width=40)
    mod_ent.grid(row=1, column=1, padx=5)
    btn2 = tk.Button(main_frame, text="Selecionar", command=lambda: select_folder(mod_ent))
    btn2.grid(row=1, column=2)
    elements += [mod_ent, btn2]

    tk.Label(main_frame, text="Salvar Patch:").grid(row=2, column=0, sticky='e')
    patch_ent = tk.Entry(main_frame, width=40)
    patch_ent.grid(row=2, column=1, padx=5)
    btn3 = tk.Button(main_frame, text="Salvar", command=lambda: select_file(patch_ent))
    btn3.grid(row=2, column=2)
    elements += [patch_ent, btn3]

    log_frame = tk.LabelFrame(main_frame, text="Log de Operação")
    log_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky='we')
    log_frame.columnconfigure(0, weight=1)
    elements.append(log_frame)

    log = tk.Text(log_frame, height=8, state=tk.DISABLED)
    log.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
    scroll = tk.Scrollbar(log_frame, command=log.yview)
    scroll.grid(row=0, column=1, sticky='ns')
    log.config(yscrollcommand=scroll.set)
    elements.append(log)

    progress_frame = tk.Frame(main_frame)
    progress_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky='we')
    progress_bar = Progressbar(progress_frame, orient='horizontal', mode='determinate',
                               length=550, style="green.Horizontal.TProgressbar")
    progress_bar.pack(fill=tk.X, padx=5)
    status_label = tk.Label(progress_frame, text="Aguardando operação...", font=("Arial", 9))
    status_label.pack(pady=3)
    elements += [progress_frame, status_label]

    btn_frame = tk.Frame(main_frame)
    btn_frame.grid(row=5, column=0, columnspan=3, pady=10)
    create_btn = tk.Button(btn_frame, text="Criar Patch", width=15, font=("Arial", 10, "bold"))
    create_btn.pack(side=tk.LEFT, padx=5)
    elements.append(create_btn)

    help_btn = tk.Button(btn_frame, text="Ajuda", command=lambda: messagebox.showinfo("Ajuda",
        "Instruções:\n\n"
        "1. Selecione a pasta ORIGINAL (versão antiga)\n"
        "2. Selecione a pasta MODIFICADA (versão nova)\n"
        "3. Escolha onde salvar o arquivo PATCH\n"
        "4. Clique em 'Criar Patch'\n\n"
        "A PASTA ORIGINAL deve conter os arquivos inalterados\n"
        "A PASTA MODIFICADA deve conter os arquivos que foram editados, alterados e/ou modificados.\n"
        "Arquivos adicionados serão incluídos no patch, os alterados serão salvos como delta.\n"
        "O processo pode demorar dependendo do tamanho dos arquivos e da quantidade de alterações."))
    help_btn.pack(side=tk.LEFT, padx=5)
    elements.append(help_btn)

    toggle_btn = tk.Button(btn_frame, text="Alternar Tema", command=lambda: toggle_theme(root, elements))
    toggle_btn.pack(side=tk.LEFT, padx=5)
    elements.append(toggle_btn)

    create_btn.config(command=lambda: run_thread(orig_ent.get(), mod_ent.get(), patch_ent.get(),
                                                 log, progress_bar, status_label, create_btn))

    apply_theme(root, elements)
    root.mainloop()


if __name__ == "__main__":
    build_ui()
