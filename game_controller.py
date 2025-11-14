"""Controlador principal do jogo com menu inicial em POO."""

import pygame

from scenes import BaseScene, MenuScene

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FRAME_RATE = 60

COLORS = {
    "background": (18, 18, 18),
    "primary": (235, 218, 168),
    "accent": (94, 131, 227),
    "text": (240, 240, 245),
    "text_muted": (160, 160, 168),
}


class GameApp:
    """Responsável pela inicialização do pygame e troca de cenas."""

    def __init__(self) -> None:
        pygame.init()
        self.window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Engrenada Hero")
        self.clock = pygame.time.Clock()
        self.running = False
        self.active_scene: BaseScene = MenuScene(self)

    def toggle_fullscreen(self) -> None:
        """Alterna entre modo janela e tela cheia."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.window_size)

    def change_scene(self, scene: BaseScene) -> None:
        """Atribui uma nova cena ativa ao aplicativo."""
        self.active_scene = scene

    def quit(self) -> None:
        """Encerra o loop principal do jogo de forma graciosa."""
        self.running = False

    def run(self) -> None:
        """Executa o loop principal tratando eventos, atualização e renderização."""
        self.running = True
        while self.running:
            dt = self.clock.tick(FRAME_RATE) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.active_scene.handle_event(event)

            self.active_scene.update(dt)
            self.active_scene.render(self.screen)
            pygame.display.flip()

        pygame.quit()


def main() -> None:
    """Inicializa e executa o aplicativo do jogo."""
    GameApp().run()


if __name__ == "__main__":
    main()