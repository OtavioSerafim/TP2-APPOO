"""Cena de menu inicial do jogo."""

import pygame

from .base import BaseScene
from .music_select import MusicSelectScene
from .add_music import AddMusicScene
from utils.constants import (
    COLOR_BACKGROUND,
    COLOR_PRIMARY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_ERROR,
    COLOR_INPUT_BACKGROUND,
    COLOR_INPUT_BORDER,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from utils.buttons import Button, ButtonTheme
from utils.input_field import InputField


SUBTITLE_TEXT = "Pressione um botão para começar"


class MenuScene(BaseScene):
    """Cena inicial com os botões Play, Adicionar Música e Sair."""

    def __init__(self, app) -> None:
        """Configura fontes, tema e layout inicial do menu."""
        super().__init__(background_name="menu_background.png")
        self.app = app
        self.title_font = pygame.font.Font(None, 82)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 42)
        self.theme = ButtonTheme()
        self.buttons = self._build_buttons()
        self.player_input_font = pygame.font.Font(None, 30)
        self.player_label_font = pygame.font.Font(None, 24)
        self.player_button_font = pygame.font.Font(None, 28)
        self.player_feedback_font = pygame.font.Font(None, 22)
        self.player_field = InputField(
            label="Jogador",
            placeholder="Digite seu nome",
            rect=pygame.Rect(0, 0, 0, 0),
            font=self.player_input_font,
            label_font=self.player_label_font,
        )
        self.player_confirm_button = Button(
            pygame.Rect(0, 0, 0, 0),
            "Salvar",
            self.player_button_font,
            self._on_player_confirm,
            self.theme,
        )
        self.player_exit_button = Button(
            pygame.Rect(0, 0, 0, 0),
            "Sair",
            self.player_button_font,
            self.app.quit,
            self.theme,
        )
        self.player_logout_button = Button(
            pygame.Rect(0, 0, 0, 0),
            "Deslogar",
            self.player_button_font,
            self._on_player_logout,
            self.theme,
        )
        self.player_feedback_text = ""
        self.player_feedback_color = COLOR_TEXT_MUTED
        self._player_feedback_pos = (0, 0)
        self._player_display_rect = pygame.Rect(0, 0, 0, 0)
        stored_player = getattr(self.app, "active_player", None)
        if stored_player:
            try:
                stored_name = str(stored_player["name"]).strip()
            except (KeyError, TypeError):
                stored_name = ""
            if stored_name:
                self.player_field.set_text(stored_name)
        self._show_player_input = True
        self._update_player_mode()
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
        vertical_shift = -50

        title_y = max(int(height * 0.25) + vertical_shift, 80)
        subtitle_y = title_y + 60
        block_height = len(self.buttons) * button_height + (len(self.buttons) - 1) * spacing
        block_start_y = height // 2 - block_height // 2 + vertical_shift
        start_y = max(block_start_y, subtitle_y + 60)

        for index, button in enumerate(self.buttons):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.centerx = width // 2
            rect.y = start_y + index * (button_height + spacing)
            button.rect = rect

        corner_padding = 32
        field_height = 52
        field_width = min(280, int(width * 0.35))
        field_rect = pygame.Rect(
            corner_padding,
            height - field_height - corner_padding,
            field_width,
            field_height,
        )
        self.player_field.set_rect(field_rect)
        self._player_display_rect = field_rect.copy()

        button_spacing = 12
        player_buttons = self._player_local_buttons()

        def compute_button_rects(anchor: pygame.Rect) -> list[tuple[Button, pygame.Rect]]:
            rects: list[tuple[Button, pygame.Rect]] = []
            current_x = anchor.right + button_spacing
            for btn in player_buttons:
                label_width = self.player_button_font.size(btn.label)[0]
                button_width = max(96, label_width + 28)
                rect = pygame.Rect(current_x, anchor.top, button_width, field_height)
                rects.append((btn, rect))
                current_x = rect.right + button_spacing
            return rects

        button_rects = compute_button_rects(field_rect)
        total_right = button_rects[-1][1].right if button_rects else field_rect.right
        overshoot = total_right + corner_padding - width
        if overshoot > 0:
            field_rect.x = max(corner_padding, field_rect.x - overshoot)
            self.player_field.set_rect(field_rect)
            self._player_display_rect = field_rect.copy()
            button_rects = compute_button_rects(field_rect)

        for button, rect in button_rects:
            button.rect = rect

        self._player_feedback_pos = (field_rect.left, field_rect.bottom + 8)

        exit_width = max(120, self.player_button_font.size(self.player_exit_button.label)[0] + 28)
        exit_rect = pygame.Rect(
            width - corner_padding - exit_width,
            height - field_height - corner_padding,
            exit_width,
            field_height,
        )
        self.player_exit_button.rect = exit_rect

        self._title_pos = (width // 2, title_y)
        self._subtitle_pos = (self._title_pos[0], subtitle_y)
        self._layout_size = (width, height)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Repasa eventos de entrada para os botões e campo do menu."""
        if self._show_player_input:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player_field.rect.collidepoint(event.pos):
                    self.player_field.set_active(True)
                elif any(btn.rect.collidepoint(event.pos) for btn in self._player_local_buttons()):
                    self.player_field.set_active(True)
                else:
                    self.player_field.set_active(False)

            if self.player_field.handle_event(event):
                self._clear_player_feedback()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.player_field.active:
                self._on_player_confirm()
                return
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player_field.set_active(False)

        for button in self._player_local_buttons():
            button.handle_event(event)

        self.player_exit_button.handle_event(event)

        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        """Atualiza elementos animados do menu, como o cursor do campo."""
        if self._show_player_input:
            self.player_field.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Redesenha o plano de fundo, textos e botões do menu."""
        width, height = surface.get_size()
        if (width, height) != self._layout_size:
            self._apply_layout(width, height)

        self.draw_background(surface, COLOR_BACKGROUND)

        title = self.title_font.render("Engrenada Hero", True, COLOR_PRIMARY)
        title_rect = title.get_rect(center=self._title_pos)

        title_shadow = self.title_font.render("Engrenada Hero", True, (0, 0, 0))
        title_shadow = title_shadow.convert_alpha()
        title_shadow.set_alpha(190)
        shadow_rect = title_rect.move(4, 4)
        surface.blit(title_shadow, shadow_rect)
        surface.blit(title, title_rect)

        subtitle = self.subtitle_font.render(SUBTITLE_TEXT, True, COLOR_TEXT_MUTED)
        surface.blit(subtitle, subtitle.get_rect(center=self._subtitle_pos))

        for button in self.buttons:
            button.draw(surface)

        if self._show_player_input:
            self.player_field.draw(surface)
        else:
            rect = self._player_display_rect
            label_surface = self.player_label_font.render("Jogador", True, COLOR_TEXT)
            label_rect = label_surface.get_rect()
            label_rect.left = rect.left
            label_rect.bottom = rect.top - 8
            surface.blit(label_surface, label_rect)

            pygame.draw.rect(surface, COLOR_INPUT_BACKGROUND, rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_INPUT_BORDER, rect, width=2, border_radius=8)

            name = self._get_active_player_name()
            available_width = rect.width - 24
            display_text = name or "Jogador ativo"
            if name:
                while self.player_input_font.size(display_text)[0] > available_width and len(display_text) > 1:
                    display_text = display_text[1:]
                if display_text != name:
                    display_text = "..." + display_text
                text_color = COLOR_TEXT
            else:
                text_color = COLOR_TEXT_MUTED
            text_surface = self.player_input_font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.left = rect.left + 12
            text_rect.centery = rect.centery
            surface.blit(text_surface, text_rect)

        for button in self._player_local_buttons():
            button.draw(surface)

        self.player_exit_button.draw(surface)

        if self.player_feedback_text:
            feedback_surface = self.player_feedback_font.render(
                self.player_feedback_text,
                True,
                self.player_feedback_color,
            )
            feedback_rect = feedback_surface.get_rect()
            feedback_rect.topleft = self._player_feedback_pos
            surface.blit(feedback_surface, feedback_rect)

    def _clear_player_feedback(self) -> None:
        """Remove mensagens temporárias quando o texto é editado."""
        if self.player_feedback_text:
            self.player_feedback_text = ""
            self.player_feedback_color = COLOR_TEXT_MUTED

    def _set_player_feedback(self, message: str, *, is_error: bool = False) -> None:
        """Exibe mensagem curta junto ao campo de jogador."""
        self.player_feedback_text = message
        self.player_feedback_color = COLOR_ERROR if is_error else COLOR_PRIMARY

    def _player_local_buttons(self) -> list[Button]:
        """Retorna os botões associados ao painel local do jogador."""
        if self._show_player_input:
            return [self.player_confirm_button]
        return [self.player_logout_button]

    def _update_player_mode(self) -> None:
        """Habilita campo ou painel conforme o jogador ativo."""
        has_player = getattr(self.app, "active_player", None) is not None
        self._show_player_input = not has_player
        self.player_field.set_active(self._show_player_input)
        layout_size = getattr(self, "_layout_size", None)
        if layout_size:
            width, height = layout_size
            if width and height:
                self._apply_layout(width, height)

    def _get_active_player_name(self) -> str:
        """Retorna o nome do jogador ativo ou string vazia."""
        player = getattr(self.app, "active_player", None)
        if player is None:
            return ""
        try:
            return str(player["name"]).strip()
        except (KeyError, TypeError):
            return ""

    def _on_player_logout(self) -> None:
        """Remove o jogador ativo e reabre o campo de texto."""
        self.app.active_player = None
        self.player_field.clear(silent=True)
        self._set_player_feedback("Jogador desconectado.", is_error=False)
        self._update_player_mode()

    def _on_player_confirm(self) -> None:
        """Garante que o jogador informado exista e o torna ativo."""
        name = self.player_field.text.strip()
        if not name:
            self._set_player_feedback("Informe um nome para jogar.", is_error=True)
            return

        try:
            player_model = self.app.models.player
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao acessar modelo Player: {exc}")
            self._set_player_feedback("Não foi possível acessar os jogadores.", is_error=True)
            return

        try:
            existing = player_model.get_by_name(name)
        except ValueError as exc:
            self._set_player_feedback(str(exc), is_error=True)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao buscar jogador: {exc}")
            self._set_player_feedback("Falha ao buscar jogador.", is_error=True)
            return

        if existing:
            canonical_name = str(existing["name"]).strip()
            self.app.active_player = existing
            if canonical_name:
                self.player_field.set_text(canonical_name)
            self._update_player_mode()
            self._set_player_feedback(f"Bem-vindo de volta, {canonical_name}!", is_error=False)
            return

        try:
            new_id = player_model.create({"name": name})
            created = player_model.read(new_id)
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao criar jogador: {exc}")
            self._set_player_feedback("Não foi possível criar o jogador.", is_error=True)
            return

        if created is None:
            self._set_player_feedback(
                "Jogador criado, mas não foi possível carregar os dados.",
                is_error=True,
            )
            return

        canonical_name = str(created["name"]).strip()
        self.app.active_player = created
        if canonical_name:
            self.player_field.set_text(canonical_name)
        self._update_player_mode()
        self._set_player_feedback("Jogador criado com sucesso!", is_error=False)

    def _on_play_selected(self) -> None:
        """Alterna para a cena de seleção de músicas"""
        self.app.change_scene(MusicSelectScene(self.app))

    def _on_add_music_selected(self) -> None:
        """Alterna para a cena de adição de músicas."""
        self.app.change_scene(AddMusicScene(self.app))

    def _on_toggle_fullscreen(self) -> None:
        """Solicita ao controlador a alternância de modo de tela."""
        self.app.toggle_fullscreen()
