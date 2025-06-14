import cv2
import numpy as np
from mss import mss
import time
import random
import ctypes
import pyautogui
import os

FUSIVEL_TEMPLATE = "imagens\\fusivel.png"
THRESHOLD = 0.75

def click_win_api(x, y):
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    ax = int(x * 65535 / screen_w)
    ay = int(y * 65535 / screen_h)
    ctypes.windll.user32.mouse_event(0x0001 | 0x8000, ax, ay, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(0x0002, ax, ay, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(0x0004, ax, ay, 0, 0)

def clique_humano(x, y, agito=15):
    offset_x = random.randint(-agito, agito)
    offset_y = random.randint(-agito, agito)
    destino_x = x + offset_x
    destino_y = y + offset_y
    pyautogui.FAILSAFE = False
    pyautogui.moveTo(destino_x, destino_y, duration=random.uniform(0.05, 0.1))  # mais rápido
    time.sleep(random.uniform(0.02, 0.07))
    pyautogui.moveTo(x, y, duration=random.uniform(0.05, 0.1))  # mais rápido
    click_win_api(x, y)
    time.sleep(0.05)
    click_win_api(x, y)  # duplo clique

def capturar_tela():
    with mss() as sct:
        monitor = sct.monitors[1]  # Tela inteira principal
        img = sct.grab(monitor)
        return np.array(img), monitor

def encontrar_fusivel(imagem, template_path):
    template = cv2.imread(template_path)
    if template is None:
        while True:
            print(f"Template não encontrado: {template_path}")
            time.sleep(2)
        # Nunca retorna pontos se não encontrar o template
    img_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= THRESHOLD)
    h, w = tpl_gray.shape[:2]
    pontos = [(int(pt[0] + w/2), int(pt[1] + h/2)) for pt in zip(*loc[::-1])]
    return pontos

def main():
    while True:
        tela, monitor = capturar_tela()
        bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
        pontos = encontrar_fusivel(bgr, FUSIVEL_TEMPLATE)
        if pontos:
            x, y = pontos[0]
            x_click = monitor['left'] + x
            y_click = monitor['top'] + y
            print(f"⚡ Fusível detectado em ({x_click}, {y_click}), clicando...")
            clique_humano(x_click, y_click)
            # Sinaliza para o bot principal que o fusível foi clicado
            with open("fusivel_acionado.flag", "w") as f:
                f.write("1")
            time.sleep(1)  # Aguarda para evitar múltiplos cliques seguidos
        else:
            time.sleep(0.3)

if __name__ == "__main__":
    main()
