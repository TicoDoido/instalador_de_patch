# Recursos Destacados  

✅ Empacotamento de múltiplos patches em único executável  
🎨 Personalização completa da interface (banners/ícones)  
📁 Geração automática de estrutura de diretórios  
🖥️ Interface gráfica amigável (tkinter)  
🚀 Compilação para .exe (Windows)  

# COMO FUNCIONA:  
Use o CRIAR.py para criar o patch, ele vai gerar um delta unico   
comparando os arquivos de uma pasta de um jogo com tudo original   
e outra pasta (a mesma) porem com os arquivos que foram alterados   
Arquivos adicionados também serão incluídos no patch  
Altere o banner.png o icon.ico e os textos dentro do instalador.py  
para personalizar de acordo com o seu projeto   
Deixei um modelo que instala patch em xdelta também  
  
📦 Requisitos do Sistema  
Componente	\ Versão Mínima	Recomendada  
Python	\ 3.6	3.10+  
PyInstaller	\ 5.8+  
Sistema	Windows 10	Windows 11  

# 🚀 Começando Rápido  
Pré-requisitos  

instale os módulos necessários  

pip install pyinstaller  
pip install bsfdiff4  

Configuração Inicial  
Clone o repositório:  
  
git clone https://github.com/TicoDoido/instalador_de_patch.git  
cd instalador_de_patch  
  
# Copie seu arquivo data.patch para esta pasta  
Gerando Instalador  

python CRIAR.py  # Cria os arquivos base  
COMPILAR.bat     # Gera o executável final  
🗂️ Estrutura do Projeto  
instalador_de_patch/  
├── 📁 dist/                   # Executáveis gerados  
├── 📄 CRIAR.py                # Script de construção  
├── 📄 COMPILAR.bat            # Script de compilação  
├── 🖼️ banner.png              # Banner personalizável  
├── 🎯 icon.ico                # Ícone personalizável  
└── 📄 instalador.py           # Lógica principal  

🧪 Testando e Contribuindo  

# Rodar em modo desenvolvimento  
python instalador.py  
Contribuições são bem-vindas! Siga estes passos:  
  
Fork o repositório  
  
Crie sua branch (git checkout -b feature/nova-funcionalidade)  
  
Commit suas mudanças (git commit -m 'Adiciona incrível funcionalidade')  
  
Push para a branch (git push origin feature/nova-funcionalidade)  
  
Abra um Pull Request  
  
⚠️ Limitações Atuais  
Compatibilidade apenas com Windows  
Sem sistema de rollback automático  
Validação limitada de formatos de patch  
  
📬 Suporte e Contato  
Encontrou problemas? Abra uma issue  
  
📄 Licença  
Este projeto está em discussão para adoção de licença. Enquanto isso:  
  
Você pode usar e modificar o código, mas redistribuição comercial
requer permissão expressa do autor.  
  
Você pode personalizar o banner.png e o icon.ico (256x256px) para dar  
identidade visual ao projeto!  
