import time
import keyboard

from chamar_roblox import janela_ativa_eh_roblox, focar_janela_roblox
from estado_menu import abrir_menu_se_necessario, verificar_menu_aberto
from seleciona_pets import selecionar_pets

bot_ativo = False

def toggle_bot():
    global bot_ativo
    bot_ativo = not bot_ativo
    estado = "ATIVADO ✅" if bot_ativo else "DESATIVADO ❌"
    print(f"\n⚡ Bot {estado}")

def iniciar_loop():
    keyboard.add_hotkey('end', toggle_bot)
    print("🔁 Pressione [END] para ligar/desligar o bot.")

    while True:
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
            sucesso = selecionar_pets()
            if not sucesso:
                print("⚠️ Nenhum pet clicável encontrado.")

        time.sleep(1)

if __name__ == "__main__":
    iniciar_loop()
