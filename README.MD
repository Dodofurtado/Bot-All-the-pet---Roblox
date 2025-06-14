# Bot All Pets

Bot automatizado para fusão de pets usando Machine Learning e OpenCV.

## Estrutura

```
bot_all_pets/
├── imagens/           # Templates e imagens de referência
├── dataset/           # Dataset para treinar o modelo ML
├── modelo_pet.joblib  # Modelo ML treinado
├── main.py           # Script principal
├── seleciona_pets.py # Lógica de seleção de pets
├── click_fusivel.py  # Monitor do botão de fusão
├── verifica_slots.py # Ferramenta de debug visual
└── treinar_modelo.py # Script para treinar o modelo ML
```

## Requisitos

```bash
pip install -r requirements.txt
```

## Uso

1. Execute o bot:
```bash
python main.py
```

2. Controles:
- `END` - Liga/Desliga o bot
- `HOME` - (Debug) Mostra slots detectados

## Funcionalidades

- Detecção de pets usando Machine Learning
- Verificação de seleção via OpenCV
- Monitor automático do botão de fusão
- Interface visual para debug

## Observações

- Certifique-se de que o Roblox está aberto e visível na tela.
- Ajuste as regiões (PET_REGION, FUSIVEL_REGION, etc) conforme a resolução/tela do seu jogo.
- O bot simula movimentos humanos, mas use por sua conta e risco.

Desenvolvido por Dodofurtado.