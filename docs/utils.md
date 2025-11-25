# Utilitários de UI

> Componentes reutilizáveis que suportam a interface das cenas em pygame.

## Arquivos
```
utils/
├── __init__.py
├── buttons.py
├── constants.py
└── input_field.py
```

## `constants.py`
- Centraliza cores e dimensões (`SCREEN_WIDTH`, `SCREEN_HEIGHT`).
- Padrões de cor baseados na paleta do menu para manter identidade visual.
- Campos exportados são importados por cenas e widgets para evitar valores mágicos.

## Botões (`buttons.py`)
- `ButtonTheme` agrega paleta para estados normal/hover/borda/texto.
- `Button` gerencia rect, fonte, rótulo e callback:
  - `handle_event` monitora `MOUSEMOTION`/`MOUSEBUTTONDOWN` e dispara `_play_hover_sound`/_`_play_click_sound`.
  - `draw` renderiza retângulo arredondado e texto centralizado.
- Sons de hover/click são carregados sob demanda de `assets/sounds/` e só executam se `pygame.mixer` estiver inicializado.

## Campo de Entrada (`input_field.py`)
- `InputField` encapsula rótulo, placeholder, foco, cursor piscante e eventos de teclado.
- Suporta repetição automática de backspace, limpeza (`clear`) e atualização do retângulo (`set_rect`).
- `poll_text_changed()` permite que a cena verifique se houve alteração desde a última verificação.
- Renderiza placeholder em cor mutada até o usuário inserir texto.

## Convenções de Uso
- Instancie widgets uma única vez por cena e reutilize `handle_event`, `update` e `draw` dentro do ciclo principal.
- Prefira importar via `from utils import Button, ButtonTheme, InputField` para manter consistência.
- Sons opcionais: garanta que os arquivos `.mp3` existam ou envolva `pygame.mixer` com fallback silencioso, como já implementado.
