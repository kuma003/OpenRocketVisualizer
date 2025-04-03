"""Scene module for the OpenRocket visualizer application."""

import abc
import enum
from pathlib import Path

import numpy as np
import pygame as pg

import visualizer.config as cfg
import visualizer.ui_elements as ui_elements
from visualizer.dialogs import ask_whether_to_exit, open_ork_file
from visualizer.fonts import Fonts
from visualizer.rocket import *

pg.init()


class SCENE_STATE(enum.Enum):
    """
    Enum class for scene state.
    """

    TOP = 0
    BRIEFING = 1
    GAME = 2
    EXIT = 3
    QUIT = 4


class Scene(abc.ABC):
    """
    Base class for all scenes. All scenes should inherit from this class.
    """

    def __init__(self) -> None:
        """
        Initialize the scene with default values.
        """
        # Common elements for all scenes
        self.state = (
            SCENE_STATE.TOP
        )  # Default state (to be overridden by derived classes)

    @abc.abstractmethod
    def handle_event(self, event) -> SCENE_STATE:
        """
        Process events for the scene.

        Args:
            event: Pygame event to process

        Returns:
            SCENE_STATE: New scene state if transition is needed, None otherwise
        """
        # Common event handling
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if ask_whether_to_exit():
                    return SCENE_STATE.EXIT
        return None

    @abc.abstractmethod
    def update(self) -> None:
        """
        Update the scene state. Must be implemented by derived classes.
        """
        pass

    @abc.abstractmethod
    def draw(self, screen: pg.Surface) -> None:
        """
        Draw the scene elements to the screen.

        Args:
            screen: Pygame surface to draw on
        """
        pass

    def exec(self, screen: pg.Surface) -> SCENE_STATE:
        """
        Execute the scene logic, updating and drawing.

        Args:
            screen: Pygame surface to draw on

        Returns:
            SCENE_STATE: Current scene state
        """
        # Clear the screen
        screen.fill(cfg.COLOR_PALE_WHITE1)

        # Update state
        self.update()

        # Draw elements
        self.draw(screen)

        # Update display
        pg.display.update()

        return self.state


