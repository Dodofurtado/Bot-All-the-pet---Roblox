"""
Bot All Pets - Script Principal

Este é o script principal que coordena todas as funcionalidades do bot.
Inicia o monitor de fusível em paralelo e gerencia o ciclo principal de fusão de pets.

Controles:
    END - Liga/Desliga o bot
"""

import time
import keyboard
import subprocess
import os

from chamar_roblox import janela_ativa_eh_roblox, focar_janela_roblox
from estado_menu import abrir_menu_se_necessario, verificar_menu_aberto
from seleciona_pets import selecionar_pets

# Inicia o click_fusivel.py em paralelo (caminho absoluto)
fusivel_path = os.path.join(os.path.dirname(__file__), "click_fusivel.py")
fusivel_proc = subprocess.Popen(['python', fusivel_path])

bot_ativo = False

def toggle_bot():
    global bot_ativo
    bot_ativo = not bot_ativo 
    estado = "ATIVADO ✅" if bot_ativo else "DESATIVADO ❌"
    print(f"\n⚡ Bot {estado}")

def iniciar_loop():
    keyboard.add_hotkey('end', toggle_bot)
    print("🔁 Pressione [END] para ligar/desligar o bot.")

    def bot_parado():
        return not bot_ativo

    while True:
        # Verifica se o fusível foi acionado
        if os.path.exists("fusivel_acionado.flag"):
            print("⚡ Fusível acionado! Reiniciando ciclo principal.")
            os.remove("fusivel_acionado.flag")
            time.sleep(1)
            continue

        if bot_ativo:
            print("🔎 Verificando janela ativa...")
            if janela_ativa_eh_roblox():
                print("🟢 Roblox está ativo e em foco.")
            else:
                print("🔴 Roblox não está em foco. Trazendo janela...")
                focar_janela_roblox()
                time.sleep(1)
                continue  # volta ao topo do loop

            print("📁 Verificando se menu já está aberto...")
            if not verificar_menu_aberto():
                print("📂 Tentando abrir menu...")
                if not abrir_menu_se_necessario():
                    print("⛔ Falha ao abrir o menu. Repetindo ciclo.")
                    time.sleep(2)
                    continue

            print("🐾 Selecionando pets...")
            sucesso = selecionar_pets(parar_callback=bot_parado)
            if not sucesso:
                print("⚠️ Nenhum pet clicável encontrado.")

        time.sleep(1)

if __name__ == "__main__":
    try:
        iniciar_loop()
    finally:
        fusivel_proc.terminate()
