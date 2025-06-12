Bot All Pets
Automação para seleção de pets e interação com o jogo Roblox, utilizando reconhecimento de imagem e controle do mouse no Windows.

Funcionalidades
Detecta e foca automaticamente a janela do Roblox.
Abre o menu do jogo caso esteja fechado.
Seleciona automaticamente até 3 pets de acordo com imagens de referência.
Realiza cliques simulando movimentos humanos.
Automatiza o clique em áreas específicas (ex: fusível).
Requisitos
Windows (uso de APIs específicas)
Python 3.8+
Dependências Python:
opencv-python
numpy
mss
pyautogui
pywin32
keyboard

Instale as dependências com:
pip install opencv-python numpy mss pyautogui pywin32 keyboard

Estrutura dos Arquivos
main.py — Loop principal e controle do bot.
chamar_roblox.py — Funções para focar e maximizar a janela do Roblox.
estado_menu.py — Verificação e abertura do menu do jogo.
seleciona_pets.py — Lógica de reconhecimento e seleção de pets.
imagens — Pasta com templates das imagens dos pets e do menu.

Como Usar
Coloque as imagens dos pets e do menu na pasta imagens (exemplo: klot.png, klotS.png, klotV.png, etc).
Execute o main.py:
Pressione a tecla END para ativar/desativar o bot.
O bot irá focar o Roblox, abrir o menu e selecionar os pets automaticamente.
Observações
Certifique-se de que o Roblox está aberto e visível na tela.
Ajuste as regiões (PET_REGION, FUSIVEL_REGION, etc) conforme a resolução/tela do seu jogo.
O bot simula movimentos humanos, mas use por sua conta e risco.

Desenvolvido por Dodofurtado.
