import cv2
import numpy as np
from mss import mss
import keyboard
import os
import joblib

PET_REGION = {"top": 119, "left": 199, "width": 788, "height": 853}
SLOTS_COORDS = [
    (338, 374), (517, 375), (685, 373), (861, 372),
    (344, 543), (514, 543), (682, 536), (865, 544),
    (343, 716), (514, 711), (690, 710), (861, 707)
]
# Coordenadas absolutas do símbolo de selecionado para cada slot
SELECIONADO_COORDS = [
    (393, 314), (567, 313), (741, 315), (914, 314),
    (394, 483), (566, 484), (740, 483), (913, 484),
    (394, 653), (566, 654), (740, 655), (915, 654)
]
SELECIONADO_RGB = (125, 243, 119)
SELECIONADO_TOL = 10  # tolerância para cada canal

PET_NAMES = ["klot", "zumbido", "f_lobisomem", "filhote", "cinza", "umbra"]
THRESHOLD = 0.93

def capturar_regiao(region):
    with mss() as sct:
        img = sct.grab(region)
        return np.array(img)

def identificar_pet(slot_img, templates):
    slot_gray = cv2.cvtColor(slot_img, cv2.COLOR_BGR2GRAY)
    melhor_nome = "desconhecido"
    melhor_valor = 0
    for name, tpl in templates.items():
        if tpl is None:
            continue
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
        if slot_gray.shape[0] < tpl_gray.shape[0] or slot_gray.shape[1] < tpl_gray.shape[1]:
            continue
        res = cv2.matchTemplate(slot_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > melhor_valor and max_val >= THRESHOLD:
            melhor_valor = max_val
            melhor_nome = name
    return melhor_nome, melhor_valor

def carregar_templates():
    templates = {}
    for name in PET_NAMES:
        paths = [f"imagens\\{name}.png", f"imagens\\{name}S.png"]
        for path in paths:
            if os.path.isfile(path):
                templates[name] = cv2.imread(path)
                break
        else:
            templates[name] = None
    return templates

# Carregue o modelo treinado
ML_MODEL_PATH = "modelo_pet.joblib"
if os.path.isfile(ML_MODEL_PATH):
    clf = joblib.load(ML_MODEL_PATH)
else:
    clf = None

def prever_pet_ml(slot_img, clf):
    # Ajuste para o tamanho usado no modelo ML (64x64)
    img = cv2.resize(slot_img, (64, 64)).flatten().reshape(1, -1)
    pred = clf.predict(img)
    return pred[0]

def slot_esta_selecionado_cor(tela_bgr, coord, rgb=SELECIONADO_RGB, tol=SELECIONADO_TOL):
    """Verifica se o slot está selecionado pela cor no pixel absoluto da tela."""
    x_abs, y_abs = coord
    # Corrige para coordenada relativa à região capturada
    x = x_abs - PET_REGION['left']
    y = y_abs - PET_REGION['top']
    # Protege contra coordenadas fora da imagem
    if y < 0 or y >= tela_bgr.shape[0] or x < 0 or x >= tela_bgr.shape[1]:
        return False
    b, g, r = tela_bgr[y, x]  # OpenCV usa BGR
    target_r, target_g, target_b = rgb
    return (
        abs(int(r) - target_r) <= tol and
        abs(int(g) - target_g) <= tol and
        abs(int(b) - target_b) <= tol
    )

def mostrar_slots(gabarito=None):
    tela = capturar_regiao(PET_REGION)
    bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
    templates = carregar_templates()
    resultados = []
    SLOT_W, SLOT_H = 173 + 8, 163 + 8 

    for idx, (x, y) in enumerate(SLOTS_COORDS):
        cx = x - PET_REGION['left']
        cy = y - PET_REGION['top']
        x0 = max(cx - (SLOT_W // 2) - 3 - 8 - 4 + 5, 0) 
        y0 = max(cy - (SLOT_H // 2) - 4, 0)
        x1 = x0 + SLOT_W
        y1 = y0 + SLOT_H
        slot_img = bgr[y0:y1, x0:x1]
        # Prioriza o modelo ML se disponível
        if clf is not None:
            nome_ml = prever_pet_ml(slot_img, clf)
            nome = nome_ml
            resultado_ml = f"ML: {nome_ml}"
        else:
            nome, score = identificar_pet(slot_img, templates)
            resultado_ml = ""
        # Verifica se está selecionado pela cor
        selecionado = slot_esta_selecionado_cor(bgr, SELECIONADO_COORDS[idx])
        resultados.append((nome, selecionado))
        # Escreve o nome e seleção na imagem do slot
        img_show = slot_img.copy()
        cv2.putText(img_show, nome, (5, SLOT_H - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv2.LINE_AA)
        if resultado_ml:
            cv2.putText(img_show, resultado_ml, (5, SLOT_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)
        if selecionado:
            cv2.putText(img_show, "SELECIONADO", (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2, cv2.LINE_AA)
        cv2.imshow(f"Slot {idx+1}", img_show)
    print("Leitura dos slots:")
    for idx, (nome, selecionado) in enumerate(resultados):
        status = "SELECIONADO" if selecionado else "nao"
        print(f"Slot {idx+1}: {nome} [{status}]")
    print("Pressione ESC para fechar as janelas.")

def fechar_janelas():
    for idx in range(len(SLOTS_COORDS)):
        cv2.destroyWindow(f"Slot {idx+1}")

print("Aperte 'home' para verificar os slots. Aperte ESC para sair.")

while True:
    if keyboard.is_pressed('home'):
        mostrar_slots()
        # Aguarda até soltar a tecla para evitar múltiplas leituras rápidas
        while keyboard.is_pressed('home'):
            cv2.waitKey(100)
    if cv2.waitKey(50) == 27:  # ESC
        fechar_janelas()
        break
