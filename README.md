🖱️ MouseClone - Arduino HID Spoofer

Projeto que transforma um Arduino Leonardo em um dispositivo HID, clonando as informações de um mouse USB (VID/PID) real. Ideal para testes, automação e simulações de dispositivos de entrada.

## 🚀 Funcionalidades

- Detecta automaticamente mouses conectados via USB;
- Lê e exibe VID (Vendor ID) e PID (Product ID);
- Atualiza a configuração do Arduino Leonardo com os dados do mouse;
- Compila e faz upload do sketch via Arduino CLI;
- Faz spoof completo do dispositivo para parecer um mouse real.

## 🛠️ Pré-requisitos

- Arduino Leonardo;
- Windows com PowerShell;
- [Python instalado](https://www.python.org/downloads/);
- Acesso de administrador (para manipular dispositivos).

## 📦 Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/Sapientiia/MouseClone.git
   cd MouseClone
   ```
 2. Execute o script Python:

  ```bash
  python spoofino.py
  ```
3. Siga as instruções no terminal:

Selecione o mouse desejado

Informe a porta COM do seu Arduino


⚠️ Aviso Legal
Este projeto é apenas para fins educacionais e de pesquisa. O uso indevido pode violar leis de segurança e privacidade. Utilize com responsabilidade.

