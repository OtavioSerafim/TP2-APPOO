"""Widget simples de texto para formulários em pygame."""

from __future__ import annotations

import pygame

from .constants import (
    COLOR_INPUT_BACKGROUND,
    COLOR_INPUT_BORDER,
    COLOR_INPUT_BORDER_ACTIVE,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)


class InputField:
    """Campo de texto reutilizável com suporte a foco e cursor piscante."""

    def __init__(
        self,
        label: str,
        placeholder: str,
        rect: pygame.Rect,
        font: pygame.font.Font,
        label_font: pygame.font.Font,
    ) -> None:
        self.label = label
        self.placeholder = placeholder
        self.rect = rect
        self.font = font
        self.label_font = label_font
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self._cursor_timer = 0.0
        self._max_length = 220
        self._pending_change = False
        self._backspace_held = False
        self._backspace_timer = 0.0
        self._backspace_delay = 0.35
        self._backspace_interval = 0.06

    def set_rect(self, rect: pygame.Rect) -> None:
        """Atualiza a posição e tamanho do campo."""
        self.rect = rect

    def set_active(self, is_active: bool) -> None:
        """Ativa ou desativa o campo de texto."""
        self.active = is_active
        if is_active:
            self.cursor_visible = True
            self._cursor_timer = 0.0
        else:
            self._backspace_held = False

    def _mark_changed(self) -> None:
        """Marca que o texto sofreu alteração."""
        self._pending_change = True
        self.cursor_visible = True
        self._cursor_timer = 0.0

    def clear(self, *, silent: bool = False) -> None:
        """Limpa o conteúdo do campo."""
        self.text = ""
        self._backspace_held = False
        self._backspace_timer = 0.0
        if silent:
            self.cursor_visible = True
            self._cursor_timer = 0.0
            self._pending_change = False
        else:
            self._mark_changed()

    def set_text(self, text: str) -> None:
        """Define o conteúdo do campo respeitando o limite máximo."""
        if text is None:
            value = ""
        else:
            value = str(text)
        self.text = value[: self._max_length]
        self._backspace_held = False
        self._backspace_timer = 0.0
        self._mark_changed()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa teclas quando o campo está ativo."""
        if not self.active:
            return False

        if event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE:
            self._backspace_held = False
            return False

        if event.type != pygame.KEYDOWN:
            return False

        text_changed = False
        if event.key == pygame.K_BACKSPACE:
            if self.text:
                self.text = self.text[:-1]
                text_changed = True
            self._backspace_held = True
            self._backspace_timer = self._backspace_delay
        elif event.key == pygame.K_DELETE:
            if self.text:
                self.clear()
                text_changed = True
            self._backspace_held = False
        else:
            if event.unicode and event.unicode.isprintable():
                if len(self.text) < self._max_length:
                    self.text += event.unicode
                    text_changed = True
            self._backspace_held = False

        if text_changed:
            self._mark_changed()
        return text_changed

    def update(self, dt: float) -> None:
        """Atualiza animação do cursor piscante."""
        if not self.active:
            return
        if self._backspace_held:
            self._backspace_timer -= dt
            if self._backspace_timer <= 0:
                if self.text:
                    self.text = self.text[:-1]
                    self._mark_changed()
                    self._backspace_timer += self._backspace_interval
                else:
                    self._backspace_held = False
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self._cursor_timer = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza o campo, incluindo rótulo e texto."""
        label_surface = self.label_font.render(self.label, True, COLOR_TEXT)
        label_rect = label_surface.get_rect()
        label_rect.left = self.rect.left
        label_rect.bottom = self.rect.top - 8
        surface.blit(label_surface, label_rect)

        background_color = COLOR_INPUT_BACKGROUND
        border_color = COLOR_INPUT_BORDER_ACTIVE if self.active else COLOR_INPUT_BORDER
        pygame.draw.rect(surface, background_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        available_width = self.rect.width - 24
        if self.text:
            display_text = self.text
            while self.font.size(display_text)[0] > available_width and len(display_text) > 1:
                display_text = display_text[1:]
            if display_text != self.text:
                display_text = "..." + display_text
            text_color = COLOR_TEXT
        else:
            display_text = self.placeholder
            text_color = COLOR_TEXT_MUTED

        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.left = self.rect.left + 12
        text_rect.centery = self.rect.centery
        surface.blit(text_surface, text_rect)

        if self.active and self.cursor_visible:
            if self.text:
                cursor_x = text_rect.right + 2
            else:
                cursor_x = text_rect.left + 2
            cursor_rect = pygame.Rect(cursor_x, text_rect.top + 4, 2, text_rect.height - 8)
            pygame.draw.rect(surface, COLOR_TEXT, cursor_rect)

    def poll_text_changed(self) -> bool:
        """Indica se o conteúdo foi alterado desde a última sondagem."""
        changed = self._pending_change
        self._pending_change = False
        return changed
