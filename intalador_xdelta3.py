import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import winreg
import sys
import zlib
import shutil
import threading
import datetime
import hashlib
import subprocess
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
        
        # Configurar tema escuro
        self.dark_bg = "#1e1e1e"
        self.dark_fg = "#e0e0e0"
        self.dark_accent = "#2c2c2c"
        self.dark_highlight = "#3498db"
        self.dark_success = "#2ecc71"
        self.dark_error = "#e74c3c"
        self.dark_text = "#b0b0b0"
        
        self.title("Instalador da Tradução - Shadows of the Damned: Hella Remastered")
        self.geometry("700x450")
        self.resizable(False, False)
        self.configure(bg=self.dark_bg)
        
        # Configurar estilo
        self.setup_styles()
        
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

    def setup_styles(self):
        """Configura os estilos para o modo escuro"""
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Configurações gerais
        style.configure('.', 
                        background=self.dark_bg,
                        foreground=self.dark_fg,
                        fieldbackground=self.dark_accent,
                        selectbackground=self.dark_highlight,
                        selectforeground=self.dark_fg,
                        troughcolor=self.dark_accent,
                        highlightcolor=self.dark_highlight,
                        insertcolor=self.dark_fg)
        
        # Frames
        style.configure('TFrame', background=self.dark_bg)
        style.configure('Dark.TFrame', background=self.dark_accent)
        
        # Labels
        style.configure('TLabel', background=self.dark_bg, foreground=self.dark_fg)
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12))
        style.configure('Info.TLabel', foreground=self.dark_text)
        
        # Botões
        style.configure('TButton', 
                        background=self.dark_accent,
                        foreground=self.dark_fg,
                        borderwidth=1,
                        focusthickness=0,
                        focuscolor='none')
        style.map('TButton',
                  background=[('active', self.dark_highlight), ('disabled', '#333333')],
                  foreground=[('active', 'white'), ('disabled', '#7f8c8d')])
        
        # Entradas
        style.configure('TEntry', 
                        fieldbackground=self.dark_accent,
                        foreground=self.dark_fg,
                        insertcolor=self.dark_fg,
                        bordercolor=self.dark_accent,
                        lightcolor=self.dark_accent,
                        darkcolor=self.dark_accent)
        
        # Checkbuttons e Radiobuttons
        style.configure('TCheckbutton', background=self.dark_bg, foreground=self.dark_fg)
        style.configure('TRadiobutton', background=self.dark_bg, foreground=self.dark_fg)
        
        # Barra de progresso
        style.configure('Horizontal.TProgressbar', 
                        background=self.dark_highlight,
                        troughcolor=self.dark_accent,
                        bordercolor=self.dark_accent,
                        lightcolor=self.dark_highlight,
                        darkcolor=self.dark_highlight)

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
            r"C:\Program Files (x86)\Steam\steamapps\common\ShadowsoftheDamnedHellaRemastered",
            r"D:\Program Files (x86)\Steam\steamapps\common\ShadowsoftheDamnedHellaRemastered",
            r"E:\Program Files (x86)\Steam\steamapps\common\ShadowsoftheDamnedHellaRemastered",
        ]

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
                custom_path = os.path.join(steam_path, "steamapps", "common", "Shadows of the Damned Hella Remastered")
                possible_paths.insert(0, custom_path)
        except Exception:
            pass

        for path in possible_paths:
            exe_path = os.path.join(path, "game.exe")
            if os.path.exists(exe_path):
                self.selected_dir.set(path)
                return

        self.selected_dir.set(r"C:\Program Files (x86)\Steam\steamapps\common\ShadowsoftheDamnedHellaRemastered")

    def load_banner_image(self):
        try:
            image_path = resource_path("banner.png")
            img = Image.open(image_path)
            img = img.resize((self.banner_width, self.banner_height), Image.LANCZOS)
            self.banner_image = ImageTk.PhotoImage(img)
        except Exception:
            # Criar banner padrão com tema escuro
            img = Image.new("RGB", (self.banner_width, self.banner_height), self.dark_bg)
            self.banner_image = ImageTk.PhotoImage(img)

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
        frame = ttk.Frame(self, style='TFrame')

        # Container principal para banner e conteúdo
        main_container = ttk.Frame(frame)
        main_container.pack(fill='both', expand=True)

        # Frame para o banner (lado esquerdo)
        banner_frame = ttk.Frame(main_container)
        banner_frame.pack(side='left', fill='y')

        # Adicionar a imagem do banner
        banner_label = tk.Label(banner_frame, image=self.banner_image, bg=self.dark_bg)
        banner_label.pack(fill='both', expand=True)

        # Frame para o conteúdo (lado direito)
        content = ttk.Frame(main_container)
        content.pack(side='left', expand=True, fill='both', padx=20, pady=10)

        # Frame para centralizar conteúdo verticalmente
        content_container = ttk.Frame(content)
        content_container.pack(expand=True, fill='both', pady=10)

        ttk.Label(content_container,
                  text="Instalador da Tradução",
                  style='Title.TLabel').pack(anchor='w', pady=(0, 5))
        
        ttk.Label(content_container,
                  text="Shadows of the Damned: Hella Remastered",
                  style='Subtitle.TLabel').pack(anchor='w', pady=(0, 15))

        ttk.Label(content_container,
                  text="Esta ferramenta irá guiá-lo através do processo de instalação da tradução.\n\nClique em 'Avançar' para continuar ou 'Cancelar' para fechar o instalador.",
                  style='TLabel',
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
        frame = ttk.Frame(self, style='TFrame')

        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=20, pady=15)

        ttk.Label(content,
                  text="Informações Importantes",
                  style='Title.TLabel').pack(anchor='w', pady=(0, 10))

        info_frame = ttk.Frame(content)
        info_frame.pack(fill='x', pady=(0, 15))

        info_text = (
            "• Este instalador é para a versão \"Steam\" do Shadows of the Damned: Hella Remastered\n"
            "• Feche o jogo antes de iniciar a instalação\n"
            "• É recomendado fazer um backup dos arquivos originais\n\n"
            "Selecione o diretório de instalação do jogo:"
        )
        ttk.Label(info_frame,
                  text=info_text,
                  style='TLabel',
                  wraplength=650,
                  justify="left").pack(anchor='w')

        dir_frame = ttk.Frame(content)
        dir_frame.pack(fill='x', pady=(0, 10))

        entry = ttk.Entry(dir_frame,
                  textvariable=self.selected_dir,
                  width=60)
        entry.pack(side='left', fill='x', expand=True)
        
        # Configurar cor do texto para a entrada
        entry.configure(style='TEntry')
        
        ttk.Button(dir_frame,
                  text="Procurar",
                  command=self.browse_directory,
                  width=10).pack(side='left', padx=5)

        self.path_status = ttk.Label(content, text="", foreground=self.dark_error)
        self.path_status.pack(anchor='w', pady=(0, 15))
        self.verify_path()

        ttk.Label(content,
                  text="Você concorda com os termos acima?",
                  style='TLabel').pack(anchor='w', pady=(0, 5))

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
            self.path_status.config(text="Selecione um diretório válido", foreground=self.dark_error)
            return False

        exe_path = os.path.join(path, "game.exe")
        data_vfs_path = os.path.join(path, "fishgame\\data.vfs")

        if not os.path.exists(path):
            self.path_status.config(text="Diretório não encontrado", foreground=self.dark_error)
            return False
        elif not os.path.exists(exe_path):
            self.path_status.config(text="Executável do jogo não encontrado", foreground=self.dark_error)
            return False
        elif not os.path.exists(data_vfs_path):
            self.path_status.config(text="Arquivo data.vfs não encontrado", foreground=self.dark_error)
            return False
        elif not os.access(path, os.W_OK):
            self.path_status.config(text="Sem permissão de escrita no diretório", foreground=self.dark_error)
            return False
        else:
            self.path_status.config(text="Caminho válido - Pronto para instalação", foreground=self.dark_success)
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
        frame = ttk.Frame(self, style='TFrame')
        
        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Label(content, 
                 text="Créditos da Tradução", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        ttk.Label(content, 
                 text="Esta tradução foi possível graças ao trabalho de:",
                 style='TLabel').pack(pady=(0, 10))
        
        # Frame com fundo mais escuro para os créditos
        border_frame = ttk.Frame(content, style='Dark.TFrame', padding=5)
        border_frame.pack(fill='x', padx=15, pady=5)
        
        credits_container = ttk.Frame(border_frame)
        credits_container.pack(fill='both', expand=True, padx=3, pady=3)
        
        credits = [
            ("Líder do Projeto:", "Giga"),
            ("Tradução:", "Carlos Emmanuel, Niccbilac, Kiel e Giga"),
            ("Revisão:", "Carlos Emmanuel e Niccbilac"),
            ("Texturas:", "Evil Trainer e Giga"),
            ("Testes:", "João13 e Giga"),
            ("Criadores do Instalador:", "TicoDoido, Niccbilac, Heitor Spectre")
        ]
        
        for role, names in credits:
            credit_frame = ttk.Frame(credits_container)
            credit_frame.pack(fill='x', padx=5, pady=2)
            
            title_label = ttk.Label(credit_frame, text=role, 
                                  style='TLabel',
                                  width=22, anchor='e')
            title_label.pack(side='left')
            
            names_label = ttk.Label(credit_frame, text=names, 
                                   style='TLabel',
                                   anchor='w')
            names_label.pack(side='left', padx=5, fill='x', expand=True)
        
        special_frame = ttk.Frame(credits_container)
        special_frame.pack(fill='x', padx=5, pady=(10, 2))
        
        ttk.Label(special_frame, 
                 text="Agradecimento Especial:", 
                 style='TLabel',
                 width=22, anchor='e').pack(side='left')
                 
        ttk.Label(special_frame, 
                 text="Evil Trainer", 
                 style='TLabel',
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
        frame = ttk.Frame(self, style='TFrame')

        content = ttk.Frame(frame)
        content.pack(fill='both', expand=True, padx=30, pady=15)

        ttk.Label(content,
                  text="Instalação da Tradução",
                  style='Title.TLabel').pack(pady=(5, 15))

        ttk.Label(content,
                  text="O instalador irá aplicar o patch de tradução ao arquivo data.vfs do jogo.",
                  style='Subtitle.TLabel').pack(pady=(0, 5))
        
        ttk.Label(content,
                  text="Por favor, não feche o programa durante o processo.",
                  style='Info.TLabel').pack(pady=(0, 15))

        backup_frame = ttk.Frame(content)
        backup_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Checkbutton(backup_frame, 
                       text="Deseja criar um backup dos arquivos originais antes de instalar? (Altamente recomendável)",
                       variable=self.backup_var,
                       style='TCheckbutton',
                       onvalue=True,
                       offvalue=False).pack(anchor='w')

        progress_frame = ttk.Frame(content)
        progress_frame.pack(fill='x', pady=(5, 15))

        self.status_label = ttk.Label(progress_frame,
                                      text="Pronto para iniciar a instalação",
                                      style='TLabel')
        self.status_label.pack(anchor='w', pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, 
                                      orient="horizontal", 
                                      length=500, 
                                      mode="determinate")
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
        
        for file_path in files_to_backup:
            src_path = os.path.join(target_dir, file_path)
            dest_path = os.path.join(backup_dir, file_path)
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            if os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, dest_path)
                except Exception as e:
                    print(f"Erro ao criar backup de {file_path}: {str(e)}")
        
        return backup_dir

    def create_uninstaller(self, target_dir):
        """Cria o desinstalador em um local seguro (diretório do jogo)"""
        uninstaller_dir = os.path.join(target_dir, "Central do PS3")
        os.makedirs(uninstaller_dir, exist_ok=True)
        
        uninstaller_path = os.path.join(uninstaller_dir, "desinstalar_traducao.bat")
        
        script_content = """@echo off
echo Desinstalando a tradução do Shadows of the Damned: Hella Remastered...
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
copy /Y "backup\\data.vfs" . >nul

echo Removendo arquivos de controle...
del "install.log"

echo Removendo arquivos de tradução desnecessários...
rmdir /S /Q "backup" 2>nul

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
        self.progress["value"] = 0
        self.update_idletasks()
        
        install_thread = threading.Thread(target=self.perform_installation)
        install_thread.daemon = True
        install_thread.start()

    def run_xdelta(self, patch_path, original_path, output_path):
        """Executa o xdelta para aplicar o patch"""
        # Localizar o xdelta3.exe nos recursos
        xdelta_path = resource_path("xdelta3.exe")
        
        if not os.path.exists(xdelta_path):
            raise FileNotFoundError("xdelta3.exe não encontrado nos recursos")
        
        command = [
            xdelta_path,
            "-d",  # Modo decodificação (aplicar patch)
            "-s", original_path,  # Arquivo original
            patch_path,  # Arquivo de patch
            output_path   # Arquivo de saída
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore') or result.stdout.decode('utf-8', errors='ignore')
                raise RuntimeError(f"Erro ao aplicar patch (código {result.returncode}): {error_msg}")
            
        except Exception as e:
            raise RuntimeError(f"Falha ao executar xdelta3: {str(e)}")

    def perform_installation(self):
        target_dir = self.selected_dir.get()
        patch_path = resource_path("sotd.xdelta")
        original_file = os.path.join(target_dir, "fishgame\\data.vfs")
        log_file = os.path.join(target_dir, "install.log")
        temp_output = os.path.join(target_dir, "fishgame\\data.vfs.tmp")

        # Criar backup se necessário
        backup_created = False
        if self.backup_var.get():
            self.status_label.config(text="Criando backup do arquivo original...")
            self.progress["value"] = 20
            self.update_idletasks()
            
            try:
                self.create_backup(target_dir, ["data.vfs"])
                backup_created = True
            except Exception as e:
                messagebox.showwarning("Aviso", 
                                     f"O backup não pôde ser criado: {str(e)}\n\n"
                                     "Deseja continuar sem backup?",
                                     icon=messagebox.WARNING)
                if messagebox.askyesno("Continuar?", "Continuar sem backup?"):
                    backup_created = False
                else:
                    self.status_label.config(text="Instalação cancelada")
                    self.install_button.config(state='normal')
                    return

        # Aplicar o patch
        try:
            self.status_label.config(text="Aplicando patch... (Isso pode levar alguns minutos)")
            self.progress["value"] = 40
            self.update_idletasks()
            
            # Executar xdelta para aplicar o patch
            self.run_xdelta(patch_path, original_file, temp_output)
            
            # Substituir o arquivo original pelo patchado
            os.replace(temp_output, original_file)
            
            self.status_label.config(text="Patch aplicado com sucesso! Já pode fechar os instalador")
            self.progress["value"] = 100
            self.update_idletasks()
            
            # Criar arquivo de log
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Instalação: Sim\n")
                f.write(f"Backup: {'Sim' if backup_created else 'Não'}\n")
                f.write(f"Data da instalação: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Diretório do jogo: {target_dir}\n")
            
            # Criar desinstalador
            uninstaller_path = ""
            if backup_created:
                try:
                    uninstaller_path = self.create_uninstaller(target_dir)
                except Exception as e:
                    messagebox.showwarning("Aviso", 
                                         f"O desinstalador não pôde ser criado: {str(e)}\n\n"
                                         "A instalação foi concluída, mas você precisará restaurar manualmente o arquivo usando a pasta 'backup'.")
            
            # Atualizar UI
            self.installation_completed = True
            self.install_button.config(text="Instalação Concluída", state='disabled')
            
            # Mensagem de sucesso
            success_msg = "O patch foi aplicado com êxito!\n\nO jogo está pronto para ser executado."
            if backup_created and uninstaller_path:
                success_msg += f"\n\nUm desinstalador foi criado em:\n{uninstaller_path}"
            
            messagebox.showinfo("Sucesso", success_msg)

        except Exception as e:
            # Restaurar backup se a instalação falhou
            if backup_created:
                try:
                    backup_file = os.path.join(target_dir, "backup", "data.vfs")
                    if os.path.exists(backup_file):
                        os.replace(backup_file, original_file)
                        messagebox.showinfo("Restauração", 
                                          "A instalação falhou, mas o arquivo original foi restaurado do backup.")
                except Exception as restore_error:
                    messagebox.showerror("Erro Crítico", 
                                        f"Falha na instalação e na restauração:\n{str(e)}\n\n"
                                        f"Erro na restauração: {str(restore_error)}\n\n"
                                        "Você precisará verificar manualmente o arquivo data.vfs.")
            
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