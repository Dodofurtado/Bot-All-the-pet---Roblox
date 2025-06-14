import pyautogui
import keyboard
import mouse
import time

print("\U0001F4CD Aguardando clique com o botão direito do mouse... (pressione ESC para sair)")

try:
    while True:
        if mouse.is_pressed(button='right'):
            x, y = pyautogui.position()
            r, g, b = pyautogui.pixel(x, y)
            print(f"👡 Coordenadas: X={x}, Y={y} | Cor: RGB=({r}, {g}, {b})")
            time.sleep(0.3)  # Evita flood de prints

        if keyboard.is_pressed("esc"):
            print("⛔ Encerrando coleta de coordenadas.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    print("⛔ Interrompido manualmente.")