class AppMain:
    def __init__(self) -> None:
        """
        Initialize the main application.
        """
        info = pg.display.Info()
        screen_width, screen_height = info.current_w, info.current_h

        # Initial window size with 16:9 aspect ratio
        self.base_width = screen_width // 2
        self.base_height = int(self.base_width * 9 / 16)

        # Set window to be resizable
        self.screen = pg.display.set_mode(
            (self.base_width, self.base_height), pg.RESIZABLE
        )
        pg.display.set_caption("F.T.E. OpenRocket Visualizer")
        pg.display.set_icon(pg.image.load("img/ろけにゃん_ロケット.png"))

        # Set initial scene
        self.scene = TopScene()
        self.current_state = SCENE_STATE.TOP

    def adjust_window_size(self, width, height):
        """
        Adjust window size while maintaining 16:9 aspect ratio.

        Args:
            width: Requested window width
            height: Requested window height

        Returns:
            tuple: New width and height values that maintain 16:9 aspect ratio
        """
        target_ratio = 16 / 9
        current_ratio = width / height

        if current_ratio > target_ratio:
            # If too wide, adjust width based on height
            new_width = int(height * target_ratio)
            new_height = height
        else:
            # If too tall, adjust height based on width
            new_width = width
            new_height = int(width / target_ratio)

        self.screen = pg.display.set_mode((new_width, new_height), pg.RESIZABLE)
        return new_width, new_height

    def handle_common_events(self):
        """
        Process events common to all scenes.

        Returns:
            SCENE_STATE: New scene state if transition is needed, None otherwise
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if ask_whether_to_exit():
                    return SCENE_STATE.EXIT
            elif event.type == pg.VIDEORESIZE:
                # Maintain aspect ratio when window is resized
                self.adjust_window_size(event.w, event.h)

            # Pass event to current scene for scene-specific handling
            result = self.scene.handle_event(event)
            if result:
                return result

        return None

    def switch_scene(self, new_state):
        """
        Switch to a new scene based on the state.

        Args:
            new_state: SCENE_STATE enum value indicating the scene to switch to
        """
        if new_state == self.current_state:
            return

        # Store old scene for data transfer if needed
        old_scene = self.scene

        # Create new scene based on state
        if new_state == SCENE_STATE.TOP:
            self.scene = TopScene()
        elif new_state == SCENE_STATE.BRIEFING:
            # When transitioning to Briefing, get ork file from previous scene
            if isinstance(old_scene, TopScene) and hasattr(old_scene, "ork_file"):
                self.scene = BriefingScene(old_scene.ork_file)
            else:
                self.scene = BriefingScene()
        elif new_state == SCENE_STATE.GAME:
            self.scene = GameScene()

        self.current_state = new_state

    def run(self) -> None:
        """
        Run the main application loop.
        """
        clock = pg.time.Clock()
        fps = 60

        while True:
            clock.tick(fps)

            # Process common events
            result = self.handle_common_events()
            if result:
                if result == SCENE_STATE.EXIT or result == SCENE_STATE.QUIT:
                    break
                # Handle scene transition
                self.switch_scene(result)

            # Execute current scene
            new_state = self.scene.exec(self.screen)
            if new_state != self.current_state:
                # Handle scene transition requested by scene
                self.switch_scene(new_state)

        pg.quit()


class TopScene(Scene):
    """
    Initial scene of the application.
    """

    def __init__(self) -> None:
        """
        Initialize the top scene.
        """
        super().__init__()
        self.state = SCENE_STATE.TOP
        self.ork_file: Path = Path("")

        self.FTE_icon = ui_elements.BackgruondLogo()
        self.settings_button = ui_elements.Button(
            ui_elements.load_transparent_img("img/settings.png", cfg.COLOR_GRAY1),
            (0, 0),
            4,
        )
        self.settings_button.set_callback(lambda: self.set_ork_file())

        self.oepn_file_text = ui_elements.UI_Text(
            "  orkファイルを開く | Open ork File  ",
            "r_Mplus_medium",
            3.75,
            cfg.COLOR_BLACK,
            (50, 75),
            True,
            underline=True,
        )
        self.oepn_file_text.set_callback(lambda: self.set_ork_file())
        self.title = ui_elements.UI_Text(
            "From The Earth\nOpenRocket Visualizer",
            "oswald",
            7.5,
            cfg.COLOR_BLACK,
            (50, 20),
            True,
            0.85,
        )

        self.copyright = ui_elements.UI_Text(
            cfg.TEXT_COPYRIGHT, "oswald", 1.25, cfg.COLOR_GRAY1, (87.5, 97)
        )

    def set_ork_file(self):
        """
        Open an ORK file dialog and set the file path.
        """
        self.ork_file = Path(open_ork_file())
        if self.ork_file.exists() and self.ork_file.suffix == ".ork":
            print(f"Open file: {self.ork_file}")
            self.state = SCENE_STATE.BRIEFING  # next scene

    def handle_event(self, event) -> SCENE_STATE:
        """
        Process events for the top scene.

        Args:
            event: Pygame event to process

        Returns:
            SCENE_STATE: New scene state if transition is needed, None otherwise
        """
        result = super().handle_event(event)
        if result:
            return result

        if hasattr(self.settings_button, "event_handler"):
            self.settings_button.event_handler(event=event)
        if hasattr(self.oepn_file_text, "event_handler"):
            self.oepn_file_text.event_handler(event)
        return None

    def update(self) -> None:
        """
        Update the scene elements.
        """
        self.FTE_icon.update()
        self.settings_button.update()
        self.title.update()
        self.oepn_file_text.update()
        self.copyright.update()

    def draw(self, screen: pg.Surface) -> None:
        """
        Draw the scene elements.

        Args:
            screen: Pygame surface to draw on
        """
        self.FTE_icon.draw(screen)
        self.settings_button.draw(screen)
        self.oepn_file_text.draw(screen)
        self.title.draw(screen)
        self.copyright.draw(screen)


class BriefingScene(Scene):
    """
    Briefing scene that displays rocket information.
    """

    def __init__(self, ork_file: Path = None) -> None:
        """
        Initialize the briefing scene.

        Args:
            ork_file: Path to ORK file, or None if not available
        """
        super().__init__()
        self.state = SCENE_STATE.BRIEFING

        if ork_file and ork_file.exists() and ork_file.suffix == ".ork":
            self.run_simulation(ork_file)
        else:
            # Initialize with defaults if ork_file is invalid
            self.rocket = None
            self.specification = None
            self.spec_detail = None
            self.flight_profile = None
            self.flight_profile_detail = None
            self.FTE_icon = ui_elements.BackgruondLogo()
            self.copyright = ui_elements.UI_Text(
                cfg.TEXT_COPYRIGHT, "oswald", 1.25, cfg.COLOR_GRAY1, (87.5, 97)
            )
            self.back_icon = ui_elements.Button(
                ui_elements.load_transparent_img("img/back.png", cfg.COLOR_GRAY1),
                (0, 0),
                4,
            )
            self.back_icon.set_callback(lambda: self.back_to_top())
            self.back_icon_text = ui_elements.UI_Text(
                "戻る | Back", "r_Mplus_regular", 3, cfg.COLOR_GRAY1, (4, 0)
            )
            self.back_icon_text.set_callback(lambda: self.back_to_top())

    def run_simulation(self, ork_file: os.PathLike):
        """
        Load the ORK file data and run simulation.

        Args:
            ork_file: Path to the ORK file
        """
        self.rocket = Rocket(ork_file)
        self.rocket.run_simulation()
        self.rocket.drawing_size = 0.75
        self.specification = ui_elements.UI_Text(
            " 諸元 | Specification                          ",
            "r_Mplus_medium",
            3.75,
            cfg.COLOR_BLACK,
            (40, 7.5),
            underline=True,
        )
        spec_detail_text = f"""
