import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import winreg
import sys
import bsdiff4
import zlib
import shutil
import threading
import datetime
from PIL import Image, ImageTk

def resource_path(relative_path):
    """Pega o caminho absoluto para recursos, funcionará quando rodar no PyInstaller."""
    try:
        # Quando rodar como executável PyInstaller, os dados são extraídos em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Instalador da Tradução - Plants Vs Zombies GOTY Steam")
        self.geometry("700x450")  # Altura reduzida para melhor acomodar o banner
        self.resizable(False, False)
        self.frames = []
        self.selected_dir = tk.StringVar()
        self.checkbox_state = tk.StringVar(value="")
        self.credits_next_button = None
        self.banner_image = None
        self.tempo_restante = 10
        self.after_id = None
        self.installation_completed = False
        self.install_button = None
        self.backup_var = tk.BooleanVar(value=True)
        self.current_frame_index = 0

        # Configurar ícone
        self.set_window_icon()

        # Carregar banner com dimensões fixas
        self.banner_width = 200
        self.banner_height = 450
        self.load_banner_image()

        # Detectar caminho de instalação
        self.detect_install_path()

        self.create_pages()
        self.show_frame(0)

    def set_window_icon(self):
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

    def detect_install_path(self):
        """Detecta o caminho de instalação do jogo"""
        possible_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Plants Vs Zombies",
            r"D:\Program Files (x86)\Steam\steamapps\common\Plants Vs Zombies",
            r"E:\Program Files (x86)\Steam\steamapps\common\Plants Vs Zombies",
        ]

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
                custom_path = os.path.join(steam_path, "steamapps", "common", "Plants Vs Zombies")
                possible_paths.insert(0, custom_path)
        except Exception:
            pass

        for path in possible_paths:
            exe_path = os.path.join(path, "PlantsVsZombies.exe")
            if os.path.exists(exe_path):
                self.selected_dir.set(path)
                return

        self.selected_dir.set(r"C:\Program Files (x86)\Steam\steamapps\common\Plants Vs Zombies")

    def load_banner_image(self):
        try:
            image_path = resource_path("banner.png")
            img = Image.open(image_path)
            
            # Redimensionar exatamente para 200x400
            img = img.resize((self.banner_width, self.banner_height), Image.LANCZOS)
            self.banner_image = ImageTk.PhotoImage(img)
        except Exception:
            # Fallback: criar uma imagem sólida com as dimensões especificadas
            self.banner_image = ImageTk.PhotoImage(Image.new("RGB", (self.banner_width, self.banner_height), "#2c3e50"))

    def create_pages(self):
        self.frames.append(self.create_intro_page())
        self.frames.append(self.create_info_page())
        self.frames.append(self.create_credits_page())
        self.frames.append(self.create_install_page())

    def show_frame(self, index):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        for frame in self.frames:
            frame.pack_forget()

        self.frames[index].pack(fill='both', expand=True)
        self.current_frame_index = index

        if index == 2:
            self.tempo_restante = 10
            self.iniciar_contagem_regressiva()
        elif index == 3:
            self.check_installation_status()

    def iniciar_contagem_regressiva(self):
        if self.tempo_restante > 0:
            self.credits_next_button.config(
                text=f"Avançar ({self.tempo_restante}s)",
                state='disabled'
            )
            self.tempo_restante -= 1
            self.after_id = self.after(1000, self.iniciar_contagem_regressiva)
        else:
            self.credits_next_button.config(
                text="Avançar",
                state='normal'
            )

    def create_intro_page(self):
        frame = ttk.Frame(self)

        # Container principal para banner e conteúdo
        main_container = ttk.Frame(frame)
        main_container.pack(fill='both', expand=True)

        # Frame para o banner (lado esquerdo)
        banner_frame = ttk.Frame(main_container)
        banner_frame.pack(side='left', fill='y')

        # Adicionar a imagem do banner
        banner_label = tk.Label(banner_frame, image=self.banner_image)
        banner_label.pack(fill='both', expand=True)

        # Frame para o conteúdo (lado direito)
        content = ttk.Frame(main_container)
        content.pack(side='left', expand=True, fill='both', padx=20, pady=10)  # Padding reduzido

        # Frame para centralizar conteúdo verticalmente
        content_container = ttk.Frame(content)
        content_container.pack(expand=True, fill='both', pady=10)

        ttk.Label(content_container,
                  text="Instalador da Tradução",
                  font=("Helvetica", 18, "bold")).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(content_container,
                  text="Plants vs. Zombies GOTY \"Steam\"",
                  font=("Helvetica", 16, "bold")).pack(anchor='w', pady=(0, 15))

        ttk.Label(content_container,
                  text="Esta ferramenta irá guiá-lo através do processo de instalação da tradução.\n\nClique em 'Avançar' para continuar ou 'Cancelar' para fechar o instalador.",
                  wraplength=450,
                  justify="left").pack(anchor='w', pady=(0, 30))

        button_frame = ttk.Frame(content_container)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))

        ttk.Frame(button_frame).pack(side='left', expand=True)

        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side='right')

        ttk.Button(btn_container,
                  text="Cancelar",
                  command=self.quit).pack(side='left', padx=5)

        ttk.Button(btn_container,
                  text="Avançar",
                  command=lambda: self.show_frame(1)).pack(side='left', padx=5)

        return frame

    def create_info_page(self):
        frame = ttk.Frame(self)

        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=20, pady=15)  # Padding ajustado

        ttk.Label(content,
                  text="Informações Importantes",
                  font=("Segoe UI", 14, "bold")).pack(anchor='w', pady=(0, 10))

        info_frame = ttk.Frame(content)
        info_frame.pack(fill='x', pady=(0, 15))

        info_text = (
            "• Este instalador é para a versão \"Steam\" do Plants Vs Zombies GOTY Edition\n"
            "• Feche o jogo antes de iniciar a instalação\n"
            "• É recomendado fazer um backup dos arquivos originais\n"
            "• A instalação aplicará um patch delta (data.patch) aos arquivos do jogo\n\n"
            "Selecione o diretório de instalação do jogo:"
        )
        ttk.Label(info_frame,
                  text=info_text,
                  wraplength=650,
                  justify="left").pack(anchor='w')

        dir_frame = ttk.Frame(content)
        dir_frame.pack(fill='x', pady=(0, 10))

        ttk.Entry(dir_frame,
                  textvariable=self.selected_dir,
                  width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame,
                  text="Procurar",
                  command=self.browse_directory,
                  width=10).pack(side='left', padx=5)

        self.path_status = ttk.Label(content, text="", foreground="red")
        self.path_status.pack(anchor='w', pady=(0, 15))
        self.verify_path()

        ttk.Label(content,
                  text="Você concorda com os termos acima?",
                  font=("Segoe UI", 9)).pack(anchor='w', pady=(0, 5))

        terms_frame = ttk.Frame(content)
        terms_frame.pack(anchor='w', pady=(0, 15))

        ttk.Radiobutton(terms_frame,
                        text="Sim, concordo e desejo continuar",
                        variable=self.checkbox_state,
                        value="agree",
                        command=self.update_next_button_state).pack(anchor='w')

        ttk.Radiobutton(terms_frame,
                        text="Não concordo",
                        variable=self.checkbox_state,
                        value="disagree",
                        command=self.update_next_button_state).pack(anchor='w', pady=5)

        button_frame = ttk.Frame(content)
        button_frame.pack(side='bottom', fill='x', pady=(10, 5))

        ttk.Frame(button_frame).pack(side='left', expand=True)

        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side='right')

        ttk.Button(btn_container,
                  text="Voltar",
                  command=lambda: self.show_frame(0),
                  width=10).pack(side='left', padx=5)

        ttk.Button(btn_container,
                  text="Cancelar",
                  command=self.quit,
                  width=10).pack(side='left', padx=5)

        self.info_next_button = ttk.Button(btn_container,
                                           text="Avançar",
                                           state="disabled",
                                           command=lambda: self.show_frame(2),
                                           width=10)
        self.info_next_button.pack(side='left', padx=5)

        return frame

    def verify_path(self):
        path = self.selected_dir.get()
        if not path:
            self.path_status.config(text="Selecione um diretório válido", foreground="red")
            return False

        exe_path = os.path.join(path, "PlantsVsZombies.exe")

        if not os.path.exists(path):
            self.path_status.config(text="Diretório não encontrado", foreground="red")
            return False
        elif not os.path.exists(exe_path):
            self.path_status.config(text="Executável do jogo não encontrado", foreground="red")
            return False
        elif not os.access(path, os.W_OK):
            self.path_status.config(text="Sem permissão de escrita no diretório", foreground="red")
            return False
        else:
            self.path_status.config(text="Caminho válido - Pronto para instalação", foreground="green")
            return True

    def browse_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_dir.set(path)
            self.verify_path()

    def update_next_button_state(self):
        if self.checkbox_state.get() == "agree" and self.verify_path():
            self.info_next_button.config(state='normal')
        else:
            self.info_next_button.config(state='disabled')

    def create_credits_page(self):
        frame = ttk.Frame(self)
        
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=20, pady=10)  # Padding ajustado
        
        ttk.Label(content, 
                 text="Créditos da Tradução", 
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        ttk.Label(content, 
                 text="Esta tradução foi possível graças ao trabalho de:",
                 font=("Segoe UI", 9)).pack(pady=(0, 10))
        
        border_frame = ttk.Frame(content, relief="solid", borderwidth=2)
        border_frame.pack(fill='x', padx=15, pady=5)
        
        credits_container = ttk.Frame(border_frame, padding=8)
        credits_container.pack(fill='both', expand=True)
        
        credits = [
            ("Tradução:", "Carlos Emmanuel, Heitor Spectre, Giga e Oficial"),
            ("Revisão:", "Heitor Spectre e Carlos Emmanuel"),
            ("Texturas:", "Niccbilac, Heitor Spectre, Kiel, Evil Trainer,"),
            ("", "Carlos Emmanuel, João 13 e Oficial"),
            ("Testes:", "Heitor Spectre e Carlos Emmanuel"),
            ("Criadores do Instalador:", "Tico Doido, Niccbilac, Heitor Spectre")
        ]
        
        for role, names in credits:
            credit_frame = ttk.Frame(credits_container)
            credit_frame.pack(fill='x', padx=5, pady=2)
            
            title_label = ttk.Label(credit_frame, text=role, 
                                  font=("Segoe UI", 10, "bold"),
                                  width=22, anchor='e')
            title_label.pack(side='left')
            
            names_label = ttk.Label(credit_frame, text=names, 
                                   font=("Segoe UI", 10),
                                   anchor='w')
            names_label.pack(side='left', padx=5, fill='x', expand=True)
        
        special_frame = ttk.Frame(credits_container)
        special_frame.pack(fill='x', padx=5, pady=(10, 2))
        
        ttk.Label(special_frame, 
                 text="Agradecimento Especial:", 
                 font=("Segoe UI", 10, "bold"),
                 width=22, anchor='e').pack(side='left')
                 
        ttk.Label(special_frame, 
                 text="Tico Doido", 
                 font=("Segoe UI", 10),
                 anchor='w').pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Frame(content).pack(fill='y', expand=True)
        
        button_frame = ttk.Frame(content)
        button_frame.pack(side='bottom', fill='x', pady=(5, 5))
        
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side='right')

        ttk.Button(btn_container,
                  text="Voltar",
                  command=lambda: self.show_frame(1),
                  width=10).pack(side='left', padx=5)
        
        self.credits_next_button = ttk.Button(btn_container, 
                                            text="Avançar", 
                                            state="disabled",
                                            command=lambda: self.show_frame(3),
                                            width=12)
        self.credits_next_button.pack(side='left', padx=5)

        return frame

    def create_install_page(self):
        frame = ttk.Frame(self)

        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=15)  # Padding ajustado

        ttk.Label(content,
                  text="Instalação da Tradução",
                  font=("Segoe UI", 16, "bold")).pack(pady=(5, 15))

        ttk.Label(content,
                  text="O instalador irá aplicar o patch de tradução aos arquivos do jogo.",
                  font=("Segoe UI", 10)).pack(pady=(0, 5))
        
        ttk.Label(content,
                  text="Por favor, não feche o programa durante o processo.",
                  font=("Segoe UI", 9, "italic")).pack(pady=(0, 15))

        backup_frame = ttk.Frame(content)
        backup_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Checkbutton(backup_frame, 
                       text="Deseja criar um backup dos arquivos originais antes de instalar? (Altamente recomendável)",
                       variable=self.backup_var,
                       onvalue=True,
                       offvalue=False).pack(anchor='w')

        progress_frame = ttk.Frame(content)
        progress_frame.pack(fill='x', pady=(5, 15))

        self.status_label = ttk.Label(progress_frame,
                                      text="Pronto para iniciar a instalação",
                                      font=("Segoe UI", 10))
        self.status_label.pack(anchor='w', pady=(0, 5))

        s = ttk.Style()
        s.theme_use('clam')
        s.configure("green.Horizontal.TProgressbar", foreground='#2ecc71', background='#2ecc71')
        
        self.progress = ttk.Progressbar(progress_frame, 
                                      orient="horizontal", 
                                      length=500, 
                                      mode="determinate",
                                      style="green.Horizontal.TProgressbar")
        self.progress.pack(fill='x', pady=5)

        button_frame = ttk.Frame(content)
        button_frame.pack(side='bottom', fill='x', pady=(0, 5))

        ttk.Frame(button_frame).pack(side='left', expand=True)

        btn_container = ttk.Frame(button_frame)
        btn_container.pack(side='right')

        ttk.Button(btn_container,
                  text="Voltar",
                  command=lambda: self.show_frame(2),
                  width=10).pack(side='left', padx=5)

        ttk.Button(btn_container,
                  text="Cancelar",
                  command=self.quit,
                  width=10).pack(side='left', padx=5)

        self.install_button = ttk.Button(btn_container,
                  text="Iniciar Instalação",
                  command=self.start_installation_thread,
                  width=15)
        self.install_button.pack(side='left', padx=5)

        return frame

    def check_installation_status(self):
        target_dir = self.selected_dir.get()
        if not target_dir:
            return
            
        log_file = os.path.join(target_dir, "install.log")
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    if "Instalação: Sim" in content:
                        self.installation_completed = True
                        self.install_button.config(text="Tradução Já Instalada", state='disabled')
                        self.status_label.config(text="A tradução já foi instalada anteriormente.")
            except:
                pass

    def create_backup(self, target_dir, files_to_backup):
        """Cria um backup dos arquivos originais ANTES da instalação"""
        backup_dir = os.path.join(target_dir, "backup")
        os.makedirs(backup_dir, exist_ok=True)
        
        backed_up_files = 0
        total_files = len(files_to_backup)
        
        for rel_path in files_to_backup:
            src_path = os.path.join(target_dir, rel_path)
            dest_path = os.path.join(backup_dir, rel_path)
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            if os.path.exists(src_path):
                try:
                    # Copia o arquivo ORIGINAL antes de qualquer modificação
                    shutil.copy2(src_path, dest_path)
                    backed_up_files += 1
                    
                    progress_percent = int((backed_up_files / total_files) * 50)
                    self.progress["value"] = progress_percent
                    self.status_label.config(text=f"Criando backup: {rel_path} ({progress_percent}%)")
                    self.update_idletasks()
                except Exception as e:
                    print(f"Erro ao criar backup de {rel_path}: {str(e)}")
        
        return backup_dir

    def create_uninstaller(self, target_dir):
        """Cria o desinstalador em um local seguro (diretório do jogo)"""
        # Usar o diretório do jogo em vez de Program Files
        uninstaller_dir = os.path.join(target_dir, "Central do PS3")
        os.makedirs(uninstaller_dir, exist_ok=True)
        
        uninstaller_path = os.path.join(uninstaller_dir, "desinstalar_traducao.bat")
        
        # Script simplificado que opera apenas no diretório do jogo
        script_content = f"""@echo off
echo Desinstalando a tradução do Plants Vs Zombies...
echo.

set "game_dir=%~dp0.."
cd /d "%game_dir%"

if not exist "backup" (
    echo Erro: Pasta de backup não encontrada!
    echo A desinstalação não pode ser concluída.
    pause
    exit /b 1
)

echo Restaurando arquivos originais do backup...
xcopy /E /Y /I "backup" .

echo Removendo arquivos de controle...
del "install.log"

echo Apagando a pasta de backup...
rmdir /S /Q "backup"

echo Desinstalação concluída com sucesso!
echo O jogo foi restaurado para o estado original.
echo.
pause
"""
        
        try:
            with open(uninstaller_path, 'w') as f:
                f.write(script_content)
            return uninstaller_path
        except Exception as e:
            print(f"Erro ao criar desinstalador: {str(e)}")
            return ""

    def start_installation_thread(self):
        if self.installation_completed:
            return
            
        self.install_button.config(state='disabled')
        self.status_label.config(text="Preparando a instalação...")
        self.update_idletasks()
        
        install_thread = threading.Thread(target=self.perform_installation)
        install_thread.daemon = True
        install_thread.start()

    def perform_installation(self):
        target_dir = self.selected_dir.get()
        patch_path = resource_path("data.patch")
        log_file = os.path.join(target_dir, "install.log")

        if not self.verify_path():
            messagebox.showerror("Erro", "Por favor, selecione um caminho válido antes de instalar")
            self.install_button.config(state='normal')
            return

        if not os.path.exists(patch_path):
            messagebox.showerror("Erro", f"Arquivo de patch não encontrado:\n{patch_path}")
            self.install_button.config(state='normal')
            return

        try:
            # Passo 1: Ler o patch para obter a lista de arquivos
            entries = []
            files_to_backup = []
            with open(patch_path, 'rb') as pf:
                while True:
                    size_bytes = pf.read(4)
                    if not size_bytes or len(size_bytes) < 4:
                        break
                    path_len = int.from_bytes(size_bytes, 'little')

                    rel_path_bytes = pf.read(path_len)
                    rel_path = rel_path_bytes.decode('utf-8')

                    files_to_backup.append(rel_path)

                    flag_byte = pf.read(1)
                    flag = int.from_bytes(flag_byte, 'little')

                    comp_size = int.from_bytes(pf.read(4), 'little')

                    comp_data = pf.read(comp_size)

                    entries.append((rel_path, flag, comp_data))

            # Passo 2: Criar backup ANTES de aplicar qualquer modificação
            backup_created = False
            if self.backup_var.get():
                self.status_label.config(text="Criando backup dos arquivos originais...")
                self.create_backup(target_dir, files_to_backup)
                backup_created = True

            total_entries = len(entries)
            applied_count = 0

            # Passo 3: Aplicar o patch DEPOIS do backup
            for rel_path, flag, comp_data in entries:
                applied_count += 1
                progress_percent = 50 + int((applied_count / total_entries) * 50)
                self.progress["value"] = progress_percent
                self.status_label.config(text=f"Aplicando patch: {rel_path} ({progress_percent}%)")
                self.update_idletasks()

                full_target_path = os.path.join(target_dir, rel_path)
                full_target_dir = os.path.dirname(full_target_path)
                os.makedirs(full_target_dir, exist_ok=True)

                data = zlib.decompress(comp_data)

                if flag == 1:
                    if not os.path.exists(full_target_path):
                        raise FileNotFoundError(f"Arquivo original ausente para aplicar delta: {rel_path}")

                    with open(full_target_path, 'rb') as orig_f:
                        orig_data = orig_f.read()

                    new_data = bsdiff4.patch(orig_data, data)

                    with open(full_target_path, 'wb') as out_f:
                        out_f.write(new_data)

                else:
                    with open(full_target_path, 'wb') as out_f:
                        out_f.write(data)

            # Atualização final
            self.progress["value"] = 100
            self.status_label.config(text="Patch aplicado com sucesso!")
            self.update_idletasks()
            
            # Criar arquivo de log
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Instalação: Sim\n")
                f.write(f"Backup: {'Sim' if backup_created else 'Não'}\n")
                f.write(f"Data da instalação: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Diretório do jogo: {target_dir}\n")
            
            # Criar desinstalador (com tratamento de erro)
            uninstaller_path = ""
            if backup_created:
                try:
                    uninstaller_path = self.create_uninstaller(target_dir)
                    if not uninstaller_path:
                        messagebox.showwarning("Aviso", 
                                             "O desinstalador não pôde ser criado, mas a instalação foi concluída.\n\n" 
                                             "Você pode restaurar manualmente os arquivos usando a pasta 'backup'.")
                except Exception as e:
                    messagebox.showwarning("Aviso", 
                                         f"O desinstalador não pôde ser criado: {str(e)}\n\n"
                                         "A instalação foi concluída, mas você precisará restaurar manualmente os arquivos usando a pasta 'backup'.")
            
            # Atualizar UI
            self.installation_completed = True
            self.install_button.config(text="Instalação Concluída", state='disabled')
            
            # Mensagem de sucesso
            success_msg = "O patch delta foi aplicado com êxito!\n\nO jogo está pronto para ser executado."
            if backup_created and uninstaller_path:
                success_msg += f"\n\nUm desinstalador foi criado em:\n{uninstaller_path}"
            
            messagebox.showinfo("Sucesso", success_msg)

        except FileNotFoundError as fnf_err:
            messagebox.showerror("Erro", str(fnf_err))
            self.status_label.config(text="Erro durante a aplicação do patch")
            self.install_button.config(state='normal')
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na aplicação do patch: {str(e)}")
            self.status_label.config(text="Erro durante a aplicação do patch")
            self.install_button.config(state='normal')

if __name__ == "__main__":
    try:
        app = InstallerApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado:\n{str(e)}")
        sys.exit(1)
