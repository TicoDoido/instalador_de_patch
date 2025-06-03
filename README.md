Instalador de Patchs Personalizados 🛠️  

Este projeto é uma ferramenta em Python para criar instaladores customizados  
de patchs (modificações) para jogos e aplicações. Com ele, você pode empacotar  
uma coleção de arquivos de patch em um único executável instalador, incluindo  
ícones e banners personalizados. É útil para desenvolvedores e modders que  
desejam distribuir mods ou atualizações de forma prática, pois simplifica  
a aplicação dos patchs no computador do usuário.  

Funcionalidades Principais  

Pacote de múltiplos arquivos de patch em um único instalador executável.  
Suporte a arquivos de mídia do instalador (como banner.png e icon.ico)  
para personalizar a interface.  
Geração automática de estrutura de diretórios de instalação para aplicar os patchs.  
Menu ou interface básica (via script) para escolher e aplicar os patchs desejados.  

Requisitos do Sistema 📋  

Python 3.x (recomendado 3.7 ou superior).  
Bibliotecas padrão do Python, como tkinter (GUI), os, zipfile, shutil etc. (já inclusas no Python).  
PyInstaller (opcional): para converter os scripts Python em um executável .exe do Windows.  
Sistema operacional Windows (os scripts .bat e a compilação em .exe são voltados para Windows).  

Instalação e Execução 📝  
Clonar o repositório:  

git clone https://github.com/TicoDoido/instalador_de_patch.git  
cd instalador_de_patch  

Preparar os patchs: Crie uma pasta patchs/ no diretório do projeto  
e coloque nela todos os arquivos de patch que deseja empacotar.  
Configurar (opcional): Personalize o banner (banner.png) e o ícone (icon.ico)  
do instalador substituindo os arquivos padrão.  
Gerar o instalador: Execute o script principal:  

python CRIAR.py  
Esse script irá processar os arquivos de patch e criar os arquivos  
necessários para o instalador.  
Compilar (opcional): Se desejar um único arquivo executável .exe,  
use o arquivo de compilação:  

COMPILAR.bat  

O script .bat geralmente chama o PyInstaller para gerar o instalador  
final. Certifique-se de ter o PyInstaller instalado (pip install pyinstaller).  
Após esses passos, você terá um instalador pronto para distribuir seus patchs.  
Estrutura de Pastas Esperada 📁  
A estrutura básica do projeto deve ser semelhante a:  

instalador_de_patch/  
├─ CRIAR.py  
├─ COMPILAR.bat  
├─ patchs/  
│   ├─ data.patch  
├─ banner.png  
└─ icon.ico  

Coloque todos os arquivos de patch dentro de patchs/ antes de executar o script.  
Os arquivos banner.png e icon.ico são opcionais, servem para personalizar a aparência do instalador.  

Avisos e Limitações ⚠️  
Plataforma: Atualmente, o instalador foi desenvolvido e testado apenas no Windows.  
Status do Projeto: Trata-se de uma ferramenta em fase inicial/protótipo.  
Algumas funcionalidades podem estar incompletas ou em desenvolvimento  
(observado pelos scripts instalador_prototipo.py e instalador_incompleto.py).  

Formatos de Patch: Não há validação automática de formatos específicos;  
certifique-se de que seus arquivos de patch sejam compatíveis com o método  
de aplicação utilizado pelo instalador.  
Uso de Recursos: O script não faz rollback automático; recomenda-se testar em  
ambiente controlado antes de aplicar patches em sistemas importantes.  
Suporte: Este projeto não inclui recursos avançados (logs detalhados, desinstalador, etc.)  
e não oferece suporte formal. Use a ferramenta por sua conta e risco.  

Licença 📄  
Nenhuma licença foi especificada neste repositório. O uso deste código  
fica sujeito às permissões implícitas do autor. Para maiores informações  
sobre uso e distribuição, consulte o mantenedor do projeto.  
