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
- Além dos botões principais (Play, Adicionar Música, Tela Cheia, Sair), renderiza no canto inferior esquerdo um painel de login simples:
  - Campo de texto para informar o nome do jogador e botão **Salvar** para criar ou reutilizar o registro (`Models.player`).
  - Quando há um jogador ativo, substitui o campo por uma placa informativa e exibe botão **Deslogar**.
- Mantém feedback textual curto (sucesso/erro) ao lado do campo.
- Garante layout responsivo e fixa o botão "Sair" no canto inferior direito.
- Ao confirmar um jogador, atualiza `app.active_player` e mantém o objeto disponível para outras cenas.

## `MusicSelectScene`
- Lista músicas válidas na pasta `musics/` (exige exatamente um `.csv` e um `.mp3`).
- Permite navegação por teclado (`↑`, `↓`, `Enter`, `Esc`) e prévia de áudio com `pygame.mixer.music`.
- Painel esquerdo agora exibe:
  - Título da música alinhado ao canto superior esquerdo.
  - Leaderboard com as 10 melhores partidas daquela música (`Models.play.leaderboard_for_music`).
  - No rodapé, o melhor resultado do jogador ativo, se existir (`Models.play.best_for_player_and_music`).
- Painel direito continua mostrando a lista de músicas com destaque na selecionada.
- `_refresh_song_stats()` é chamado sempre que a seleção muda para atualizar os dados.

## `AddMusicScene`
- Formulário para criar uma nova música a partir de um arquivo ZIP.
- Usa `utils.InputField` para campos "Nome da música" e "Arquivo ZIP".
- Integra com `tkinter.filedialog` (opcional) para selecionar o arquivo em uma janela nativa.
- `_import_song` extrai o ZIP em diretório temporário, valida `.csv`/`.mp3` e salva em `musics/<nome_sanitizado>/`.
- Exibe feedback de sucesso/erro na parte inferior da tela.

## `GameplayScene`
- Cena de execução rítmica.
- Carrega o `CSV` associado à música selecionada, gera instâncias de `entities.Notes.*` e agenda o spawn das notas com base no tempo de antecipação calculado a partir da velocidade de movimento.
- Durante o loop:
  - Gerencia acertos com tolerância para perfeitos (100 pts) e bons (50 pts).
  - Aplica feedback visual, animações de fade/fall e contabiliza estatísticas (perfeitas, boas, erros).
- Ao fim da música (todas as notas consumidas ou expiradas):
  - Faz fade to black de 2 segundos, pausa/encerra a trilha e mostra tela de resultados.
  - Persiste a partida na tabela `plays` usando `app.models.play` (incluindo score, erros e breakdown de acertos) quando há jogador ativo.
  - Exibe mensagem contextual e aguarda `Enter/Esc` para iniciar um novo fade de saída e retornar à `MusicSelectScene`.

## Fluxo de Transição
1. `GameApp` inicia com `MenuScene`.
2. "Play" envia para `MusicSelectScene`.
3. `MusicSelectScene` deverá criar `GameplayScene` quando `Enter` for pressionado (TODO).
4. "Adicionar Música" no menu abre `AddMusicScene`, que pode retornar para o menu via botão Cancelar ou `Esc`.
5. Todas as cenas chamam `self.app.change_scene(...)` para navegar e aproveitam `self.app.toggle_fullscreen()` conforme necessário.
