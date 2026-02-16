# Guia: Transformando o Controle AOC em um App (APK)

Para disponibilizar o download do seu aplicativo via QR Code no seu site, você precisa compilar o código em um arquivo APK (para Android). Como o projeto usa **Kivy**, a ferramenta recomendada é o **Buildozer**.

## 1. Como Gerar o APK

### Opção A: Usando Google Colab (Recomendado - Mais Fácil)
Se você não tem Linux instalado, pode usar o Google Colab para compilar:
1. Vá para o [Google Colab](https://colab.research.google.com/).
2. Faça upload da pasta do projeto (ZIP).
3. Execute os seguintes comandos em uma célula:
   ```bash
   !pip install buildozer
   !pip install cython==0.29.33
   !sudo apt-get install -y scons libncurses5-dev libncursesw5-dev libyaml-dev libssl-dev
   !buildozer init
   !buildozer -v android debug
   ```
4. O arquivo `.apk` será gerado na pasta `bin/`.

### Opção B: Usando Linux Local
1. Instale o Buildozer: `pip install buildozer`
2. Na pasta do projeto, execute: `buildozer android debug`

## 2. Como Disponibilizar para Download via QR Code

### Passo 1: Hospedar o APK
Você precisa colocar o arquivo APK em um local acessível pela internet.
- **Opção 1 (Próprio Site):** Faça upload do arquivo `ControleAOC.apk` para a pasta de arquivos do seu servidor (ex: `seusite.com/downloads/ControleAOC.apk`).
- **Opção 2 (Google Drive/Dropbox):** Faça upload, coloque como "Público para qualquer pessoa com o link" e use um encurtador de links (como Bitly) para obter um link direto.

### Passo 2: Gerar o QR Code
1. Pegue o link direto do seu APK (ex: `https://seusite.com/app.apk`).
2. Vá a um site gerador de QR Code (ex: [QRCode Monkey](https://www.qrcode-monkey.com/)).
3. Insira o link do APK.
4. Baixe a imagem do QR Code e coloque no seu site com um texto: *"Aponte a câmera para baixar o app"*.

## 3. Configurações Importantes no `buildozer.spec`
Já configurei o arquivo `buildozer.spec` no seu projeto para incluir:
- Permissões de Internet e Rede (necessárias para controlar a TV).
- Inclusão dos arquivos JSON e assets.
- Nome do App: "Controle AOC Pro".
