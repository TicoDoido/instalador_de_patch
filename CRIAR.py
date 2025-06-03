# script_create_patch.py
import os
import zlib
import bsdiff4
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Dark theme colors
BG_COLOR = "#2E2E2E"
FG_COLOR = "#FFFFFF"
BTN_BG = "#3A3A3A"
BTN_FG = "#FFFFFF"
ENTRY_BG = "#3A3A3A"
ENTRY_FG = "#FFFFFF"
TEXT_BG = "#1E1E1E"
TEXT_FG = "#FFFFFF"


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
    file = filedialog.asksaveasfilename(defaultextension=".patch", filetypes=[("Patch Files", "*.patch")])
    if file:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file)


def create_patch(original_dir, modified_dir, patch_file, log_widget):
    try:
        modified_files = set()
        for root, _, files in os.walk(modified_dir):
            for name in files:
                rel = os.path.relpath(os.path.join(root, name), modified_dir)
                modified_files.add(rel)

        with open(patch_file, 'wb') as pf:
            for root, _, files in os.walk(original_dir):
                for name in files:
                    orig = os.path.join(root, name)
                    rel = os.path.relpath(orig, original_dir)
                    mod = os.path.join(modified_dir, rel)
                    if os.path.exists(mod):
                        with open(orig, 'rb') as f1, open(mod, 'rb') as f2:
                            d1, d2 = f1.read(), f2.read()
                        if d1 != d2:
                            delta = bsdiff4.diff(d1, d2)
                            comp = zlib.compress(delta, level=9)
                            pf.write(len(rel).to_bytes(4,'little'))
                            pf.write(rel.encode('utf-8'))
                            pf.write((1).to_bytes(1,'little'))
                            pf.write(len(comp).to_bytes(4,'little'))
                            pf.write(comp)
                            log_message(log_widget, f"Patch gerado: {rel}")
                        modified_files.discard(rel)
            for rel in modified_files:
                mod = os.path.join(modified_dir, rel)
                data = open(mod,'rb').read()
                comp = zlib.compress(data, level=9)
                pf.write(len(rel).to_bytes(4,'little'))
                pf.write(rel.encode('utf-8'))
                pf.write((0).to_bytes(1,'little'))
                pf.write(len(comp).to_bytes(4,'little'))
                pf.write(comp)
                log_message(log_widget, f"Arquivo novo: {rel}")
        messagebox.showinfo("Sucesso", f"Patch criado: {patch_file}")
    except Exception as e:
        messagebox.showerror("Erro ao criar patch", str(e))


def run_thread(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()


def build_ui():
    root = tk.Tk()
    root.title("Criar Patch")
    root.configure(bg=BG_COLOR)
    root.geometry("600x300")
    root.resizable(False, False)

    tk.Label(root, text="Pasta Original:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, pady=5, sticky='e')
    orig_ent = tk.Entry(root, width=40, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR)
    orig_ent.grid(row=0, column=1)
    tk.Button(root, text="Selecionar", command=lambda: select_folder(orig_ent), bg=BTN_BG, fg=BTN_FG).grid(row=0, column=2)

    tk.Label(root, text="Pasta Modificada:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, pady=5, sticky='e')
    mod_ent = tk.Entry(root, width=40, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR)
    mod_ent.grid(row=1, column=1)
    tk.Button(root, text="Selecionar", command=lambda: select_folder(mod_ent), bg=BTN_BG, fg=BTN_FG).grid(row=1, column=2)

    tk.Label(root, text="Salvar Patch:", bg=BG_COLOR, fg=FG_COLOR).grid(row=2, column=0, sticky='e')
    patch_ent = tk.Entry(root, width=40, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR)
    patch_ent.grid(row=2, column=1)
    tk.Button(root, text="Salvar", command=lambda: select_file(patch_ent), bg=BTN_BG, fg=BTN_FG).grid(row=2, column=2)

    log = tk.Text(root, height=8, bg=TEXT_BG, fg=TEXT_FG, state=tk.DISABLED)
    log.grid(row=3, column=0, columnspan=3, pady=10)

    tk.Button(root, text="Criar Patch", width=15,
              command=lambda: run_thread(create_patch, orig_ent.get(), mod_ent.get(), patch_ent.get(), log),
              bg="#006400", fg=FG_COLOR).grid(row=4, column=1, pady=10)
    tk.Button(root, text="Ajuda", bg=BTN_BG, fg=BTN_FG, command=lambda: messagebox.showinfo("Ajuda", \
        "1. Selecione pastas e nome do patch.\n2. Clique em 'Criar Patch'.\n3. Backup recomendado."))
    
    root.mainloop()

if __name__ == "__main__":
    build_ui()

