"""Componentes reutilizáveis de botões para interfaces pygame."""

from typing import Callable

import pygame

from .constants import (
    COLOR_BUTTON_BACKGROUND,
    COLOR_BUTTON_BACKGROUND_HOVER,
    COLOR_BUTTON_BORDER,
    COLOR_TEXT,
)


class ButtonTheme:
    """Agrupa cores utilizadas pelos botões."""

    def __init__(
        self,
        background: tuple[int, int, int] | None = None,
        background_hover: tuple[int, int, int] | None = None,
        border: tuple[int, int, int] | None = None,
        text: tuple[int, int, int] | None = None,
    ) -> None:
        self.background = background or COLOR_BUTTON_BACKGROUND
        self.background_hover = background_hover or COLOR_BUTTON_BACKGROUND_HOVER
        self.border = border or COLOR_BUTTON_BORDER
        self.text = text or COLOR_TEXT


class Button:
    """Componente simples de botão com callback."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        font: pygame.font.Font,
        on_click: Callable[[], None],
        theme: ButtonTheme,
    ) -> None:
        self.rect = rect
        self.label = label
        self.font = font
        self.on_click = on_click
        self.theme = theme
        self._is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos de mouse para interação com o botão."""
        if event.type == pygame.MOUSEMOTION:
            self._is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha o botão na superfície fornecida."""
        background = self.theme.background_hover if self._is_hovered else self.theme.background
        pygame.draw.rect(surface, background, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.theme.border, self.rect, width=2, border_radius=8)

        text_surface = self.font.render(self.label, True, self.theme.text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
