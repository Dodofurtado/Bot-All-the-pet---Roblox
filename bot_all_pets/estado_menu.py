import cv2
import numpy as np
from mss import mss
import time
import random
import ctypes

# Configurações
MENU_REGION = {"top": 136, "left": 752, "width": 268, "height": 124}
TEMPLATE_PATH = "imagens/menu_aberto.png"
THRESHOLD = 0.9
CLICK_X = (840 + 1063) // 2
CLICK_Y = (897 + 1016) // 2
MAX_TENTATIVAS = 3

# Constantes da API do Windows para mouse_event
MOUSEEVENTF_MOVE      = 0x0001
MOUSEEVENTF_ABSOLUTE  = 0x8000
MOUSEEVENTF_LEFTDOWN  = 0x0002
MOUSEEVENTF_LEFTUP    = 0x0004

# Clique via API do Windows
def click_win_api(x, y):
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    ax = int(x * 65535 / screen_w)
    ay = int(y * 65535 / screen_h)

    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ax, ay, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, ax, ay, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP,   ax, ay, 0, 0)

# Movimento humano + clique real sem manipular janela
def clique_humano(x, y, agito=15):
    offset_x = random.randint(-agito, agito)
    offset_y = random.randint(-agito, agito)
    destino_x = x + offset_x
    destino_y = y + offset_y
    click_win_api(destino_x, destino_y)

# Captura região do menu
def capturar_regiao():
    with mss() as sct:
        img = sct.grab(MENU_REGION)
        return np.array(img)

# Detecta se o menu está aberto via template
def verificar_menu_aberto():
    tela = capturar_regiao()
    tela_bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)

    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_COLOR)
    if template is None:
        print(f"❌ Template não encontrado: {TEMPLATE_PATH}")
        return False

    res = cv2.matchTemplate(tela_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    return max_val >= THRESHOLD

# Verifica se o menu está aberto e tenta abrir clicando se necessário
def abrir_menu_se_necessario():
    tentativas = 0

    while tentativas < MAX_TENTATIVAS:
        if verificar_menu_aberto():
            print(f"✅ Menu está aberto (tentativa {tentativas + 1}).")
            return True
        
        print(f"❌ Menu fechado. Clicando para abrir (tentativa {tentativas + 1})...")
        clique_humano(CLICK_X, CLICK_Y)
        time.sleep(1)

        tentativas += 1

    print("⛔ Menu não foi aberto após várias tentativas.")
    return False
