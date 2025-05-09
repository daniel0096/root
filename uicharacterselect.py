import pygame
from typing import Union
from utils import base_path, get_font, eFontType, MAX_LEVEL, MAX_NAME_LEN

class InputBoard:
    def __init__(self, width: int, height: int, text: str = "Choose Your Name"):
        self.width = width
        self.height = height
        self.text = text
        self._name = ""
        self.active = False

        self.font = get_font(eFontType.FONT_TYPE_UPHEAVAL, 44)
        self.dialog = pygame.image.load(base_path() + "/assets/ui/input_name_dialog_gray.png").convert_alpha()
        self.dialog_rect = self.dialog.get_rect(center=(width // 2, height // 2))

        self.input = pygame.image.load(base_path() + "/assets/ui/bar_gray.png").convert_alpha()
#        self.input_rect = pygame.Rect(self.dialog_rect.centerx - 100, self.dialog_rect.centery - 10, 200, 40)


        self.input_rect = self.input.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.centery - 10))

        self.button_images = {}
        self.buttons = {}
        self.clicked_button = None
        self.hovered_button = None

        self.load_buttons()

    def load_buttons(self):
        def load_states(name):
            return {
                "default": pygame.image.load(base_path() + f"/assets/buttons/{name}_default.png").convert_alpha(),
                "hover": pygame.image.load(base_path() + f"/assets/buttons/{name}_over.png").convert_alpha(),
                "click": pygame.image.load(base_path() + f"/assets/buttons/{name}_click.png").convert_alpha(),
            }

        self.button_images = {
            "accept": load_states("accept"),
            "cancel": load_states("cancel"),
        }

        self.buttons = {
            "accept": self.button_images["accept"]["default"].get_rect(topleft=(self.input_rect.left, self.input_rect.bottom + 20)),
            "cancel": self.button_images["cancel"]["default"].get_rect(topleft=(self.input_rect.right - self.button_images["cancel"]["default"].get_width(), self.input_rect.bottom + 20)),
        }

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "accept"
            elif event.key == pygame.K_BACKSPACE:
                self._name = self._name[:-1]
            else:
                if len(self._name) >= 12:
                    return "input is too long"
                else:
                    self._name += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.clicked_button = key

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked_button:
                key = self.clicked_button
                rect = self.buttons.get(key)
                if rect and rect.collidepoint(pygame.mouse.get_pos()):
                    self.clicked_button = None
                    return key
            self.clicked_button = None
    
        return None

    def draw(self, screen):
        screen.blit(self.dialog, self.dialog_rect.topleft)
        screen.blit(self.input, self.input_rect.topleft)

        # Vstupní pole
        txt_surface = self.font.render(self._name, True, (0, 0, 0))
        screen.blit(txt_surface, (self.input_rect.x + 10, self.input_rect.y + 5))

        mouse_pos = pygame.mouse.get_pos()
        for key, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                state = "click" if self.clicked_button == key else "hover"
            else:
                state = "default"

            screen.blit(self.button_images[key][state], rect.topleft)

