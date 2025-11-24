# game_controller.py

> Resumo do ponto de entrada do jogo, responsável por inicializar pygame e orquestrar o loop principal.

## Papel do Arquivo
- Define constantes globais (`SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FRAME_RATE`, `COLORS`) utilizadas pelas cenas.
- Instancia `GameApp`, que encapsula o ciclo de vida do pygame: janela, clock, cena ativa e estado de execução.
- Expõe `main()` como ponto de partida para scripts e importações.

## Classe `GameApp`
- Inicializa pygame, configura a janela inicial em modo janela (`800x600`) e registra o título "Engrenada Hero".
- Mantém a cena ativa por meio de um objeto que herda de `BaseScene` (`MenuScene` por padrão).
- Possui métodos auxiliares:
  - `toggle_fullscreen()` alterna entre modos janela e fullscreen.
  - `change_scene(scene)` substitui a cena ativa por outra instância.
  - `quit()` encerra o loop principal com segurança.

## Loop Principal (`run`)
1. Liga `self.running = True` e inicia o controle de tempo com `clock.tick(FRAME_RATE)`.
2. Percorre os eventos do pygame:
   - `QUIT` finaliza a aplicação.
   - Demais eventos são delegados para `active_scene.handle_event(event)`.
3. Atualiza e renderiza:
   - `active_scene.update(dt)` para lógicas dependentes de tempo.
   - `active_scene.render(surface)` para desenhar na tela corrente.
4. Executa `pygame.display.flip()` para exibir o frame.
5. Ao sair do loop, fecha pygame com `pygame.quit()`.

## Execução Direta
- `python game_controller.py` chama `main()` e inicia o jogo.
- As cenas são responsáveis por chamar `app.change_scene(...)` quando o fluxo deve trocar.
- Utilize `GameApp.toggle_fullscreen()` (ligado ao botão "Tela Cheia" do menu) para alternar modos durante testes.

## Interações com Outras Camadas
- Cenas importam `GameApp` apenas como dependência leve; não há ciclo de importação porque `GameApp` só instancia cenas após pygame estar pronto.
- `Models` e demais serviços são instanciados pelas cenas conforme necessário, mantendo o controlador principal enxuto.
