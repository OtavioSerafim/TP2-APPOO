from ..Note import Note
import pathlib
import pygame

class Flam(Note):
    def __init__(self, spawn_time: float, hit_time: float):
        super().__init__(spawn_time, hit_time, "f")

    @staticmethod
    def note_sound(self) -> None:
        """Reproduz flam.wav desta pasta."""
        folder = pathlib.Path(__file__).parent
        wav_path = folder / "flam.wav"
        if not wav_path.exists():
            print("flam.note_sound: arquivo flam.wav não encontrado.")
            return
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            sound = pygame.mixer.Sound(str(wav_path))
            sound.play()
        except pygame.error as e:
            print(f"flam.note_sound: erro ao reproduzir flam.wav: {e}")