全長 | Length:  {self.rocket.length*100:.1f} cm
直径 | Diameter:  {self.rocket.radius*2000:.1f} cm
重量 | Weight:  {self.rocket.dry_mass*1000:.2f} g
"""
        self.spec_detail = ui_elements.UI_Text(
            spec_detail_text,
            "r_Mplus_regular",
            3.5,
            cfg.COLOR_BLACK,
            (42.5, 10),
        )

        self.flight_profile = ui_elements.UI_Text(
            " 飛行プロファイル | Flight Profile        ",
            "r_Mplus_medium",
            3.75,
            cfg.COLOR_BLACK,
            (40, 50),
            underline=True,
        )
        flight_profile_text = f"""
飛行時間 | Flight Time:  {self.rocket.flight_time:.1f} s
最高高度 | Max Altitude:  {self.rocket.max_altitude:.1f} m
最高速度 | Max Velocity:  {self.rocket.max_velocity:.1f} m/s
"""
        self.flight_profile_detail = ui_elements.UI_Text(
            flight_profile_text,
            "r_Mplus_regular",
            3.5,
            cfg.COLOR_BLACK,
            (42.5, 52.5),
        )

        self.FTE_icon = ui_elements.BackgruondLogo()
        self.copyright = ui_elements.UI_Text(
            cfg.TEXT_COPYRIGHT, "oswald", 1.25, cfg.COLOR_GRAY1, (87.5, 97)
        )

        self.back_icon = ui_elements.Button(
            ui_elements.load_transparent_img("img/back.png", cfg.COLOR_GRAY1),
            (0, 0),
            4,
        )
        self.back_icon.set_callback(lambda: self.back_to_top())

        self.back_icon_text = ui_elements.UI_Text(
            "戻る | Back", "r_Mplus_regular", 3, cfg.COLOR_GRAY1, (4, 0)
        )
        self.back_icon_text.set_callback(lambda: self.back_to_top())

    def back_to_top(self):
        """
        Return to the top scene.
        """
        self.state = SCENE_STATE.TOP

    def handle_event(self, event) -> SCENE_STATE:
        """
        Process events for the briefing scene.

        Args:
            event: Pygame event to process

        Returns:
            SCENE_STATE: New scene state if transition is needed, None otherwise
        """
        result = super().handle_event(event)
        if result:
            return result

        if hasattr(self.back_icon, "event_handler"):
            self.back_icon.event_handler(event)
        if hasattr(self.back_icon_text, "event_handler"):
            self.back_icon_text.event_handler(event)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                return SCENE_STATE.TOP
            if event.key == pg.K_RETURN:
                return SCENE_STATE.GAME
        return None

    def update(self) -> None:
        """
        Update the briefing scene elements.
        """
        self.FTE_icon.update()
        self.copyright.update()
        self.back_icon.update()
        self.back_icon_text.update()

        if self.rocket:
            t = pg.time.get_ticks() / 1000.0
            self.rocket.update(np.array([0.2, 0.5]), t * 360 * 3, 15, 0)
            self.specification.update()
            self.spec_detail.update()
            self.flight_profile.update()
            self.flight_profile_detail.update()

    def draw(self, screen: pg.Surface) -> None:
        """
        Draw the briefing scene elements.

        Args:
            screen: Pygame surface to draw on
        """
        self.FTE_icon.draw(screen)
        self.copyright.draw(screen)
        self.back_icon.draw(screen)
        self.back_icon_text.draw(screen)

        if self.rocket:
            self.rocket.draw(screen)
            self.specification.draw(screen)
            self.spec_detail.draw(screen)
            self.flight_profile.draw(screen)
            self.flight_profile_detail.draw(screen)


class GameScene(Scene):
    """
    Flight simulation game scene.
    """

    def __init__(self) -> None:
        """
        Initialize the game scene.
        """
        super().__init__()
        self.state = SCENE_STATE.GAME

    def handle_event(self, event) -> SCENE_STATE:
        """
        Process events for the game scene.

        Args:
            event: Pygame event to process

        Returns:
            SCENE_STATE: New scene state if transition is needed, None otherwise
        """
        result = super().handle_event(event)
        if result:
            return result
        return None

    def update(self) -> None:
        """
        Update the game state.
        """
        pass

    def draw(self, screen: pg.Surface) -> None:
        """
        Draw the game elements.

        Args:
            screen: Pygame surface to draw on
        """
        pass
