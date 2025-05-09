import pygame
from PIL import Image
from log import TRACE_LOG

from uicharacterselect import ProgressBoard

from typing import Tuple

from utils import (
    eMenuState,
    eLogLevel,
    DEBUG_MODE,
    file_name_map,
    eFileType,
    base_path,
    eFontType,
    get_font

)
from config import Config

class Menu:
    def __init__(self):
        self._menu_state = eMenuState.MENU_STATE_MAIN
        self.config = Config(file_name_map[eFileType.FILE_CONFIG])
        self.frames = self._load_gif_frames(base_path() + "/assets/bg01.gif")
        self.current_frame = 0
        self.frame_delay = 150
        self.last_frame_time = pygame.time.get_ticks()

        self.screen = None
        self.clock = pygame.time.Clock()

        self.button_images = {}
        self.buttons = {}

        self.hovered_button = None
        self.clicked_button = None

        self.progress_board = None

        self.base_btn_size: Tuple[int, int] = []

        self.resolution_dropdown_active: bool = False
        self.available_resolutions = [(1280, 720), (1600, 900), (1920, 1080)]
        self.resolution_options_rects = []

        self.animate_background = self.config.animated_background

    def load_buttons(self):
        screen_width, screen_height = self.config.resolution

        target_width = (screen_width * 0.5)
        target_height = (screen_height * 0.5)

        def load_states(name):
            return {
                "default": pygame.image.load(base_path() + f"/assets/buttons/{name}_default.png").convert_alpha(),
                "hover": pygame.image.load(base_path() + f"/assets/buttons/{name}_over.png").convert_alpha(),
                "click": pygame.image.load(base_path() + f"/assets/buttons/{name}_click.png").convert_alpha(),
            }

        self.button_images = {
            "play": load_states("play"),
            "options": load_states("options"),
            "exit": load_states("exit"),
            "back": load_states("back"),
            "resolution": load_states("resolution01")
        }

        def center_button(image, y_offset):
            rect = image.get_rect()
            rect.center = (screen_width // 2, y_offset + (screen_height // 3))
            return rect

        self.buttons = {
            eMenuState.MENU_STATE_MAIN: {
                "play": center_button(self.button_images["play"]["default"], 100),
                "options": center_button(self.button_images["options"]["default"], 200),
                "exit": center_button(self.button_images["exit"]["default"], 300),
            },
            eMenuState.MENU_STATE_OPTIONS: {
                "resolution": center_button(self.button_images["resolution"]["default"], screen_height // 5),

                "back": center_button(self.button_images["back"]["default"], 400)
            }
        }

        self.dropdown_images = {
            "default": pygame.image.load(base_path() + "/assets/buttons/drop_down_bar_default.png").convert_alpha(),
            "hover": pygame.image.load(base_path() + "/assets/buttons/drop_down_bar_over.png").convert_alpha(),
            "click": pygame.image.load(base_path() + "/assets/buttons/drop_down_bar_click.png").convert_alpha(),
        }


        self.logo_image = pygame.image.load(base_path() + "/assets/ui/logo.png").convert_alpha()
        self.logo_rect = self.logo_image.get_rect(midtop=(screen_width // 2, 100))

        # settings board
        self.settings_board = pygame.image.load(base_path() + "/assets/ui/transparent_board_03.png").convert_alpha()
        self.settings_board = pygame.transform.scale(self.settings_board, (target_height, target_height))
        self.settings_board_rect = self.settings_board.get_rect(midtop=(screen_width // 2, screen_width // 6))

        # volume bar
        self.volume_bar_empty = pygame.image.load(base_path() + "/assets/buttons/volume_bar_empty.png").convert_alpha()
        self.volume_bar_fill = pygame.image.load(base_path() + "/assets/buttons/volume_bar_fill.png").convert_alpha()
        self.volume_bar_rect = self.volume_bar_empty.get_rect(center=(screen_width // 2, screen_height // 2.5))

        # full_screen btn
        self.fullscreen_on = pygame.image.load(base_path()+ "/assets/buttons/on_btn.png").convert_alpha()
        self.fullscreen_off = pygame.image.load(base_path()+ "/assets/buttons/off_btn.png").convert_alpha()
        self.fullscreen_btn_rect = self.fullscreen_on.get_rect(topleft=(self.volume_bar_rect.right * 0.87, self.volume_bar_rect.bottom))

        # animatated bg btn
        self.animate_bg_btn_on = pygame.image.load(base_path()+ "/assets/buttons/on_btn.png").convert_alpha()
        self.animate_bg_btn_off = pygame.image.load(base_path()+ "/assets/buttons/off_btn.png").convert_alpha()
        self.animate_bg_btn_rect = self.animate_bg_btn_on.get_rect(topleft=(self.volume_bar_rect.right * 0.87, self.fullscreen_btn_rect.bottom * 1.2))

        self.progress_board = ProgressBoard(self.screen.get_width(), self.screen.get_height())

        self.base_btn_size = self.button_images["back"]["default"].get_size()

        # resize resolution btn
        for state in ("default", "hover", "click"):
            drop_down_pre = self.button_images["resolution"][state]
            drop_down_box = self.dropdown_images[state]

#            self.button_images["resolution"][state] = pygame.transform.scale(drop_down_pre, (self.base_btn_size[0] * 1.0, self.base_btn_size[1] * 1.0))
            self.dropdown_images[state] = pygame.transform.scale(drop_down_box, (self.base_btn_size[0] * 0.85, self.base_btn_size[1] * 1.0))

        self.buttons[eMenuState.MENU_STATE_OPTIONS]["resolution"] = self.button_images["resolution"]["default"].get_rect(
            center=self.buttons[eMenuState.MENU_STATE_OPTIONS]["resolution"].center)

    @property
    def menu_state(self) -> eMenuState:
        return self._menu_state

    @menu_state.setter
    def menu_state(self, new_state):
        if isinstance(new_state, int):
            self._menu_state = eMenuState(new_state)
        elif isinstance(new_state, eMenuState):
            self._menu_state = new_state
        else:
            raise ValueError(f"Invalid menu state: {new_state}")

        #fixme002 -> create new input board after its closed, the initial instance is destroyed in build_menu
        if self._menu_state == eMenuState.MENU_STATE_PLAY:
            self.progress_board = ProgressBoard(self.screen.get_width(), self.screen.get_height())

    def build_menu(self):
        pygame.init()

        if not self.screen:
            self.screen = pygame.display.set_mode((self.config.resolution[0], self.config.resolution[1]))
            pygame.display.set_caption("Game Menu")

        self.load_buttons()

        running = True
        while running:
            for event in pygame.event.get():

                if self.menu_state == eMenuState.MENU_STATE_PLAY:
                    result = self.progress_board.handle_event(event)
                    if result == "back":
                        self.progress_board = None
                        self.menu_state = eMenuState.MENU_STATE_MAIN

                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_state == eMenuState.MENU_STATE_OPTIONS:
                        resolution_btn = self.buttons[eMenuState.MENU_STATE_OPTIONS]["resolution"]

                        if self.resolution_dropdown_active and resolution_btn.collidepoint(event.pos):
                            self.resolution_dropdown_active = False

                        elif not self.resolution_dropdown_active and resolution_btn.collidepoint(event.pos):
                            self.resolution_dropdown_active = True
                            self.generate_resolution_rects()

                        elif self.resolution_dropdown_active:
                            for res, rect in self.resolution_options_rects:
                                if rect.collidepoint(event.pos):
                                    self._set_resolution(res)
                                    self.resolution_dropdown_active = False
                                    break

                        if self.volume_bar_rect.collidepoint(event.pos):
                            self._update_volume(event.pos[0])
                        elif self.fullscreen_btn_rect.collidepoint(event.pos):
                            self._toggle_fullscreen()
                        elif self.animate_bg_btn_rect.collidepoint(event.pos):
                            self._toggle_animated_background()

                    for label, rect in self.buttons.get(self.menu_state, {}).items():
                        if rect.collidepoint(event.pos):
                            self.clicked_button = label

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.clicked_button:
                        label = self.clicked_button
                        self.clicked_button = None
                        rect = self.buttons.get(self.menu_state, {}).get(label)
                        if rect and rect.collidepoint(pygame.mouse.get_pos()):
                            self._handle_click(label)

            if self.animate_background:
                now = pygame.time.get_ticks()
                if now - self.last_frame_time > self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
                    self.last_frame_time = now

            self.screen.blit(self.frames[self.current_frame], (0, 0))
            self._draw_buttons()

            pygame.display.flip()
            self.clock.tick(60)

#            if self.menu_state == eMenuState.MENU_STATE_PLAY:
#                running = False

    def _draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()

        self.screen.blit(self.logo_image, self.logo_rect.topleft)

        if self.menu_state == eMenuState.MENU_STATE_PLAY:
            self.progress_board.draw(self.screen)

        elif self.menu_state == eMenuState.MENU_STATE_OPTIONS:
            self.screen.blit(self.settings_board, self.settings_board_rect.topleft)
            self.screen.blit(self.volume_bar_empty, self.volume_bar_rect.topleft)

            # volume bar
            volume = self.config.volume 
            max_width = self.volume_bar_fill.get_width()
            fill_width = int((volume / 100) * max_width)

            fill_surface = self.volume_bar_fill.subsurface((0, 0, fill_width, self.volume_bar_fill.get_height()))
            self.screen.blit(fill_surface, self.volume_bar_rect.topleft)
            # volume bar end

            # volume bar tooltip
            font = get_font(eFontType.FONT_TYPE_UPHEAVAL, 28)
            volume_bar_text = font.render("Volume settings", True, (232, 232, 232))
            self.screen.blit(volume_bar_text, (self.volume_bar_rect.bottomleft[0] * 1.1, self.volume_bar_rect.bottomleft[1] * 0.8))
            # volume bar tooltip end

            # full screen toggle btn
            fullscreen_on = self.config.fullscreen
            btn_image = self.fullscreen_on if fullscreen_on else self.fullscreen_off
            self.screen.blit(btn_image, self.fullscreen_btn_rect.topleft)    
            # full screen toggle btn end

            # full screen toggle tooltip
            full_screen_toggle_text = font.render("Fullscreen mode", True, (232, 232, 232))
            self.screen.blit(full_screen_toggle_text, (self.volume_bar_rect.bottomleft[0] * 1.1, self.fullscreen_btn_rect.topleft[1] * 1.02))
            # full screen toggle tooltip end

            # animate btn toggle btn
            animated_bg_on = self.config.animated_background
            btn_animated = self.animate_bg_btn_on if animated_bg_on else self.animate_bg_btn_off
            self.screen.blit(btn_animated, self.animate_bg_btn_rect.topleft)

            # full screen toggle tooltip
            animated_bg_text = font.render("Animated bg", True, (232, 232, 232))
            self.screen.blit(animated_bg_text, (self.volume_bar_rect.bottomleft[0] * 1.1, self.animate_bg_btn_rect.topleft[1] * 1.02))
            # full screen toggle tooltip end

            # resolution drop down btn
            # resolution drop down btn end

        for label, rect in self.buttons.get(self.menu_state, {}).items():
            if rect.collidepoint(mouse_pos):
                if self.clicked_button == label:
                    state = "click"
                else:
                    state = "hover"
                self.hovered_button = label
            else:
                state = "default"

            image = self.button_images[label][state]
            self.screen.blit(image, rect.topleft)

        if self.resolution_dropdown_active:
            for res, rect in self.resolution_options_rects:
                if rect.collidepoint(mouse_pos):
                    img = self.dropdown_images["hover"]
                else:
                    img = self.dropdown_images["default"]
                self.screen.blit(img, (rect.topleft[0] + 15, rect.topleft[1]))

                label = get_font(eFontType.FONT_TYPE_UPHEAVAL, 24).render(f"{res[0]}x{res[1]}", True, (0, 0, 0))
                label_rect = label.get_rect(center=rect.center)
                self.screen.blit(label, label_rect)


    def _handle_click(self, label: str):
        if self.menu_state == eMenuState.MENU_STATE_MAIN:
            if label == "play":
                self.menu_state = eMenuState.MENU_STATE_PLAY
            elif label == "options":
                self.menu_state = eMenuState.MENU_STATE_OPTIONS
            elif label == "exit":
                pygame.quit()
                exit()
        elif self.menu_state == eMenuState.MENU_STATE_OPTIONS:
            if label == "back":
                self.menu_state = eMenuState.MENU_STATE_MAIN
            elif label == "resolution":
                # handling resolution done above
                pass

    def _load_gif_frames(self, path: str) -> list[pygame.Surface]:
        frames = []
        try:
            gif = Image.open(path)
            while True:
                frame = gif.convert("RGBA")
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                surface = pygame.image.fromstring(data, size, mode)
                frames.append(surface)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        return frames

    def _update_volume(self, mouse_x: int):
        bar_x = self.volume_bar_rect.x
        bar_width = self.volume_bar_fill.get_width()
        rel_x = max(0, min(bar_width, mouse_x - bar_x))
        new_volume = int((rel_x / bar_width) * 100)
        self.config.volume = new_volume
        self.config.save()

    def _toggle_animated_background(self):
        self.config.animated_background = not self.config.animated_background
        self.config.save()
        print(f"[Menu] Animated bg set to: {self.config.animated_background}")

        self.animate_background = True if self.config.animated_background else False

    def _toggle_fullscreen(self):
        self.config.fullscreen = not self.config.fullscreen
        self.config.save()
        if DEBUG_MODE:
            TRACE_LOG(eLogLevel.LOG_LEVEL_LOG, f"[Menu] Fullscreen set to: {self.config.fullscreen}")

        flags = pygame.FULLSCREEN if self.config.fullscreen else 0
        self.screen = pygame.display.set_mode(self.config.resolution, flags)

    def generate_resolution_rects(self):
        base_rect = self.buttons[eMenuState.MENU_STATE_OPTIONS]["resolution"]
        img_width, img_height = self.dropdown_images["default"].get_size()

        for i, res in enumerate(self.available_resolutions):
            rect = pygame.Rect(
                base_rect.left,
                base_rect.bottom + i * img_height,
                img_width,
                img_height
            )
            self.resolution_options_rects.append((res, rect))

    def _set_resolution(self, resolution):
        self.config.resolution = resolution
        self.config.save()
        flags = pygame.FULLSCREEN if self.config.fullscreen else 0
        self.screen = pygame.display.set_mode(resolution, flags)
        self.load_buttons()
