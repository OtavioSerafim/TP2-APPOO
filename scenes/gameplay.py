import pygame

from .base import BaseScene
from utils.buttons import Button, ButtonTheme
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, SCREEN_WIDTH, SCREEN_HEIGHT
COLOR_YELLOW_BACKGROUND = (228, 177, 39)

class GameplayScene(BaseScene):
    """Cena onde ocorre toda a jogabilidade"""
    def __init__(self, app):
        self.app = app

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        surface.fill(COLOR_YELLOW_BACKGROUND)
        width, height = surface.get_size()

        # lane
        lane_bottom = height // 2
        lane_top = lane_bottom - 200
        lane_rect = pygame.Rect(0, lane_top, width, 200)

        # desenha lane e suas bordas
        pygame.draw.rect(surface, COLOR_BACKGROUND, lane_rect)
        border_thickness = 2
        pygame.draw.line(surface, (255, 255, 255), (0, lane_top), (width - 1, lane_top), border_thickness)
        pygame.draw.line(surface, (255, 255, 255), (0, lane_bottom - 1), (width - 1, lane_bottom - 1), border_thickness)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass