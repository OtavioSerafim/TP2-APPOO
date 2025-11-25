"""Cena de seleção de músicas do jogo."""

import pygame
import pathlib

from .base import BaseScene
from entities.Music import Music
from utils.buttons import Button, ButtonTheme
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, SCREEN_WIDTH, SCREEN_HEIGHT

class MusicSelectScene(BaseScene):
    """Cena com lista das músicas disponíveis e pré-visualização da música selecionada"""
    def __init__(self, app) -> None:
        """Configura fontes, tema e layout inicial do menu."""
        super().__init__()
        self.app = app
        self.title_font = pygame.font.Font(None, 82)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 42)
        self.theme = ButtonTheme(
            background=(42, 52, 71),
            background_hover=(70, 92, 141),
            border=(20, 28, 43),
            text=COLOR_TEXT,
        )
        self.leaderboard_font = pygame.font.Font(None, 34)
        self.leaderboard_small_font = pygame.font.Font(None, 26)
        self._song_panel_margin = 28
        self.leaderboard_entries: list = []
        self.player_best_entry = None
        self.buttons = self._build_buttons()
        self._title_pos = (SCREEN_WIDTH + 60, SCREEN_HEIGHT + 60)
        self._subtitle_pos = (SCREEN_WIDTH + 120, SCREEN_HEIGHT + 60)
        self._layout_size = (0, 0)
        self._apply_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Músicas válidas
        self.songs = self._load_songs()
        self.selected_index = 0
        self._refresh_song_stats()

    def _build_buttons(self) -> list[Button]:
        """Cria os botões com seus respectivos callbacks."""
        labels_callbacks = [
            ("Voltar", self._on_home_selected),
            ("Adicionar Música", self._on_add_music_selected),
            ("Tela Cheia", self._on_toggle_fullscreen),
        ]
        return [
            Button(pygame.Rect(0, 0, 0, 0), label, self.button_font, callback, self.theme)
            for (label, callback) in labels_callbacks
        ]
    
    def _apply_layout(self, width: int, height: int) -> None:
        """Posiciona os botões conforme o tamanho da tela."""
        button_width = min(250, int(width * 0.3))
        button_height = 60
        spacing = 20
        
        # Posiciona botões no canto inferior direito
        start_x = width - button_width - 40
        start_y = height - (len(self.buttons) * (button_height + spacing)) - 40
        
        for index, button in enumerate(self.buttons):
            y = start_y + index * (button_height + spacing)
            button.rect = pygame.Rect(start_x, y, button_width, button_height)
        
        self._layout_size = (width, height)
    
    def _load_songs(self) -> list[dict]:
        """Escaneia a pasta 'musics' por músicas válidas."""
        print("Carregando músicas...")
        songs_dir = pathlib.Path("musics")
        song_list = []

        # Itera pelas pastas em 'musics'
        for song_folder in songs_dir.iterdir():
            # Valida existência dos arquivos necessários
            if song_folder.is_dir():
                csv_file = list(song_folder.glob("*.csv"))
                mp3_file = list(song_folder.glob("*.mp3"))

                # Se ambos existirem e só um de cada, a música é válida
                if len(csv_file) == 1 and len(mp3_file) == 1:
                    song_data = Music(song_folder.name, csv_file[0], mp3_file[0])
                    song_list.append(song_data) # Adiciona à lista de músicas válidas
                    print(f"Música encontrada: {song_data.title}")
                else:
                    print(f"Pasta '{song_folder.name}' ignorada: requer 1 CSV e 1 MP3")

        if len(song_list) == 0:
            print("Nenhuma música válida encontrada!")

        # Retorna músicas válidas
        return song_list

    def _refresh_song_stats(self) -> None:
        """Atualiza leaderboard e melhor play do jogador para a música atual."""
        self.leaderboard_entries = []
        self.player_best_entry = None
        if not self.songs:
            return

        play_model = getattr(self.app.models, "play", None)
        if play_model is None:
            return

        song = self.songs[self.selected_index]
        music_name = getattr(song, "title", None)
        if not music_name:
            return

        try:
            entries = play_model.leaderboard_for_music(music_name, limit=10)
            self.leaderboard_entries = [dict(row) for row in entries] if entries else []
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao carregar leaderboard para '{music_name}': {exc}")
            self.leaderboard_entries = []

        player = getattr(self.app, "active_player", None)
        if player is None:
            return

        try:
            player_id = int(player["id"])
        except (KeyError, TypeError, ValueError):
            print("Jogador ativo inválido; não foi possível obter melhor partida.")
            return

        try:
            best = play_model.best_for_player_and_music(player_id, music_name)
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao carregar melhor partida do jogador: {exc}")
            best = None

        self.player_best_entry = dict(best) if best else None

    def _play_preview(self) -> None:
        """Toca trecho da música selecionada"""
        if not self.songs:
            return
        
        try:
            song = self.songs[self.selected_index]
            pygame.mixer.music.load(song.mp3_path)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(loops = 0, start = 30.0, fade_ms = 500)
        
        except pygame.error as e:
            print(f"Erro ao carregar o preview: {e}")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Lida com a seleção (teclas cima/baixo) e confirmação (Enter)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.songs:
                    self.selected_index = (self.selected_index + 1) % len(self.songs)
                    self._play_preview()
                    self._refresh_song_stats()
            
            elif event.key == pygame.K_UP:
                if self.songs:
                    self.selected_index = (self.selected_index - 1) % len(self.songs)
                    self._play_preview()
                    self._refresh_song_stats()
            
            elif event.key == pygame.K_RETURN: # Tecla Enter
                self._on_song_selected()

            elif event.key == pygame.K_ESCAPE: # Voltar para o menu
                self._on_home_selected()


    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        self.draw_background(surface, COLOR_BACKGROUND)
        width, height = surface.get_size()

        # Preview (esquerda)
        preview_panel_rect = pygame.Rect(0, 0, width // 2, height)
        preview_surface = surface.subsurface(preview_panel_rect)
        self._render_song_panel(preview_surface)
        # pygame.draw.rect(surface, (255, 0, 0), preview_panel_rect, 3)

        # Músicas (direita)
        music_selection_rect = pygame.Rect(width // 2, 0, width // 2, height)
        music_surface = surface.subsurface(music_selection_rect)
        self.render_music_list(music_surface)
        # pygame.draw.rect(surface, (0, 0, 255), music_selection_rect, 3)

        pygame.draw.line(
            surface,
            COLOR_TEXT_MUTED,
            (width // 2, self._song_panel_margin),
            (width // 2, height - self._song_panel_margin),
            2,
        )

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Quebra o texto em múltiplas linhas se exceder a largura máxima."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]

    def _render_song_panel(self, surface: pygame.Surface) -> None:
        """Renderiza informações detalhadas da música selecionada."""
        surface.fill(COLOR_BACKGROUND)
        margin = self._song_panel_margin
        width = surface.get_width()
        height = surface.get_height()
        max_width = width - margin * 2

        if not self.songs:
            no_song_font = pygame.font.Font(None, int(self.title_font.get_height() * 0.75))
            txt = no_song_font.render("Nenhuma música", True, COLOR_TEXT_MUTED)
            surface.blit(txt, txt.get_rect(center=surface.get_rect().center))
            return

        song = self.songs[self.selected_index]

        title_lines = self._wrap_text(song.title, self.title_font, max_width)
        y = margin
        for line in title_lines:
            title_surface = self.title_font.render(line, True, COLOR_PRIMARY)
            surface.blit(title_surface, (margin, y))
            y += title_surface.get_height() + 6
        y += 10

        header_surface = self.subtitle_font.render("Top 10 partidas", True, COLOR_TEXT)
        surface.blit(header_surface, (margin, y))
        y += header_surface.get_height() + 12

        best_lines: list[tuple[str, tuple[int, int, int]]] = []
        if self.player_best_entry is not None:
            best = self.player_best_entry
            best_lines.append(("Sua melhor partida", COLOR_PRIMARY))
            best_lines.append((f"Pontos: {best.get('score', 0)} pts", COLOR_TEXT))
            best_lines.append(
                (
                    f"Perfeitas {best.get('perfect_hits', 0)} | Boas {best.get('good_hits', 0)} | Erros {best.get('errors', 0)}",
                    COLOR_TEXT,
                )
            )
            best_lines.append((f"Quando: {self._format_played_at(best.get('played_at'))}", COLOR_TEXT_MUTED))
        elif getattr(self.app, "active_player", None) is not None:
            best_lines.append(("Nenhuma partida sua ainda.", COLOR_TEXT_MUTED))
        else:
            best_lines.append(("Nenhum jogador ativo.", COLOR_TEXT_MUTED))

        best_area_height = 0
        for text, _color in best_lines:
            display_text = self._truncate_text(text, self.leaderboard_small_font, max_width)
            best_area_height += self.leaderboard_small_font.size(display_text)[1]
        if best_lines:
            best_area_height += (len(best_lines) - 1) * 6
        best_area_top = height - margin - best_area_height

        if not self.leaderboard_entries:
            empty_message = self._truncate_text("Nenhuma partida registrada.", self.leaderboard_small_font, max_width)
            empty_surface = self.leaderboard_small_font.render(empty_message, True, COLOR_TEXT_MUTED)
            empty_y = min(best_area_top - empty_surface.get_height(), y)
            surface.blit(empty_surface, (margin, max(margin, empty_y)))
        else:
            for rank, row in enumerate(self.leaderboard_entries, start=1):
                player_name = str(row.get("player_name") or f"Jogador #{row.get('player_id', '?')}")
                score = row.get("score", 0)
                line = f"{rank:>2}. {player_name} - {score} pts"
                display_line = self._truncate_text(line, self.leaderboard_font, max_width)
                color = COLOR_PRIMARY if rank == 1 else COLOR_TEXT
                entry_surface = self.leaderboard_font.render(display_line, True, color)
                entry_height = entry_surface.get_height()
                if y + entry_height > best_area_top - 10:
                    break
                surface.blit(entry_surface, (margin, y))
                y += entry_height + 8

        bottom_y = height - margin
        for text, color in reversed(best_lines):
            display_text = self._truncate_text(text, self.leaderboard_small_font, max_width)
            text_surface = self.leaderboard_small_font.render(display_text, True, color)
            bottom_y -= text_surface.get_height()
            surface.blit(text_surface, (margin, bottom_y))
            bottom_y -= 6

    def render_music_list(self, surface: pygame.Surface) -> None:
        """Renderiza painel de seleção das músicas"""
        line_height = 50
        total_height = len(self.songs) * line_height
        start_y = (surface.get_height() - total_height) // 2
        max_width = surface.get_width() * 0.85  # 85% da largura

        for index, song in enumerate(self.songs):
            is_selected = (index == self.selected_index)
            color = COLOR_PRIMARY if is_selected else COLOR_TEXT
            prefix = "> " if is_selected else "  "
            
            # Quebra o texto se necessário
            full_text = prefix + song.title
            lines = self._wrap_text(full_text, self.button_font, max_width)
            
            # Renderiza apenas a primeira linha
            text = lines[0] if lines else full_text
            if len(lines) > 1:
                text += "..."  # Indica que há mais texto
            
            txt_render = self.button_font.render(text, True, color)
            pos_x = surface.get_width() * 0.1
            pos_y = start_y + index * line_height
            surface.blit(txt_render, (pos_x, pos_y))

    def _truncate_text(self, text: str, font: pygame.font.Font, max_width: int) -> str:
        if font.size(text)[0] <= max_width:
            return text
        ellipsis = "..."
        available = text
        while available and font.size(available + ellipsis)[0] > max_width:
            available = available[:-1]
        return (available + ellipsis) if available else ellipsis

    def _format_played_at(self, value) -> str:
        if value is None:
            return "-"
        text = str(value)
        return text[:16] if len(text) > 16 else text

    def _on_song_selected(self) -> None:
        """Ao pressionar ENTER ou clicar na música, direciona para a cena de jogo"""
        if not self.songs:
            return
        
        pygame.mixer.music.stop()
        song = self.songs[self.selected_index]
        
        from .gameplay import GameplayScene # importação tardia evitando importação circular
        self.app.change_scene(GameplayScene(self.app, song))  # Passa dados da música

    def _on_home_selected(self) -> None:
        """Volta para o menu principal"""
        pygame.mixer.music.stop()
        from .menu import MenuScene
        self.app.change_scene(MenuScene(self.app))

    def _on_add_music_selected(self) -> None:
        """Direciona para a tela de adição de músicas"""
        print("TODO: fazer tela de adição de músicas")

    def _on_toggle_fullscreen(self) -> None:
        """Solicita ao controlador a alternância de modo de tela."""
        self.app.toggle_fullscreen()