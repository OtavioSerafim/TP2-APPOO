"""Cena de menu inicial do jogo."""

import pygame

from .base import BaseScene
from .music_select import MusicSelectScene
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, SCREEN_WIDTH, SCREEN_HEIGHT
from utils.buttons import Button, ButtonTheme

SUBTITLE_TEXT = "Pressione um botão para começar"


class MenuScene(BaseScene):
    """Cena inicial com os botões Play, Adicionar Música e Sair."""

    def __init__(self, app) -> None:
        """Configura fontes, tema e layout inicial do menu."""
        self.app = app
        self.title_font = pygame.font.Font(None, 82)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 42)
        self.theme = ButtonTheme()
        self.buttons = self._build_buttons()
        self._title_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        self._subtitle_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60)
        self._layout_size = (0, 0)
        self._apply_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

    def _build_buttons(self) -> list[Button]:
        """Cria os botões com seus respectivos callbacks."""
        labels_callbacks = [
            ("Play", self._on_play_selected),
            ("Adicionar Música", self._on_add_music_selected),
            ("Tela Cheia", self._on_toggle_fullscreen),
            ("Sair", self.app.quit),
        ]
        return [
            Button(pygame.Rect(0, 0, 0, 0), label, self.button_font, callback, self.theme)
            for (label, callback) in labels_callbacks
        ]

    def _apply_layout(self, width: int, height: int) -> None:
        """Posiciona título, subtítulo e botões conforme o tamanho da tela."""
        button_width = min(420, int(width * 0.45))
        button_height = 70
        spacing = max(24, button_height // 3)

        title_y = max(int(height * 0.25), 80)
        subtitle_y = title_y + 60
        block_height = len(self.buttons) * button_height + (len(self.buttons) - 1) * spacing
        block_start_y = height // 2 - block_height // 2 + 40
        start_y = max(block_start_y, subtitle_y + 60)

        for index, button in enumerate(self.buttons):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.centerx = width // 2
            rect.y = start_y + index * (button_height + spacing)
            button.rect = rect

        self._title_pos = (width // 2, title_y)
        self._subtitle_pos = (self._title_pos[0], subtitle_y)
        self._layout_size = (width, height)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Repasa eventos de entrada para cada botão renderizado."""
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        """Menu não possui atualizações dependentes do tempo por enquanto."""

    def render(self, surface: pygame.Surface) -> None:
        """Redesenha o plano de fundo, textos e botões do menu."""
        width, height = surface.get_size()
        if (width, height) != self._layout_size:
            self._apply_layout(width, height)

        surface.fill(COLOR_BACKGROUND)
        title = self.title_font.render("Engrenada Hero", True, COLOR_PRIMARY)
        surface.blit(title, title.get_rect(center=self._title_pos))

        subtitle = self.subtitle_font.render(SUBTITLE_TEXT, True, COLOR_TEXT_MUTED)
        surface.blit(subtitle, subtitle.get_rect(center=self._subtitle_pos))

        for button in self.buttons:
            button.draw(surface)

    def _on_play_selected(self) -> None:
        """Alterna para a cena de seleção de músicas"""
        self.app.change_scene(MusicSelectScene(self.app))

    def _on_add_music_selected(self) -> None:
        """Placeholder para o fluxo de cadastro de músicas."""
        print("[TODO] Adicionar música: implemente fluxo de cadastro.")

    def _on_toggle_fullscreen(self) -> None:
        """Solicita ao controlador a alternância de modo de tela."""
        self.app.toggle_fullscreen()
