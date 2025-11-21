import pygame

from .base import BaseScene
from utils.buttons import Button, ButtonTheme
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, SCREEN_WIDTH, SCREEN_HEIGHT
COLOR_YELLOW_BACKGROUND = (228, 177, 39)
COLOR_PINK_NOTE = (230, 52, 120)

class GameplayScene(BaseScene):
    """Cena onde ocorre toda a jogabilidade"""
    def __init__(self, app):
        self.app = app

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        surface.fill(COLOR_YELLOW_BACKGROUND)

        self.render_lane(surface) # lane
        self.render_hit_area(surface) # área de acerto

    def render_lane(self, surface: pygame.Surface) -> None:
        """Desenha a lane em que percorrem as notas"""
        width, height = surface.get_size()

        # lane
        self.lane_bottom = height // 2
        self.lane_top = self.lane_bottom - 200
        self.lane_rect = pygame.Rect(0, self.lane_top, width, 200)

        # desenha lane e suas bordas
        pygame.draw.rect(surface, COLOR_BACKGROUND, self.lane_rect)
        border_thickness = 2
        pygame.draw.line(surface, (255, 255, 255), (0, self.lane_top), (width - 1, self.lane_top), border_thickness)
        pygame.draw.line(surface, (255, 255, 255), (0, self.lane_bottom - 1), (width - 1, self.lane_bottom - 1), border_thickness)

    def render_hit_area(self, surface: pygame.Surface) -> None:
        """Desenha a área de acerto das notas"""
        hit_radius = 80
        hit_center_x = 300
        hit_center_y = self.lane_bottom - 100

        # superfície com alpha para efeito semi-transparente
        hit_surf = pygame.Surface((hit_radius * 2, hit_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(hit_surf, (255, 255, 255, 40), (hit_radius, hit_radius), hit_radius)           # hit area externa
        pygame.draw.circle(hit_surf, (255, 255, 255, 160), (hit_radius, hit_radius), 2 * hit_radius // 3) # núcleo
        surface.blit(hit_surf, (hit_center_x - hit_radius, hit_center_y - hit_radius))
    
    def render_note(self, surface: pygame.Surface, note_center_x: int, note_center_y: int) -> None:
        """Desenha uma nota"""
        note_radius = 160 // 3

        # superfície com alpha para efeito semi-transparente
        note_surf = pygame.Surface((note_radius * 2, note_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(note_surf, COLOR_PINK_NOTE, (note_radius, note_radius), note_radius)
        surface.blit(note_surf, (note_center_x - note_radius, note_center_y - note_radius))

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass