"""A simple app to reframe an resize pictures"""

from typing import List
import sys
from pathlib import Path
from dataclasses import dataclass

import pygame
import pygame as pg

pygame.init()


@dataclass
class _Config:
    source_dir = Path("/home/teo/Dokumente/personal/Photos/Family")
    target_dir = Path("/home/teo/Dokumente/personal/Photos/Family_resized")
    resources_dir = Path("resources")
    img_rect = pg.Rect([0, 0, 123, 113])
    window_size = 900, 600


CFG = _Config()
# %%


def _main():
    # %%
    app_state = AppState()
    app_state.run()
    # %%


def _interactive_testing():
    # %%
    runfile("image_frame_resize/img_reframe_rsz.py")
    # %%


class AppState:
    """The apps moving parts"""
    def __init__( self ):
        CFG.target_dir.mkdir( parents=True, exist_ok=True )
        self.source_img_fps: List[Path] = list(CFG.source_dir.glob("*"))
        print( len(self.source_img_fps), " found" )

        pg.display.set_mode( CFG.window_size )

        self.left_button = pygame.image.load( CFG.resources_dir / "left_button.png" )
        self.right_button = pygame.image.load( CFG.resources_dir / "right_button.png")

    def run( self ):
        """run the event loop"""
        while True:
            if should_quit():
                break


def should_quit():
    """Quit if there is a quit event"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return True

        print( event )

    return False
