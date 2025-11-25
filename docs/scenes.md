# Cenas

> Panorama das classes de cena responsáveis por estados e telas do jogo.

## Organização
```
scenes/
├── __init__.py
├── add_music.py
├── base.py
├── gameplay.py
├── menu.py
└── music_select.py
```
- `BaseScene` define a interface padrão.
- `MenuScene`, `MusicSelectScene` e `AddMusicScene` já estão implementadas.
- `GameplayScene` está reservado para a lógica de jogo rítmico (ainda não implementada).

## `BaseScene`
- Classe abstrata com `handle_event`, `update` e `render` obrigatórios.
- Gerencia plano de fundo com carregamento preguiçoso, redimensionamento suave e fallback para cor sólida.
- `set_background` aceita nomes relativos em `assets/images` ou caminhos absolutos.
- `draw_background(surface, color)` padroniza o desenho do fundo antes do conteúdo específico de cada cena.

## `MenuScene`
- Cena inicial do jogo.
- Constrói botões para "Play", "Adicionar Música", "Tela Cheia" e "Sair" usando `utils.buttons.Button`.
- Responsável por ajustar layout quando a janela muda de tamanho.
- Alterna cenas via `app.change_scene(...)` e delega fullscreen para `GameApp.toggle_fullscreen()`.

## `MusicSelectScene`
- Lista músicas válidas na pasta `musics/` (exige exatamente um `.csv` e um `.mp3`).
- Permite navegação por teclado (`↑`, `↓`, `Enter`, `Esc`) e prévia de áudio com `pygame.mixer.music`.
- Divide a tela em painel de preview (esquerda) e lista (direita), reutilizando o tema de botões customizado.
- Métodos utilitários:
  - `_load_songs()` monta a coleção de faixas.
  - `_play_preview()` inicia um trecho da música atual (início configurado em 30s).
  - `_wrap_text()` quebra textos longos para caber na UI.

## `AddMusicScene`
- Formulário para criar uma nova música a partir de um arquivo ZIP.
- Usa `utils.InputField` para campos "Nome da música" e "Arquivo ZIP".
- Integra com `tkinter.filedialog` (opcional) para selecionar o arquivo em uma janela nativa.
- `_import_song` extrai o ZIP em diretório temporário, valida `.csv`/`.mp3` e salva em `musics/<nome_sanitizado>/`.
- Exibe feedback de sucesso/erro na parte inferior da tela.

## `GameplayScene`
- Arquivo reservado; a cena ainda será implementada.
- Recomenda-se herdá-la de `BaseScene` e aplicar parsing do CSV para sincronizar notas com a trilha.
- Deverá interagir com `models.Play` para registrar resultados ao final da partida.

## Fluxo de Transição
1. `GameApp` inicia com `MenuScene`.
2. "Play" envia para `MusicSelectScene`.
3. `MusicSelectScene` deverá criar `GameplayScene` quando `Enter` for pressionado (TODO).
4. "Adicionar Música" no menu abre `AddMusicScene`, que pode retornar para o menu via botão Cancelar ou `Esc`.
5. Todas as cenas chamam `self.app.change_scene(...)` para navegar e aproveitam `self.app.toggle_fullscreen()` conforme necessário.
