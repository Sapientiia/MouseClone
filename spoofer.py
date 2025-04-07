import os
import re
import time
import random
import requests 
import zipfile
import subprocess
import win32com.client 

class Spoofer:
    """
    A classe Spoofer gerencia o processo de configuração da Arduino CLI, 
    detecção de dispositivos de mouse conectados, alteração dos dados da placa Arduino Leonardo 
    e compilação/envio do sketch para o Arduino.
    """

    SKETCH_FILE = "arduino/arduino.ino"
    BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")

    def __init__(self):
        """
        Inicializa a classe Spoofer e define o caminho para o executável da Arduino CLI.
        """
        self.arduino_cli_path = os.path.join(os.getcwd(), "arduino/arduino-cli.exe")

    def download_arduino_cli(self):
        """
        Baixa e extrai a Arduino CLI se ela ainda não estiver presente.
        """
        os.makedirs("arduino", exist_ok=True)

        if os.path.exists(self.arduino_cli_path):
            return

        if not os.path.exists(os.path.join(os.getcwd(), "arduino/arduino-cli.zip")):
            print("Baixando Arduino CLI...")
            response = requests.get("https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip", stream=True)
            with open("arduino/arduino-cli.zip", "wb") as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)

        with zipfile.ZipFile("arduino/arduino-cli.zip", 'r') as zip_ref:
            zip_ref.extractall("./arduino/")

    def update_boards(self, vendor_id, product_id, mouse_name):
        """
        Atualiza o arquivo 'boards.txt' para alterar o VID, PID e nome do produto da placa Arduino Leonardo.
        
        Args:
            vendor_id (str): ID do fornecedor (VID) em formato hexadecimal (ex: '0x2341').
            product_id (str): ID do produto (PID) em formato hexadecimal (ex: '0x8036').
            mouse_name (str): Nome do dispositivo de mouse selecionado.
        """
        with open(self.BOARDS_TXT_PATH, 'r') as boards_file:
            board_config_lines = boards_file.readlines()

        for index, line in enumerate(board_config_lines):
            if line.startswith("leonardo.name="):
                board_config_lines[index] = f"leonardo.name={mouse_name}\n"
            elif line.startswith("leonardo.vid."):
                suffix = line.split("leonardo.vid.")[1].split("=")[0]
                board_config_lines[index] = f"leonardo.vid.{suffix}={vendor_id}\n"
            elif line.startswith("leonardo.pid."):
                suffix = line.split("leonardo.pid.")[1].split("=")[0]
                board_config_lines[index] = f"leonardo.pid.{suffix}={product_id}\n"
            elif line.startswith("leonardo.build.vid="):
                board_config_lines[index] = f"leonardo.build.vid={vendor_id}\n"
            elif line.startswith("leonardo.build.pid="):
                board_config_lines[index] = f"leonardo.build.pid={product_id}\n"
            elif line.startswith("leonardo.build.usb_product="):
                board_config_lines[index] = f"leonardo.build.usb_product=\"{mouse_name}\"\n"

        with open(self.BOARDS_TXT_PATH, 'w') as boards_file:
            boards_file.writelines(board_config_lines)

    def detect_mouse_devices(self):
        """
        Detecta todos os dispositivos de mouse conectados usando WMI e retorna uma lista 
        com nome, VID, PID e ID do dispositivo.

        Returns:
            list: Lista de dicionários com informações dos mouses detectados.
        """
        wmi_service = win32com.client.GetObject("winmgmts:")
        mouse_devices = wmi_service.InstancesOf("Win32_PointingDevice")
        detected_mice = []

        for device in mouse_devices:
            nome_dispositivo = device.Name
            pnp_id = device.PNPDeviceID
            print(f"Nome do dispositivo: {nome_dispositivo}")
            print(f"PNPDeviceID: {pnp_id}")

            id_match = re.search(r'VID_(\w+)&PID_(\w+)', pnp_id)

            if id_match:
                vid, pid = id_match.groups()
                detected_mice.append({
                    'name': nome_dispositivo,
                    'vid': vid,
                    'pid': pid,
                    'pnp_id': pnp_id
                })
            else:
                detected_mice.append({
                    'name': nome_dispositivo,
                    'vid': None,
                    'pid': None,
                    'pnp_id': pnp_id
                })

        # Filtrar apenas mouses USB com VID e PID válidos
        mouses_validos = [
            device for device in detected_mice
            if "USB" in device['name'] and device['vid'] and device['pid']
        ]

        return mouses_validos

    def prompt_mouse_selection(self):
        """
        Exibe os dispositivos de mouse detectados e permite ao usuário escolher qual usar.
        Em seguida, atualiza os dados da placa com base na escolha.
        """
        detected_mice = self.detect_mouse_devices()

        if not detected_mice:
            print("Nenhum mouse USB válido foi encontrado.\nSaindo em 10 segundos...")
            time.sleep(10)
            exit()

        os.system('cls')

        for index, device in enumerate(detected_mice, 1):
            print(f"{index} → {device['name']}\tVID: {device['vid']}, PID: {device['pid']}")

        selected_index = int(input("\nSelecione o número do mouse desejado: ")) - 1
        selected_device = detected_mice[selected_index]
        self.update_boards("0x" + selected_device['vid'], "0x" + selected_device['pid'], selected_device['name'])

    def install_avr_core(self):
        """
        Verifica se o core AVR e a biblioteca Mouse já estão instalados.
        Caso não estejam, instala usando a Arduino CLI.
        """
        result = subprocess.run([self.arduino_cli_path, "core", "list"], capture_output=True, text=True)

        if "arduino:avr" not in result.stdout and not "1.8.6" in result.stdout:
            print("Instalando o core AVR 1.8.6...")
            os.system(f"{self.arduino_cli_path} core install arduino:avr@1.8.6 >NUL 2>&1")

        result = subprocess.run([self.arduino_cli_path, "lib", "list"], capture_output=True, text=True)

        if "Mouse" not in result.stdout:
            print("Instalando biblioteca Mouse...")
            os.system(f"{self.arduino_cli_path} lib install Mouse >NUL 2>&1")

    def compile_sketch(self):
        """
        Compila o sketch .ino com a configuração da placa Leonardo.
        """
        os.system('cls')
        com_port = input("Digite a porta COM do seu Arduino Leonardo (ex: COM3): ")

        print("Compilando sketch...")

        if not os.path.exists(self.SKETCH_FILE):
            print(f"Erro: Arquivo '{self.SKETCH_FILE}' não encontrado!")
            return
        
        os.system(f"{self.arduino_cli_path} compile --fqbn arduino:avr:leonardo {self.SKETCH_FILE} >NUL 2>&1")
        self.upload_sketch(com_port)

    def upload_sketch(self, com_port):
        """
        Faz o upload do sketch compilado para o Arduino Leonardo.
        """
        if not os.path.exists(self.SKETCH_FILE):
            print(f"Erro: Arquivo '{self.SKETCH_FILE}' não encontrado!")
            return
        
        print("Enviando sketch para o Arduino...")

        comando = f"{self.arduino_cli_path} upload -p {com_port} --fqbn arduino:avr:leonardo {self.SKETCH_FILE}"
        resultado = os.system(comando)
        
        if resultado == 0:
            print("Spoof concluído com sucesso. Agora você pode usar o colorbot!")
        else:
            print(f"Falha ao enviar o sketch. Código de erro: {resultado}")
            print("Verifique se o Arduino está conectado e a porta COM está correta.")

    def run(self):
        """
        Executa todas as etapas: download da CLI, instalação de dependências,
        detecção do mouse, configuração da placa e upload do sketch.
        """
        self.download_arduino_cli()
        self.install_avr_core()
        self.prompt_mouse_selection()
        self.compile_sketch()


if __name__ == "__main__":
    os.system('cls')
    os.system("title github.com/iamennui/ValorantArduinoColorbot")
    Spoofer().run()
