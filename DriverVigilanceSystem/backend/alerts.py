# """
# alerts.py
# Plays audio alerts using Pygame's mixer based on the driver's current state.

# Audio files expected in ../audio/:
#     wake_up.wav      -> played when driver is drowsy (eyes closed / EAR low)
#     look_ahead.wav   -> played when driver is distracted (head turned away)
#     phone_alert.wav  -> played when a phone is detected
#     take_rest.wav    -> played when risk score is critically high for a while
# """

# import os
# import time
# import pygame

# AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")

# ALERT_FILES = {
#     "drowsy": "wake_up.wav",
#     "distracted": "look_ahead.wav",
#     "phone": "phone_alert.wav",
#     "critical": "take_rest.wav",
# }

# # Minimum seconds between repeated alerts of the same type (avoid spamming)
# COOLDOWN_SECONDS = 4.0


# class AlertManager:
#     def __init__(self, audio_dir: str = AUDIO_DIR):
#         pygame.mixer.init()
#         self.audio_dir = audio_dir
#         self._last_played = {}
#         self._sounds = {}
#         self._load_sounds()

#     def _load_sounds(self):
#         for key, filename in ALERT_FILES.items():
#             path = os.path.join(self.audio_dir, filename)
#             if os.path.exists(path):
#                 try:
#                     self._sounds[key] = pygame.mixer.Sound(path)
#                 except Exception as e:
#                     print(f"[alerts] Could not load {path}: {e}")
#             else:
#                 print(f"[alerts] Warning: audio file missing -> {path}")

#     def play(self, alert_type: str):
#         """Play an alert sound, respecting a per-type cooldown."""
#         if alert_type not in self._sounds:
#             return False

#         now = time.time()
#         last = self._last_played.get(alert_type, 0)
#         if now - last < COOLDOWN_SECONDS:
#             return False  # still in cooldown

#         self._sounds[alert_type].play()
#         self._last_played[alert_type] = now
#         return True

#     def stop_all(self):
#         pygame.mixer.stop()


# # Singleton-style accessor so app.py can reuse a single AlertManager
# _alert_manager_instance = None


# def get_alert_manager():
#     global _alert_manager_instance
#     if _alert_manager_instance is None:
#         _alert_manager_instance = AlertManager()
#     return _alert_manager_instance


# if __name__ == "__main__":
#     manager = AlertManager()
#     print("Loaded sounds:", list(manager._sounds.keys()))
#     manager.play("drowsy")
#     time.sleep(2)

"""
alerts.py
Plays audio alerts using Pygame's mixer based on the driver's current state.

Audio files expected in ../audio/:
    wake_up.wav      -> played when driver is drowsy (eyes closed / EAR low)
    look_ahead.wav   -> played when driver is distracted (head turned away)
    phone_alert.wav  -> played when a phone is detected
    take_rest.wav    -> played when risk score is critically high for a while
"""

import os
import time
import pygame

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")

ALERT_FILES = {
    "drowsy": "wake_up.wav",
    "distracted": "look_ahead.wav",
    "phone": "phone_alert.wav",
    "critical": "take_rest.wav",
}

# Minimum seconds between repeated alerts of the same type (avoid spamming)
COOLDOWN_SECONDS = 4.0


class AlertManager:
    def __init__(self, audio_dir: str = AUDIO_DIR):
        pygame.mixer.init()
        self.audio_dir = audio_dir
        self._last_played = {}
        self._sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        for key, filename in ALERT_FILES.items():
            path = os.path.join(self.audio_dir, filename)
            if os.path.exists(path):
                try:
                    self._sounds[key] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"[alerts] Could not load {path}: {e}")
            else:
                print(f"[alerts] Warning: audio file missing -> {path}")

    def play(self, alert_type: str):
        """Play an alert sound, respecting a per-type cooldown."""
        if alert_type not in self._sounds:
            return False

        now = time.time()
        last = self._last_played.get(alert_type, 0)
        if now - last < COOLDOWN_SECONDS:
            return False  # still in cooldown

        self._sounds[alert_type].play()
        self._last_played[alert_type] = now
        return True

    def stop_all(self):
        pygame.mixer.stop()


# Singleton-style accessor so app.py can reuse a single AlertManager
_alert_manager_instance = None


def get_alert_manager():
    global _alert_manager_instance
    if _alert_manager_instance is None:
        _alert_manager_instance = AlertManager()
    return _alert_manager_instance


if __name__ == "__main__":
    manager = AlertManager()
    print("Loaded sounds:", list(manager._sounds.keys()))
    manager.play("drowsy")
    time.sleep(2)