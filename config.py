from typing import Dict, Optional, List, Tuple
from log import TRACE_LOG
from utils import eLogLevel, eDirType
import os
from file_manager import FileManager

class Config:
    """
    Configuration parser for key=value pairs from config.cfg.
    """

    def __init__(self, config_name: str, config_path: Optional[str] = "../config"):
        self._config_settings: Dict[str, List[str]] = {}
        self._config_name: str = config_name
        self._config_path: str = config_path

        fileMgr = FileManager()
        fileMgr.set_working_path(eDirType.DIR_TYPE_CONFIG)
        fileMgr.create_file(config_name)

        self._load_config()
        self._apply_defaults()


    def _apply_defaults(self):
        """
        Ensures required config keys exist and are valid.
        Adds default values for missing or invalid entries.
        """

        res = self._config_settings.get("resolution")
        vol = self._config_settings.get("volume")
        f_screen = self._config_settings.get("fullscreen")
        animated_bg = self._config_settings.get("animated_background")

        if not res or len(res) != 2 or not all(r.isdigit() for r in res):
            self.resolution = (1080, 768)
            TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, f"[Config] Setting default resolution: {self.resolution[0]}x{self.resolution[1]}")

        if not vol or len(vol) != 1 or not vol[0].isdigit():
            self.volume = 100
            TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, f"[Config] Setting default volume: {self.volume}")

        if not f_screen or len(f_screen) != 1 or f_screen[0].lower() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
            self.fullscreen = False
            TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, f"[Config] Setting default fullscreen: {self.fullscreen}")

        if not animated_bg or len(animated_bg) != 1 or animated_bg[0].lower() not in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
            self.animated_bg = True
            TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, f"[Config] Setting default animated_background: {self.animated_bg}")

        self.save()

    @property
    def resolution(self) -> Optional[Tuple[int, int]]:
        """
        Returns the resolution setting as a list of strings.

        Example: ["1920", "1080"]
        """
        if self._config_settings and "resolution" in self._config_settings:
            return self._config_settings["resolution"]
        return None

    def _load_config(self) -> bool:
        """
        Loads the config file and parses its contents into a dictionary.
        """

        full_path = os.path.join(self._config_path, self._config_name)

        try:
            with open(full_path, "r", encoding="utf-8") as fp:

                for line in fp:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    if '=' in line:
                        key, value = line.split('=', 1)
                        self._config_settings[key.strip()] = [
                            v.strip() for v in value.split(",")
                        ]
            return True

        except FileNotFoundError:
            TRACE_LOG(eLogLevel.LOG_LEVEL_ERROR, f"[Config] File not found: {full_path}")

        except Exception as err:
            TRACE_LOG(eLogLevel.LOG_LEVEL_ERROR, f"[Config] Failed to load: {err}")
        return False

    @property
    def resolution(self) -> Optional[Tuple[int, int]]:
        """
        Returns the resolution as a tuple of integers (e.g. 1920, 1080).
        """
        values = self._config_settings.get("resolution")
        if values and len(values) == 2:
            try:
                return int(values[0]), int(values[1])
            except ValueError:
                TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, "[Config] Invalid resolution values.")
        return None

    @property
    def fullscreen(self) -> bool:
        """
        Returns whether fullscreen is enabled.
        """
        val = self._config_settings.get("fullscreen", ["false"])[0].lower()
        return val in {"true", "1", "yes", "on"}

    @property
    def animated_background(self) -> bool:
        """
        Returns whether animated_background is enabled.
        """
        val = self._config_settings.get("animated_background", ["false"])[0].lower()
        return val in {"true", "1", "yes", "on"}

    @property
    def volume(self) -> int:
        """
        Returns the volume level (0–100), defaults to 100.
        """
        val = self._config_settings.get("volume", ["100"])[0]
        try:
            return max(0, min(100, int(val)))
        except ValueError:
            TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, "[Config] Invalid volume value.")
            return 100

    def set(self, key: str, values: List[str]) -> None:
        """
        Updates a key in the config dictionary.

        Args:
            key (str): The config key to update.
            values (List[str]): List of string values to store.
        """
        self._config_settings[key] = values

    def save(self) -> bool:
        """
        Writes current config back to the config file.

        Returns:
            bool: True if saved successfully.
        """
        full_path = os.path.join(self._config_path, self._config_name)

        try:
            with open(full_path, "w", encoding="utf-8") as fp:
                for key, values in self._config_settings.items():
                    fp.write(f"{key} = {','.join(values)}\n")
            TRACE_LOG(eLogLevel.LOG_LEVEL_LOG, f"[Config] Saved: {full_path}")
            return True
        except Exception as e:
            TRACE_LOG(eLogLevel.LOG_LEVEL_ERROR, f"[Config] Failed to save: {e}")
            return False

    @resolution.setter
    def resolution(self, res: Tuple[int, int]):
        """
        Sets new resolution.

        Args:
            res (Tuple[int, int]): (width, height)
        """
        self.set("resolution", [str(res[0]), str(res[1])])

    @fullscreen.setter
    def fullscreen(self, enabled: bool):
        self.set("fullscreen", ["true" if enabled else "false"])

    @animated_background.setter
    def animated_background(self, enabled: bool):
        self.set("animated_background", ["true" if enabled else "false"])

    @volume.setter
    def volume(self, level: int):
        self.set("volume", [str(max(0, min(100, level)))])