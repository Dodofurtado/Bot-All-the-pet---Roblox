#chamar_roblox.py
import win32gui
import win32con
import win32com.client
import time

def get_janela_ativa():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

def janela_ativa_eh_roblox():
    titulo = get_janela_ativa().lower()
    return 'roblox' in titulo


def focar_janela_roblox():
    def enum_callback(hwnd, resultado):
        titulo = win32gui.GetWindowText(hwnd).lower()
        if 'roblox' in titulo:
            resultado.append(hwnd)

    roblox_hwnds = []
    win32gui.EnumWindows(enum_callback, roblox_hwnds)

    if not roblox_hwnds:
        print("❌ Roblox não encontrado.")
        return False

    hwnd = roblox_hwnds[0]
    shell = win32com.client.Dispatch("WScript.Shell")

    # 🔓 Remove minimização se existir
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.1)

    # ⛓️ Garante foco via ALT truque
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)

    # 🔎 Garante que está maximizada
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.3)

    print("🎮 Roblox foi trazido e MAXIMIZADO.")
    return True