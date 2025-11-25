import pygame
import csv
from datetime import datetime
from pathlib import Path

from entities.Notes.Note import Note
from entities.Notes.agudo.Agudo import Agudo
from entities.Notes.grave.Grave import Grave
from entities.Notes.flam.Flam import Flam
from entities.Notes.mao.Mao import Mao
from .base import BaseScene
from utils.constants import (
    COLOR_BACKGROUND,
    COLOR_YELLOW_BACKGROUND,
    COLOR_PINK_NOTE,
    COLOR_BLUE_NOTE,
    COLOR_GREEN_NOTE,
    COLOR_YELLOW_NOTE,
    COLOR_PERFECT_HIT,
    COLOR_GOOD_HIT,
    COLOR_MISS,
    COLOR_PRIMARY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)
from .music_select import MusicSelectScene

class GameplayScene(BaseScene):
    """Cena onde ocorre toda a jogabilidade"""
    def __init__(self, app, song_data: dict):
        self.key_cooldown = 10  # ms entre hits da mesma tecla
        self.last_key_hit_time = {}  # key -> ticks
        self.app = app
        self.song_data = song_data
        self.note_radius = 160 // 3
        self.note_speed = 450
        self.hit_area_x = 300
        self.hit_tolerance = 80  # Raio da hit area
        self.notes = []  # Notas ativas na tela
        self.note_queue = []  # Notas aguardando spawn (do CSV)
        self.start_time = None  # Timestamp do início da música
        
        # Estatísticas
        self.hits = 0
        self.goods = 0
        self.misses = 0
        self.bad_hits = 0
        self.score = 0
        
        # Fontes para UI
        self.stats_font = pygame.font.Font(None, 36)
        self.results_title_font = pygame.font.Font(None, 72)
        self.results_font = pygame.font.Font(None, 40)
        self.results_hint_font = pygame.font.Font(None, 32)
        self.legend_font = pygame.font.Font(None, 30)

        # Inicializa posições da lane
        height = self.app.screen.get_height()
        self.lane_bottom = height // 2
        self.lane_top = self.lane_bottom - 200
        self.lane_rect = pygame.Rect(0, self.lane_top, self.app.screen.get_width(), 200)

        # Calcula tempo para a nota chegar à hit_area
        width = self.app.screen.get_width()
        spawn_x = width + self.note_radius
        distance = spawn_x - self.hit_area_x
        self.anticipation_time = distance / self.note_speed  # Em segundos

        # Feedback visual
        self.flash_duration_ms = 180
        self.hit_flash_timer_ms = 0
        self.hit_flash_color = None

        # Estados de término
        self.state = "playing"
        self.end_fade_duration = 2.0
        self.end_fade_elapsed = 0.0
        self.end_overlay_alpha = 0
        self.exit_fade_duration = 2.0
        self.exit_fade_elapsed = 0.0
        self.exit_overlay_alpha = 0
        self.results_visible = False
        self.results_text_alpha = 0
        self.results_recorded = False
        self.results_message = ""

        # Repique visual (feedback do último hit)
        self.repique_target_height = (self.lane_bottom - self.lane_top) + 10
        self.repique_images: dict[str, pygame.Surface] = {}
        self.repique_state = "neutro"
        self.repique_timer = 0.0
        self.repique_anchor_top = 0
        self.repique_anchor_right = 0
        self._load_repique_sprites()
        
        self._load_beatmap()
        self._start_music()

    def _load_beatmap(self) -> None:
        """Carrega timestamps das notas do arquivo CSV"""
        try:
            with open(self.song_data.csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    hit_time = float(row.get('time', 0))  # Tempo quando nota deve estar na hit_area
                    note_type = row.get('note', 'g').lower()
                    
                    if note_type not in ['g', 'a', 'm', 'f']:
                        print(f"Tipo de nota inválido '{note_type}', usando 'g'")
                        note_type = 'g'
                        
                    spawn_time = hit_time
                    
                    if note_type == 'a': self.note_queue.append(Agudo(spawn_time, hit_time))
                    if note_type == 'g': self.note_queue.append(Grave(spawn_time, hit_time))
                    if note_type == 'f': self.note_queue.append(Flam(spawn_time, hit_time))
                    if note_type == 'm': self.note_queue.append(Mao(spawn_time, hit_time))
            
            self.note_queue.sort(key=lambda n: n.spawn_time)
            print(f"Carregadas {len(self.note_queue)} notas do beatmap")
            print(f"Tempo de antecipação: {self.anticipation_time:.2f}s")
            
            # Debug: mostra as 5 primeiras notas
            for i, note in enumerate(self.note_queue[:5]):
                print(f"Nota {i+1}: spawn={note.spawn_time:.2f}s, tipo={note.note_type}")
        
        except Exception as e:
            print(f"Erro ao carregar beatmap: {e}")
            self.note_queue = []

    def _start_music(self) -> None:
        """Inicia a reprodução da música após o tempo de antecipação"""
        try:
            pygame.mixer.music.load(self.song_data.mp3_path)
            pygame.mixer.music.set_volume(0.4)
            
            # Marca o tempo inicial ANTES de tocar
            self.start_time = pygame.time.get_ticks()
            
            # Agenda a música para tocar após o tempo de antecipação
            delay_ms = int(self.anticipation_time * 1000)  # Converte para milissegundos
            pygame.time.set_timer(pygame.USEREVENT + 1, delay_ms, 1)  # Timer único
            
            print(f"Música iniciará em {self.anticipation_time:.2f}s")
        except pygame.error as e:
            print(f"Erro ao carregar música: {e}")

    def spawn_note(self, note: Note) -> None:
        width = self.app.screen.get_width()
        note.x = width + self.note_radius
        note.y = self.lane_bottom - 100
        note.spawned = True
        note.active = (len([n for n in self.notes if getattr(n, "state", None) is None]) == 0)
        note.state = None        # None | 'fading' | 'falling'
        note.result = None       # 'perfect' | 'good' | 'miss'
        note.fade_elapsed = 0.0
        note.fade_total = 0.4    # segundos
        note.alpha = 255
        self.notes.append(note)

    def _activate_next_note(self) -> None:
        candidates = [n for n in self.notes if n.state is None]
        for n in self.notes:
            if n.state is None:
                n.active = False
        if not candidates:
            return
        nxt = min(candidates, key=lambda n: n.hit_time)
        nxt.active = True

    def _trigger_flash(self, color: tuple[int,int,int]) -> None:
        self.hit_flash_color = color
        self.hit_flash_timer_ms = self.flash_duration_ms

    def _start_fade_animation(self, note: Note) -> None:
        note.state = 'fading'
        note.fade_elapsed = 0.0

    def _start_miss_animation(self, note: Note) -> None:
        note.state = 'falling'
        note.fade_elapsed = 0.0
        note.vy = 420   # velocidade queda px/s

    def _load_repique_sprites(self) -> None:
        """Carrega e redimensiona as imagens do repique utilizado como feedback."""
        base_path = Path(__file__).resolve().parents[1] / "assets" / "images"
        lane_height = self.lane_bottom - self.lane_top
        target_height = max(1, self.repique_target_height)

        sprite_map = {
            "neutro": "repique_neutro.png",
            "perfeito": "repique_perfeito.png",
            "bom": "repique_bom.png",
            "erro": "repique_erro.png",
        }

        for state, filename in sprite_map.items():
            path = base_path / filename
            try:
                image = pygame.image.load(str(path)).convert_alpha()
            except pygame.error as exc:  # noqa: BLE001
                print(f"Erro ao carregar sprite '{filename}': {exc}")
                placeholder = pygame.Surface((target_height, target_height), pygame.SRCALPHA)
                placeholder.fill((0, 0, 0, 0))
                self.repique_images[state] = placeholder
                continue

            if image.get_height() <= 0:
                self.repique_images[state] = image
                continue

            scale_ratio = target_height / image.get_height()
            target_width = max(1, int(image.get_width() * scale_ratio))
            scaled = pygame.transform.smoothscale(image, (target_width, target_height))
            self.repique_images[state] = scaled

        if "neutro" not in self.repique_images:
            placeholder = pygame.Surface((target_height, target_height), pygame.SRCALPHA)
            placeholder.fill((0, 0, 0, 0))
            self.repique_images["neutro"] = placeholder

        self.repique_anchor_top = self.lane_top - ((target_height - lane_height) // 2)
        self.repique_anchor_right = self.hit_area_x - self.hit_tolerance - 20

    def _render_repique(self, surface: pygame.Surface) -> None:
        sprite = self.repique_images.get(self.repique_state) or self.repique_images.get("neutro")
        if not sprite:
            return

        # Reposiciona caso a geometria da lane mude (ex: redimensionamento).
        lane_height = self.lane_bottom - self.lane_top
        target_height = max(1, self.repique_target_height)
        self.repique_anchor_top = self.lane_top - ((target_height - lane_height) // 2)
        self.repique_anchor_right = self.hit_area_x - self.hit_tolerance - 20

        rect = sprite.get_rect()
        rect.top = self.repique_anchor_top
        rect.right = self.repique_anchor_right
        surface.blit(sprite, rect)

    def _set_repique_state(self, state: str) -> None:
        new_state = state if state in self.repique_images else "neutro"
        self.repique_state = new_state
        self.repique_timer = 0.0 if new_state == "neutro" else 0.5

    def _update_note_animations(self, dt: float) -> None:
        to_remove = []
        for note in self.notes:
            if note.state in ('fading', 'falling'):
                note.fade_elapsed += dt
                progress = note.fade_elapsed / note.fade_total
                note.alpha = 255 * (1 - progress)
                if note.state == 'falling':
                    note.y += getattr(note, 'vy', 400) * dt
                if progress >= 1.0 or note.alpha <= 0:
                    to_remove.append(note)
        for n in to_remove:
            if n in self.notes:
                self.notes.remove(n)

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        surface.fill(COLOR_YELLOW_BACKGROUND)
        self.render_lane(surface)
        self.render_hit_area(surface)
        self.render_notes(surface)
        self._render_repique(surface)
        self.render_stats(surface)
        self._render_legend(surface)

        overlay_alpha = 0
        if self.state == "ending_fade":
            overlay_alpha = self.end_overlay_alpha
        elif self.state in ("show_results", "leaving"):
            overlay_alpha = 255

        if overlay_alpha > 0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            surface.blit(overlay, (0, 0))

        if self.state == "leaving" and self.exit_overlay_alpha > 0:
            exit_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            exit_overlay.fill((0, 0, 0, self.exit_overlay_alpha))
            surface.blit(exit_overlay, (0, 0))

        if self.results_visible:
            self._render_results(surface)

    def render_lane(self, surface: pygame.Surface) -> None:
        """Desenha a lane em que percorrem as notas"""
        width = surface.get_width()
        self.lane_rect = pygame.Rect(0, self.lane_top, width, 200)

        pygame.draw.rect(surface, COLOR_BACKGROUND, self.lane_rect)
        border_thickness = 2
        pygame.draw.line(surface, (255, 255, 255), (0, self.lane_top), (width - 1, self.lane_top), border_thickness)
        pygame.draw.line(surface, (255, 255, 255), (0, self.lane_bottom - 1), (width - 1, self.lane_bottom - 1), border_thickness)

    def render_hit_area(self, surface: pygame.Surface) -> None:
        """Desenha a área de acerto das notas"""
        hit_center_y = self.lane_bottom - 100
        base = pygame.Surface((self.hit_tolerance * 2, self.hit_tolerance * 2), pygame.SRCALPHA)
        # brilho base
        pygame.draw.circle(base, (255, 255, 255, 40), (self.hit_tolerance, self.hit_tolerance), self.hit_tolerance)
        pygame.draw.circle(base, (255, 255, 255, 160), (self.hit_tolerance, self.hit_tolerance), 2 * self.hit_tolerance // 3)
        surface.blit(base, (self.hit_area_x - self.hit_tolerance, hit_center_y - self.hit_tolerance))

        # flash temporário
        if self.hit_flash_timer_ms > 0 and self.hit_flash_color:
            alpha = int(180 * (self.hit_flash_timer_ms / self.flash_duration_ms))
            flash = pygame.Surface((self.hit_tolerance * 2, self.hit_tolerance * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash, (*self.hit_flash_color, alpha), (self.hit_tolerance, self.hit_tolerance), self.hit_tolerance)
            surface.blit(flash, (self.hit_area_x - self.hit_tolerance, hit_center_y - self.hit_tolerance))
    
    def render_note(self, surface: pygame.Surface, note_center_x: int, note_center_y: int, note: Note) -> None:
        if note.note_type == "g": note_color = COLOR_PINK_NOTE
        elif note.note_type == "a": note_color = COLOR_BLUE_NOTE
        elif note.note_type == "m": note_color = COLOR_YELLOW_NOTE
        else: note_color = COLOR_GREEN_NOTE

        radius = self.note_radius
        note_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        alpha = max(0, min(255, int(note.alpha)))
        pygame.draw.circle(note_surf, (*note_color, alpha), (radius, radius), radius)
        outline_width = max(1, radius // 8)
        pygame.draw.circle(note_surf, (0, 0, 0, alpha), (radius, radius), radius, outline_width)
        surface.blit(note_surf, (note_center_x - radius, note_center_y - radius))

    def render_notes(self, surface: pygame.Surface) -> None:
        """Renderiza todas as notas ativas"""
        for note in self.notes:
            self.render_note(surface, int(note.x), note.y, note)

    def render_stats(self, surface: pygame.Surface) -> None:
        """Renderiza contador de acertos e erros"""
        hits_text = self.stats_font.render(f"Perfeitas: {self.hits}", True, (0, 255, 0))
        goods_text = self.stats_font.render(f"Boas: {self.goods}", True, (0, 0, 255))
        misses_text = self.stats_font.render(f"Erros: {self.misses}", True, (255, 0, 0))
        
        surface.blit(hits_text, (20, 20))
        surface.blit(goods_text, (20, 60))
        surface.blit(misses_text, (20, 100))

    def _render_legend(self, surface: pygame.Surface) -> None:
        entries = [
            ("Z", "Grave", COLOR_PINK_NOTE),
            ("A", "Agudo", COLOR_BLUE_NOTE),
            ("Espaço", "Mão", COLOR_YELLOW_NOTE),
            ("A + Espaço", "Flam", COLOR_GREEN_NOTE),
        ]

        icon_radius = 14
        spacing = 18
        x = 20
        y = self.lane_bottom + 20
        y = min(surface.get_height() - self.legend_font.get_height() - 20, y)

        for key_label, name, color in entries:
            text_surface = self.legend_font.render(f"{key_label} - {name}", True, COLOR_TEXT)
            entry_height = max(icon_radius * 2, text_surface.get_height())
            entry_surface = pygame.Surface((icon_radius * 2 + 10 + text_surface.get_width(), entry_height), pygame.SRCALPHA)

            center_y = entry_height // 2
            pygame.draw.circle(entry_surface, (*color, 255), (icon_radius, center_y), icon_radius)
            pygame.draw.circle(entry_surface, (0, 0, 0, 255), (icon_radius, center_y), icon_radius, max(1, icon_radius // 4))
            entry_surface.blit(text_surface, (icon_radius * 2 + 10, center_y - text_surface.get_height() // 2))

            if x + entry_surface.get_width() > surface.get_width() - 20:
                x = 20
                y += entry_height + spacing
                y = min(surface.get_height() - entry_height - 20, y)

            surface.blit(entry_surface, (x, y))
            x += entry_surface.get_width() + spacing

    def _render_results(self, surface: pygame.Surface) -> None:
        if self.results_text_alpha <= 0:
            return

        width, height = surface.get_size()
        center_x = width // 2
        current_y = int(height * 0.25)

        def _blit_line(font: pygame.font.Font, text: str, color: tuple[int, int, int], gap: int = 16) -> None:
            nonlocal current_y
            rendered = font.render(text, True, color)
            rendered.set_alpha(self.results_text_alpha)
            rect = rendered.get_rect(centerx=center_x, y=current_y)
            surface.blit(rendered, rect)
            current_y = rect.bottom + gap

        _blit_line(self.results_title_font, "Música concluída!", COLOR_PRIMARY, gap=28)
        _blit_line(self.results_font, f"Pontuação: {self.score}", COLOR_TEXT)
        _blit_line(self.results_font, f"Perfeitas: {self.hits}", COLOR_TEXT)
        _blit_line(self.results_font, f"Boas: {self.goods}", COLOR_TEXT)
        _blit_line(self.results_font, f"Erros: {self.misses}", COLOR_TEXT)

        if self.results_message:
            _blit_line(self.results_hint_font, self.results_message, COLOR_PRIMARY, gap=28)

        hint_text = "Pressione Enter para voltar"
        _blit_line(self.results_hint_font, hint_text, COLOR_TEXT_MUTED, gap=0)

    def check_hit(self, note_type: str) -> bool:
        """Verifica acerto apenas na nota marcada como active."""
        # Busca a nota ativa
        active_note = next((n for n in self.notes if n.active and n.state is None), None)
        
        if active_note is None:
            self.misses += 1
            self._trigger_flash(COLOR_MISS)
            self._set_repique_state("erro")
            print(f"MISS! Nenhuma nota ativa para {note_type}")
            return False

        distance = abs(active_note.x - self.hit_area_x)

        # Verifica se está dentro da janela de acerto
        if distance > self.hit_tolerance * 2:
            self._trigger_flash(COLOR_MISS)
            self.misses += 1
            self._set_repique_state("erro")
            print(f"MISS! Nota ativa fora da hit_area")
            return False

        # Verifica o tipo da nota
        if active_note.note_type == note_type:
            perfect_tolerance = 160 // 3

            # Verifica qualidade do acerto
            if distance > perfect_tolerance:
                self.goods += 1
                self.score += 50
                active_note.result = 'good'
                self._trigger_flash(COLOR_GOOD_HIT)
                self._set_repique_state("bom")
                self._start_fade_animation(active_note)
                print(f"GOOD! Tipo: {note_type}")
            else:
                self.hits += 1
                self.score += 100
                active_note.result = 'perfect'
                self._trigger_flash(COLOR_PERFECT_HIT)
                self._set_repique_state("perfeito")
                self._start_fade_animation(active_note)
                print(f"HIT! Tipo: {note_type}")

            # Remove nota atual e ativa a próxima
            self.notes.remove(active_note)
            self._activate_next_note()
            return True
        else:
            active_note.key_mistaken = True # Registra que a nota já teve sua tecla confundida
            self.misses += 1
            self._trigger_flash(COLOR_MISS)
            self._set_repique_state("erro")
            print(f"MISS! Esperava {active_note.note_type}, recebeu {note_type}")
            return False
    
    def _can_trigger(self, key: int) -> bool:
        now = pygame.time.get_ticks()
        last = self.last_key_hit_time.get(key, -10**9)
        if now - last >= self.key_cooldown:
            self.last_key_hit_time[key] = now
            return True
        return False

    def handle_event(self, event: pygame.event.Event) -> None:
        # Timer para iniciar a música
        if event.type == pygame.USEREVENT + 1 and self.state == "playing":
            pygame.mixer.music.play()
            print("Música iniciada!")
            return

        if self.state == "show_results":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self._start_exit_fade()
            return

        if self.state == "leaving" or self.state == "ending_fade":
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancela timer
                self.app.change_scene(MusicSelectScene(self.app))

            keys = pygame.key.get_pressed()

            # Reconhece combinação de teclas
            if keys[pygame.K_a] and keys[pygame.K_SPACE]:
                if self._can_trigger(pygame.K_a) and self._can_trigger(pygame.K_SPACE):
                    Flam.note_sound(self)
                    self.check_hit("f")
                return

            # Teclas individuais
            if event.key == pygame.K_z and self._can_trigger(pygame.K_z):
                Grave.note_sound(self)
                self.check_hit("g")
            elif event.key == pygame.K_a and self._can_trigger(pygame.K_a):
                Agudo.note_sound(self)
                self.check_hit("a")
            elif event.key == pygame.K_SPACE and self._can_trigger(pygame.K_SPACE):
                Mao.note_sound(self)
                self.check_hit("m")

    def update(self, dt: float) -> None:
        """Atualiza posição das notas e gerencia fases da partida."""
        if self.repique_timer > 0:
            self.repique_timer -= dt
            if self.repique_timer <= 0:
                self.repique_timer = 0
                if self.repique_state != "neutro":
                    self.repique_state = "neutro"

        if self.state == "playing":
            if self.start_time is None:
                return

            if self.hit_flash_timer_ms > 0:
                self.hit_flash_timer_ms -= int(dt * 1000)
                if self.hit_flash_timer_ms <= 0:
                    self.hit_flash_timer_ms = 0
                    self.hit_flash_color = None

            current_time = pygame.time.get_ticks()
            music_time = (current_time - self.start_time) / 1000.0

            for note_data in self.note_queue:
                if not note_data.spawned and music_time >= note_data.spawn_time:
                    self.spawn_note(note_data)
                    note_data.spawned = True

            for note in self.notes:
                note.x -= self.note_speed * dt

            notes_to_remove = []
            for note in [n for n in self.notes if n.state is None]:
                if note.x < (self.hit_area_x - self.hit_tolerance):
                    notes_to_remove.append(note)
                    if not note.key_mistaken:
                        self.misses += 1
                        note.result = 'miss'
                        self._trigger_flash(COLOR_MISS)
                        self._set_repique_state("erro")
                        self._start_miss_animation(note)
                        print(f"MISS! Nota passou: {note.note_type}")

            self._update_note_animations(dt)

            for note in notes_to_remove:
                self.notes.remove(note)
                if any(n.active for n in self.notes if n.state is None) is False:
                    self._activate_next_note()

            if self._has_finished_song():
                self._begin_end_sequence()

            return

        if self.state == "ending_fade":
            self._update_end_fade(dt)
        elif self.state == "leaving":
            self._update_exit_fade(dt)
                
    def _has_finished_song(self) -> bool:
        if self.notes:
            return False
        if not self.note_queue:
            return True
        return all(getattr(note, "spawned", False) for note in self.note_queue)

    def _begin_end_sequence(self) -> None:
        if self.state != "playing":
            return
        self.state = "ending_fade"
        self.end_fade_elapsed = 0.0
        self.end_overlay_alpha = 0
        pygame.mixer.music.fadeout(int(self.end_fade_duration * 1000))
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)

    def _update_end_fade(self, dt: float) -> None:
        self.end_fade_elapsed += dt
        progress = min(1.0, self.end_fade_elapsed / self.end_fade_duration)
        self.end_overlay_alpha = int(255 * progress)
        if progress >= 1.0:
            self._transition_to_results()

    def _transition_to_results(self) -> None:
        if self.state == "show_results":
            return
        pygame.mixer.music.stop()
        self.state = "show_results"
        self.end_overlay_alpha = 255
        self.results_visible = True
        self.results_text_alpha = 255
        if not self.results_recorded:
            self._record_play()
            self.results_recorded = True

    def _record_play(self) -> None:
        self.score = self.hits * 100 + self.goods * 50
        player = getattr(self.app, "active_player", None)
        if player is None:
            self.results_message = "Nenhum jogador ativo – resultado não salvo."
            return

        try:
            player_id = int(player["id"])
        except (KeyError, TypeError, ValueError):
            self.results_message = "Jogador inválido – resultado não salvo."
            return

        try:
            play_model = self.app.models.play
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao acessar modelo Play: {exc}")
            self.results_message = "Modelo de partidas indisponível."
            return

        payload = {
            "played_at": datetime.utcnow(),
            "music_name": getattr(self.song_data, "title", "Desconhecida"),
            "score": self.score,
            "player_id": player_id,
            "errors": self.misses,
            "perfect_hits": self.hits,
            "good_hits": self.goods,
            "bad_hits": self.bad_hits,
        }

        try:
            play_model.create(payload)
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao salvar partida: {exc}")
            self.results_message = "Erro ao salvar partida."
        else:
            self.results_message = "Partida registrada com sucesso!"

    def _start_exit_fade(self) -> None:
        if self.state != "show_results":
            return
        self.state = "leaving"
        self.exit_fade_elapsed = 0.0
        self.exit_overlay_alpha = 0
        self.results_text_alpha = 255

    def _update_exit_fade(self, dt: float) -> None:
        self.exit_fade_elapsed += dt
        progress = min(1.0, self.exit_fade_elapsed / self.exit_fade_duration)
        self.exit_overlay_alpha = int(255 * progress)
        self.results_text_alpha = int(255 * (1 - progress))
        if progress >= 1.0:
            self.app.change_scene(MusicSelectScene(self.app))
