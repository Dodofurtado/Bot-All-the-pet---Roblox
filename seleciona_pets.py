import cv2
import numpy as np
from mss import mss
import time
import random
import ctypes
import os
import joblib

PET_REGION = {"top": 119, "left": 199, "width": 788, "height": 853}
THRESHOLD = 0.95
MAX_PETS = 3
PET_NAMES = ["klot", "zumbido", "f_lobisomem", "filhote", "cinza", "umbra"]

# Coordenadas centrais dos 12 slots (ordem: esquerda->direita, cima->baixo)
SLOTS_COORDS = [
    (338, 374), (517, 375), (685, 373), (861, 372),
    (344, 543), (514, 543), (682, 536), (865, 544),
    (343, 716), (514, 711), (690, 710), (861, 707)
]

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

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
    template_path = template_path.replace('/', '\\')
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

def encontrar_pets(bgr, name):
    pontos = []
    for tpl in [f"imagens\\{name}.png", f"imagens\\{name}S.png"]:
        tpl = tpl.replace('/', '\\')
        pontos += encontrar_template(bgr, tpl)
    return sorted(pontos, key=lambda p: (p[1], p[0]))

# Carregar modelo ML
ML_MODEL_PATH = "modelo_pet.joblib"
if os.path.isfile(ML_MODEL_PATH):
    clf = joblib.load(ML_MODEL_PATH)
else:
    clf = None

def prever_pet_ml(slot_img, clf):
    img = cv2.resize(slot_img, (64, 64)).flatten().reshape(1, -1)
    pred = clf.predict(img)
    return pred[0]

def identificar_pets_slots(bgr, clf):
    SLOT_W, SLOT_H = 173 + 8, 163 + 8
    pets_nos_slots = []
    for idx, (x, y) in enumerate(SLOTS_COORDS):
        cx = x - PET_REGION['left']
        cy = y - PET_REGION['top']
        x0 = max(cx - (SLOT_W // 2) - 3 - 8 - 4 + 5, 0)
        y0 = max(cy - (SLOT_H // 2) - 4, 0)
        x1 = x0 + SLOT_W
        y1 = y0 + SLOT_H
        slot_img = bgr[y0:y1, x0:x1]
        if clf is not None:
            nome = prever_pet_ml(slot_img, clf)
        else:
            nome = "desconhecido"
        pets_nos_slots.append(nome)
    return pets_nos_slots

def slot_esta_selecionado(slot_img, selecionado_tpl, threshold=0.90):
    """Verifica se o slot está selecionado usando template matching no canto superior direito."""
    h, w = selecionado_tpl.shape[:2]
    slot_h, slot_w = slot_img.shape[:2]
    # Região do canto superior direito
    roi = slot_img[0:h, slot_w-w:slot_w]
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(selecionado_tpl, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(roi_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val >= threshold

# Coordenadas absolutas do símbolo de selecionado para cada slot
SELECIONADO_COORDS = [
    (393, 314), (567, 313), (741, 315), (914, 314),
    (394, 483), (566, 484), (740, 483), (913, 484),
    (394, 653), (566, 654), (740, 655), (915, 654)
]
SELECIONADO_RGB = (125, 243, 119)
SELECIONADO_TOL = 10  # tolerância para cada canal

def slot_esta_selecionado_cor(tela_bgr, coord, rgb=SELECIONADO_RGB, tol=SELECIONADO_TOL):
    x_abs, y_abs = coord
    x = x_abs - PET_REGION['left']
    y = y_abs - PET_REGION['top']
    if y < 0 or y >= tela_bgr.shape[0] or x < 0 or x >= tela_bgr.shape[1]:
        return False
    b, g, r = tela_bgr[y, x]
    target_r, target_g, target_b = rgb
    return (
        abs(int(r) - target_r) <= tol and
        abs(int(g) - target_g) <= tol and
        abs(int(b) - target_b) <= tol
    )

def selecionar_pets(parar_callback=None):
    # Verifica se o fusível foi acionado
    if os.path.exists("fusivel_acionado.flag"):
        print("⚡ Fusível acionado! Reiniciando fluxo do bot.")
        os.remove("fusivel_acionado.flag")
        return False

    if clf is None:
        print("Modelo ML não encontrado!")
        return False

    # --- Primeira etapa: ML, clique em um do trio disponível ---
    while True:
        if parar_callback and parar_callback():
            print("⏹️ Seleção de pets interrompida.")
            return False
        tela = capturar_regiao(PET_REGION)
        bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
        pets_nos_slots = identificar_pets_slots(bgr, clf)
        trio_encontrado = False
        for pet in PET_NAMES:
            indices = [i for i, nome in enumerate(pets_nos_slots) if nome == pet]
            if len(indices) >= 3:
                slot_idx = indices[0]
                x, y = SLOTS_COORDS[slot_idx]
                print(f"✅ Selecionando {pet} (ML) no slot {slot_idx+1} em ({x}, {y})")
                clique_humano(x, y)
                time.sleep(0.4)
                trio_encontrado = True
                pet_selecionado = pet
                trio_indices = indices[:3]
                break
        if not trio_encontrado:
            print("⚠️ Nenhum pet pode atingir 3 unidades. Abortando.")
            return False
        break  # Sai da primeira etapa

    # --- Segunda etapa: OCV por cor, clique até 3 selecionados ---
    tentativas = 0
    max_tentativas = 6
    while True:
        if parar_callback and parar_callback():
            print("⏹️ Seleção de pets interrompida.")
            return False
        tela = capturar_regiao(PET_REGION)
        bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
        # Verifica slots do trio
        selecionados = []
        for idx in trio_indices:
            if slot_esta_selecionado_cor(bgr, SELECIONADO_COORDS[idx]):
                selecionados.append(idx)
        if len(selecionados) >= 3:
            print("✅ Já há 3 pets selecionados.")
            break  # Finaliza seleção

        # Clica nos que faltam, sempre verificando após cada clique
        for idx in trio_indices:
            if idx in selecionados:
                continue
            x, y = SLOTS_COORDS[idx]
            print(f"✅ Selecionando {pet_selecionado} (OCV) no slot {idx+1} em ({x}, {y})")
            clique_humano(x, y)
            time.sleep(0.3)
            tentativas += 1
            # Verifica novamente após o clique
            tela = capturar_regiao(PET_REGION)
            bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
            # Verificação extra com ML: ainda existem 3 pets do mesmo tipo?
            pets_nos_slots = identificar_pets_slots(bgr, clf)
            indices_ml = [i for i, nome in enumerate(pets_nos_slots) if nome == pet_selecionado]
            if len(indices_ml) < 3:
                print("⚠️ Menos de 3 pets disponíveis após clique (ML). Seguindo o fluxo do bot.")
                return True
            selecionados = []
            for idx2 in trio_indices:
                if slot_esta_selecionado_cor(bgr, SELECIONADO_COORDS[idx2]):
                    selecionados.append(idx2)
            if len(selecionados) >= 3:
                print("✅ Já há 3 pets selecionados.")
                break
            if tentativas >= max_tentativas:
                print("⚠️ Limite de tentativas de seleção atingido. Seguindo o fluxo do bot.")
                return True
        if tentativas >= max_tentativas:
            print("⚠️ Limite de tentativas de seleção atingido. Seguindo o fluxo do bot.")
            return True
        time.sleep(0.2)
