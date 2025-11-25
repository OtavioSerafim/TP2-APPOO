import pygame
import csv

from entities.Notes.Note import Note
from .base import BaseScene
from utils.constants import COLOR_BACKGROUND, COLOR_YELLOW_BACKGROUND, COLOR_PINK_NOTE, COLOR_BLUE_NOTE, COLOR_GREEN_NOTE, COLOR_YELLOW_NOTE, COLOR_PERFECT_HIT, COLOR_GOOD_HIT, COLOR_MISS
from .music_select import MusicSelectScene

class GameplayScene(BaseScene):
    """Cena onde ocorre toda a jogabilidade"""
    def __init__(self, app, song_data: dict):
        self.key_cooldown = 120  # ms entre hits da mesma tecla
        self.last_key_hit_time = {}  # key -> ticks
        self.app = app
        self.song_data = song_data
        self.note_radius = 160 // 3
        self.note_speed = 300
        self.hit_area_x = 300
        self.hit_tolerance = 80  # Raio da hit area
        self.notes = []  # Notas ativas na tela
        self.note_queue = []  # Notas aguardando spawn (do CSV)
        self.start_time = None  # Timestamp do início da música
        
        # Estatísticas
        self.hits = 0
        self.goods = 0
        self.misses = 0
        
        # Fontes para UI
        self.stats_font = pygame.font.Font(None, 36)

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
                    
                    self.note_queue.append(Note(spawn_time, hit_time, note_type))
            
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
            pygame.mixer.music.set_volume(0.5)
            
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
        self.render_stats(surface)

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

    def check_hit(self, note_type: str) -> bool:
        """Verifica acerto apenas na nota marcada como active."""
        # Busca a nota ativa
        active_note = next((n for n in self.notes if n.active and n.state is None), None)
        
        if active_note is None:
            self.misses += 1
            self._trigger_flash(COLOR_MISS)
            print(f"MISS! Nenhuma nota ativa para {note_type}")
            return False

        distance = abs(active_note.x - self.hit_area_x)

        # Verifica se está dentro da janela de acerto
        if distance > self.hit_tolerance:
            self._trigger_flash(COLOR_MISS)
            self.misses += 1
            print(f"MISS! Nota ativa fora da hit_area")
            return False

        # Verifica o tipo da nota
        if active_note.note_type == note_type:
            perfect_tolerance = 160 // 3

            # Verifica qualidade do acerto
            if distance > perfect_tolerance:
                self.goods += 1
                active_note.result = 'good'
                self._trigger_flash(COLOR_GOOD_HIT)
                self._start_fade_animation(active_note)
                print(f"GOOD! Tipo: {note_type}")
                self._activate_next_note()  # Ativa a próxima
            else:
                self.hits += 1
                active_note.result = 'perfect'
                self._trigger_flash(COLOR_PERFECT_HIT)
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
        if event.type == pygame.USEREVENT + 1:
            pygame.mixer.music.play()
            print("Música iniciada!")
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancela timer
                self.app.change_scene(MusicSelectScene(self.app))

            keys = pygame.key.get_pressed()

            # Reconhece combinação de teclas
            if keys[pygame.K_a] and keys[pygame.K_v]:
                if self._can_trigger(pygame.K_a) and self._can_trigger(pygame.K_v):
                    self.check_hit("f")
                return

            # Teclas individuais
            if event.key == pygame.K_z and self._can_trigger(pygame.K_z): self.check_hit("g")
            elif event.key == pygame.K_a and self._can_trigger(pygame.K_a): self.check_hit("a")
            elif event.key == pygame.K_v and self._can_trigger(pygame.K_v): self.check_hit("m")

    def update(self, dt: float) -> None:
        """Atualiza posição das notas e spawna baseado no timer real"""
        if self.start_time is None:
            return
        
        # Atualiza flash
        if self.hit_flash_timer_ms > 0:
            self.hit_flash_timer_ms -= int(dt * 1000)
            if self.hit_flash_timer_ms <= 0:
                self.hit_flash_timer_ms = 0
                self.hit_flash_color = None
        
        # Calcula tempo decorrido usando pygame.time.get_ticks()
        current_time = pygame.time.get_ticks()
        music_time = (current_time - self.start_time) / 1000.0  # Converte ms para segundos
        
        # Spawna notas do beatmap no momento certo
        for note_data in self.note_queue:
            if not note_data.spawned and music_time >= note_data.spawn_time:
                self.spawn_note(note_data)  # Passa o objeto da nota
                note_data.spawned = True
        
        # Move todas as notas
        for note in self.notes:
            note.x -= self.note_speed * dt
        
        # Verifica notas que passaram da hit area (erros)
        notes_to_remove = []
        for note in [n for n in self.notes if n.state is None]:
            if note.x < (self.hit_area_x - self.hit_tolerance):
                notes_to_remove.append(note)
                if not note.key_mistaken:
                    self.misses += 1
                    note.result = 'miss'
                    self._trigger_flash(COLOR_MISS)
                    self._start_miss_animation(note)
                    print(f"MISS! Nota passou: {note.note_type}")
        
        # Atualiza animações
        self._update_note_animations(dt)

        # Remove notas perdidas
        for note in notes_to_remove:
            self.notes.remove(note)
            if any(n.active for n in self.notes if n.state is None) is False:
                self._activate_next_note()
                