class ProgressBoard:
    def __init__(self, width: int, height: int, character_name: str = "NONAME", character_level: int = MAX_LEVEL):
        self.width = width
        self.height = height

        self.__character_name = character_name
        self.__character_level = character_level

        self.font = get_font(eFontType.FONT_TYPE_UPHEAVAL, 60)
        self.small_font = get_font(eFontType.FONT_TYPE_UPHEAVAL, 24)

        self.input_board = InputBoard(self.width, self.height, "Choose your name")

        self.board_images = {
            "progress_board": pygame.image.load(base_path() + "/assets/ui/loads/select_progress_board.png").convert_alpha(),
            "progress_frame": pygame.image.load(base_path() + "/assets/ui/loads/progress_frame_empty.png").convert_alpha(),
            "level_bar": pygame.image.load(base_path() + "/assets/ui/loads/level_bar.png").convert_alpha(),
            "avatar": pygame.image.load(base_path() + "/assets/ui/loads/avatar.png").convert_alpha(),
        }

        def load_states(name):
            return {
                "default": pygame.image.load(base_path() + f"/assets/ui/loads/{name}_default.png").convert_alpha(),
                "hover": pygame.image.load(base_path() + f"/assets/ui/loads/{name}_over.png").convert_alpha(),
                "click": pygame.image.load(base_path() + f"/assets/ui/loads/{name}_click.png").convert_alpha(),
            }

        self.button_images = {
            "play": load_states("play"),
            "delete": load_states("delete"),
            "back": load_states("back")
        }

        self.is_empty_slot = True

        self.buttons = {}
        self.clicked_button = None
        self.hovered_button = None

        self.progress_slots = []
        self.progress_board_rect = None

        self.generate_progress_rects()
        self._init_back_button()

    def generate_progress_rects(self):
        board_rect = self.board_images["progress_board"].get_rect(center=(self.width // 2, self.height // 2))
        frame_size = self.board_images["progress_frame"].get_size()
        avatar_size = self.board_images["avatar"].get_size()
        level_bar_size = self.board_images["level_bar"].get_size()
        btn_size = self.button_images["play"]["default"].get_size()

        self.progress_slots.clear()
        spacing = 30
        start_y = board_rect.top + 40
        slot_height = frame_size[1]

        for i in range(3):
            top = start_y + i * (slot_height + spacing)
            frame_rect = pygame.Rect(board_rect.left + 55, top, *frame_size)
            avatar_rect = pygame.Rect(frame_rect.left + 35, frame_rect.top + 35, *avatar_size)

            level_rect = pygame.Rect(0, 0, *level_bar_size)
            level_rect.centerx = frame_rect.centerx
            level_rect.top = avatar_rect.centery - 20

            name_center = (level_rect.centerx, level_rect.top - 30)

            play_rect = pygame.Rect(
                frame_rect.right - btn_size[0] - 72,
                frame_rect.top + 40,
                *btn_size
            )

            delete_rect = pygame.Rect(
                frame_rect.right - btn_size[0] - 72,
                play_rect.bottom + 15,
                *btn_size
            )

            self.progress_slots.append({
                "frame": frame_rect,
                "avatar": avatar_rect,
                "name_center": name_center,
                "level_bar": level_rect,
                "play": play_rect,
                "delete": delete_rect
            })

        self.progress_board_rect = board_rect

    def _init_back_button(self):
        back_img = self.button_images["back"]["default"]
        self.buttons["back"] = back_img.get_rect(midbottom=(self.width // 2, self.progress_board_rect.bottom - 40))

    def draw(self, screen):
        screen.blit(self.board_images["progress_board"], self.progress_board_rect.topleft)
        mouse_pos = pygame.mouse.get_pos()


        for i, slot in enumerate(self.progress_slots):
            screen.blit(self.board_images["progress_frame"], slot["frame"])
            screen.blit(self.board_images["avatar"], slot["avatar"])
            screen.blit(self.board_images["level_bar"], slot["level_bar"])

            name_surface = self.font.render(self.__character_name, True, (232, 232, 232))
            name_rect = name_surface.get_rect(center=slot["name_center"])
            screen.blit(name_surface, name_rect)

            level_text = self.small_font.render(f"LEVEL {self.__character_level}", True, (232, 232, 232))
            level_text_rect = level_text.get_rect(center=slot["level_bar"].center)
            screen.blit(level_text, level_text_rect)

            for key in ("play", "delete"):
                rect = slot[key]
                if self.clicked_button == f"{key}_{i}" and rect.collidepoint(mouse_pos):
                    state = "click"
                elif rect.collidepoint(mouse_pos):
                    state = "hover"
                else:
                    state = "default"
                screen.blit(self.button_images[key][state], rect.topleft)

        if self.input_board.active:
            self.input_board.draw(screen)

        back_rect = self.buttons["back"]
        back_state = "hover" if back_rect.collidepoint(mouse_pos) else "default"
        screen.blit(self.button_images["back"][back_state], back_rect.topleft)

    def handle_event(self, event):
        if self.input_board.active:
            result = self.input_board.handle_event(event)
            if result == "accept":
                print("Accepted:", self.input_board._name)
                self.input_board.active = False
#                self.is_empty_slot = False  # change slot to empty
            elif result == "cancel":
                self.input_board.active = False
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["back"].collidepoint(event.pos):
                self.clicked_button = "back"

            for i, slot in enumerate(self.progress_slots):
                for action in ("play", "delete"):
                    if slot[action].collidepoint(event.pos):
                        self.clicked_button = f"{action}_{i}"

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked_button:
                if self.clicked_button == "back" and self.buttons["back"].collidepoint(pygame.mouse.get_pos()):
                    self.clicked_button = None
                    return "back"

                for i, slot in enumerate(self.progress_slots):
                    for action in ("play", "delete"):
                        if self.clicked_button == f"{action}_{i}" and slot[action].collidepoint(pygame.mouse.get_pos()):
                            if action == "play":
                                self._click_play_button()
                            # delete logic
                            self.clicked_button = None
                            return f"{action}_{i}"

            self.clicked_button = None

        return None

    def _click_play_button(self):
        if self.is_empty_slot:
            self.input_board.active = True
        else:
            print("Start game!")