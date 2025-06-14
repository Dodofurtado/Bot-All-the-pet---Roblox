import cv2
import numpy as np
from mss import mss
import os
import time
import keyboard
import sys

PET_REGION = {"top": 119, "left": 199, "width": 788, "height": 853}
SLOTS_COORDS = [
    (338, 374), (517, 375), (685, 373), (861, 372),
    (344, 543), (514, 543), (682, 536), (865, 544),
    (343, 716), (514, 711), (690, 710), (861, 707)
]
SLOT_W, SLOT_H = 173 + 8, 163 + 8

os.makedirs("dataset", exist_ok=True)

def capturar_regiao(region):
    with mss() as sct:
        img = sct.grab(region)
        return np.array(img)

def salvar_slots():
    tela = capturar_regiao(PET_REGION)
    bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
    for idx, (x, y) in enumerate(SLOTS_COORDS):
        cx = x - PET_REGION['left']
        cy = y - PET_REGION['top']
        x0 = max(cx - (SLOT_W // 2) - 3 - 8 - 4 + 5, 0)
        y0 = max(cy - (SLOT_H // 2) - 4, 0)
        x1 = x0 + SLOT_W
        y1 = y0 + SLOT_H
        slot_img = bgr[y0:y1, x0:x1]
        filename = f"dataset/slot_{idx+1}.png"
        cv2.imwrite(filename, slot_img)
        print(f"Salvo: {filename}")

def salvar_slots_ao_apertar_home():
    contador = 0
    print("Aperte 'home' para capturar e salvar os slots. Aperte ESC para sair.")
    while True:
        if keyboard.is_pressed('home'):
            tela = capturar_regiao(PET_REGION)
            bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
            timestamp = int(time.time())
            for idx, (x, y) in enumerate(SLOTS_COORDS):
                cx = x - PET_REGION['left']
                cy = y - PET_REGION['top']
                x0 = max(cx - (SLOT_W // 2) - 3 - 8 - 4 + 5, 0)
                y0 = max(cy - (SLOT_H // 2) - 4, 0)
                x1 = x0 + SLOT_W
                y1 = y0 + SLOT_H
                slot_img = bgr[y0:y1, x0:x1]
                filename = f"dataset/slot_{idx+1}_{timestamp}_{contador}.png"
                cv2.imwrite(filename, slot_img)
                print(f"Salvo: {filename}")
            contador += 1
            # Aguarda soltar a tecla para evitar múltiplas capturas
            while keyboard.is_pressed('home'):
                cv2.waitKey(100)
        if cv2.waitKey(50) == 27:  # ESC
            print("Saindo da captura de slots.")
            break

if __name__ == "__main__":
    salvar_slots_ao_apertar_home()