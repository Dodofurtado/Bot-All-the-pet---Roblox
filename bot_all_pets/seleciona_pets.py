import cv2
import numpy as np
from mss import mss
import time
import random
import ctypes
import os

PET_REGION = {"top": 119, "left": 199, "width": 788, "height": 853}
FUSIVEL_REGION = {"top": 553, "left": 1143, "width": 248, "height": 208}
THRESHOLD = 0.94
MAX_PETS = 3
PET_NAMES = ["klot", "zumbido", "f_lobisomem", "filhote", "cinza", "umbra"]

MOUSEEVENTF_MOVE      = 0x0001
MOUSEEVENTF_ABSOLUTE  = 0x8000
MOUSEEVENTF_LEFTDOWN  = 0x0002
MOUSEEVENTF_LEFTUP    = 0x0004

def click_win_api(x, y):
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    ax = int(x * 65535 / screen_w)
    ay = int(y * 65535 / screen_h)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ax, ay, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, ax, ay, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, ax, ay, 0, 0)

def clique_humano(x, y, agito=15):
    offset_x = random.randint(-agito, agito)
    offset_y = random.randint(-agito, agito)
    destino_x = x + offset_x
    destino_y = y + offset_y
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.moveTo(destino_x, destino_y, duration=random.uniform(0.1, 0.2))
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.2))
    click_win_api(x, y)

def capturar_regiao(region):
    with mss() as sct:
        img = sct.grab(region)
        return np.array(img)

def encontrar_template(imagem, template_path):
    if not os.path.isfile(template_path):
        return []
    template = cv2.imread(template_path)
    if template is None:
        return []

    img_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= THRESHOLD)

    h, w = tpl_gray.shape[:2]
    pontos = [(int(pt[0] + w/2), int(pt[1] + h/2)) for pt in zip(*loc[::-1])]
    return pontos

def remover_pontos_duplicados(pontos, distancia_min=20):
    filtrados = []
    for p in pontos:
        if all(np.linalg.norm(np.array(p) - np.array(outro)) > distancia_min for outro in filtrados):
            filtrados.append(p)
    return filtrados

def selecionar_pets():
    tela = capturar_regiao(PET_REGION)
    bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)

    pet_escolhido = None
    for name in PET_NAMES:
        disp = []
        for tpl in [f"imagens/{name}.png", f"imagens/{name}S.png"]:
            disp += encontrar_template(bgr, tpl)
        disp = remover_pontos_duplicados(disp)
        sel = []
        for tpl in [f"imagens/{name}V.png", f"imagens/{name}SV.png"]:
            sel += encontrar_template(bgr, tpl)
        sel = remover_pontos_duplicados(sel)
        if len(disp) + len(sel) >= MAX_PETS:
            pet_escolhido = name
            break
    if pet_escolhido is None:
        print("⚠️ Nenhum pet pode atingir 3 unidades. Abortando.")
        return False

    while True:
        tela = capturar_regiao(PET_REGION)
        bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
        sel_pts = []
        for tpl in [f"imagens/{pet_escolhido}V.png", f"imagens/{pet_escolhido}SV.png"]:
            sel_pts += encontrar_template(bgr, tpl)
        sel_pts = remover_pontos_duplicados(sel_pts)
        if len(sel_pts) >= MAX_PETS:
            break

        disp_pts = []
        for tpl in [f"imagens/{pet_escolhido}.png", f"imagens/{pet_escolhido}S.png"]:
            disp_pts += encontrar_template(bgr, tpl)
        disp_pts = remover_pontos_duplicados(disp_pts)

        candidatos = [p for p in disp_pts if all(np.linalg.norm(np.array(p)-np.array(s))>20 for s in sel_pts)]
        candidatos.sort(key=lambda p: (p[1], p[0]))

        if not candidatos:
            print(f"⚠️ Não há mais candidatos para selecionar {pet_escolhido}. Abortando.")
            return False

        x,y = candidatos[0]
        x_click = PET_REGION['left'] + x
        y_click = PET_REGION['top'] + y
        print(f"✅ Selecionando {pet_escolhido} {len(sel_pts)+1}/3 em ({x_click}, {y_click})")
        clique_humano(x_click, y_click)
        time.sleep(1)

    fx = FUSIVEL_REGION['left'] + FUSIVEL_REGION['width']//2
    fy = FUSIVEL_REGION['top'] + FUSIVEL_REGION['height']//2
    print(f"🔌 Clique no fusível em ({fx}, {fy})")
    clique_humano(fx, fy)
    time.sleep(0.5)
    return True
