"""A simple app to reframe an resize pictures"""

from typing import List, Tuple
import sys
import time
from pathlib import Path
from dataclasses import dataclass

import numpy as np
from skimage.io import imread, imsave
from skimage.transform import resize

import pygame as pg
from pygame import Surface

pg.init()


@dataclass
class _Config:
    source_dir = Path("/home/teo/Dokumente/personal/Photos/Family")
    target_dir = Path("/home/teo/Dokumente/personal/Photos/Family_resized")
    resources_dir = Path("image_reframe_resize/resources")
    move_incs = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    geom_incs = [1.01, 1.02, 1.04, 1.08, 1.16, 1.32, 1.50, 2.0, 4.0]
    window_size = 1200, 1000
    image_height = 800
    target_size = (1280, 800)
    jpeg_quality = 95

    def target_proportion( self ):
        """target width/height"""
        return self.target_size[0] / self.target_size[1]


BLACK = [0, 0, 0]

CFG = _Config()
# %%


def _main():
    # %%
    if len(sys.argv) >= 3:
        CFG.source_dir = Path( sys.argv[1] )
        CFG.target_dir = Path( sys.argv[2] )

    app_state = AppState()

    app_state.run()
    # %%


def _interactive_testing():
    # %%
    runfile("image_reframe_resize/img_reframe_rsz.py")

    rect = pg.Rect([0, 0, 330, 330])

    img_fp = list( CFG.source_dir.glob("*") )[0]

    image = pg.image.load(img_fp)
    # %%
    image = imread( img_fp )
    # %%


def scale_to_height( img: Surface, target_height: int ) -> Surface:
    """scale image to a given target_height, return new image"""
    width, height = img.get_size()
    new_size = int( (target_height / height ) * width),  int(target_height)

    return pg.transform.scale(img, new_size )
    # else:


class AppState:
    """The apps moving parts"""
    def __init__( self ):
        print( f'source_dir: {CFG.source_dir}' )
        print( f'target_dir: {CFG.target_dir}' )
        CFG.target_dir.mkdir( parents=True, exist_ok=True )
        self.source_img_fps: List[Path] = []
        self.n_imgs = 0
        self.img_idx = 0
        self.geom_inc = 1.05
        self.move_inc = 8

        self._load_source_img_fps()

        self.screen = pg.display.set_mode( CFG.window_size )

        self.left_button = pg.image.load( CFG.resources_dir / "left_button.png" )
        self.left_btn_rect = self.left_button.get_rect().move([0, CFG.window_size[1] - 100])

        self.right_button = pg.image.load( CFG.resources_dir / "right_button.png")
        self.right_btn_rect = self.right_button.get_rect().move([CFG.window_size[0] - 80,
                                                                 CFG.window_size[1] - 100])

        self._load_img()
        img_width = self.image_scaled.get_size()[0]

        self.frame = pg.Rect( [0, 0, img_width - 2, img_width / CFG.target_proportion() - 2] )
        self._draw_image_and_frame()
        self._draw_buttons()

    def _load_img( self ):
        self.orig_image_fp = self.source_img_fps[self.img_idx]
        self.orig_image = pg.image.load( self.orig_image_fp )
        self.image_scaled = scale_to_height( self.orig_image, CFG.image_height )

    def run( self ):
        """run the event loop"""
        while True:
            if self.process_events():
                return

            self.screen.fill( BLACK )

            img_w = self.image.get_width()
            img_x = self.screen.get_width() / 2 - img_w / 2
            self.screen.blit( self.image, (img_x, 50) )

            self._draw_buttons()

            pg.display.flip()
            time.sleep(0.050)

    def process_events(self):
        """Quit if there is a quit event"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit(0)

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEWHEEL) :
                self._process_mouse_event(event)

            elif event.type == pg.KEYUP:
                # print( event )
                self._process_kb_event(event)

            # print( event )

    def _process_mouse_event( self, event ):
        # print( type(event), event )

        if event.type == pg.MOUSEBUTTONDOWN:
            if _is_in_rect( event.pos, self.left_btn_rect ):
                self._img_skip(inc=-1)
            if _is_in_rect( event.pos, self.right_btn_rect ):
                self._img_skip(inc=+1)

        elif event.type == pg.MOUSEWHEEL:
            # print( event )
            if event.y == +1:
                self._reduce_frame()
            elif event.y == -1:
                self._enlarge_frame()

    def _process_kb_event( self, event ):
        if event.key == pg.K_UP:
            self.frame.y -= self.move_inc
            self._draw_image_and_frame()

        elif event.key == pg.K_DOWN:
            self.frame.y += self.move_inc
            self._draw_image_and_frame()

        elif event.key == pg.K_RIGHT:
            self.frame.x += self.move_inc
            self._draw_image_and_frame()

        elif event.key == pg.K_LEFT:
            self.frame.x -= self.move_inc
            self._draw_image_and_frame()

        elif event.key == pg.K_PAGEUP:
            self._img_skip(inc=-1)

        elif event.key == pg.K_PAGEDOWN:
            self._img_skip(inc=+1)

        elif event.key == pg.K_KP_PLUS:
            self._enlarge_frame()

        elif event.key == pg.K_KP_MINUS:
            self._reduce_frame()

        elif pg.K_1 <= event.key <= pg.K_9:
            self._update_incs( event.key - pg.K_1 )

        elif event.key == pg.K_KP_ENTER or event.key == pg.K_RETURN:
            self._save_resized_image()

    def _enlarge_frame(self):
        self.frame.h *= self.geom_inc
        self.frame.w = self.frame.h * CFG.target_proportion()
        self._draw_image_and_frame()

    def _reduce_frame( self ):
        self.frame.h /= self.geom_inc
        self.frame.w = self.frame.h * CFG.target_proportion()
        self._draw_image_and_frame()

    def _update_incs( self, idx: int ):
        self.geom_inc = CFG.geom_incs[idx]
        self.move_inc = CFG.move_incs[idx]
        print(f'geom_inc = {self.geom_inc}, move_inc = {self.move_inc}')

    def _img_skip( self, inc: int ):
        self.img_idx += inc
        self.img_idx = (self.img_idx + self.n_imgs) % self.n_imgs
        self._load_img()
        self._draw_image_and_frame()

    def _load_source_img_fps( self ):

        all_files = list( CFG.source_dir.glob( "*" ) )

        self.source_img_fps = [ fpath for fpath in all_files
                                if fpath.suffix.lower() in (".jpg", ".png")]

        print( len( self.source_img_fps ), f" found:\n{self.source_img_fps}" )

        self.n_imgs = len( self.source_img_fps )

        if self.n_imgs == 0:
            raise RuntimeError( f"No images found under {CFG.source_dir}" )

    def _draw_image_and_frame( self ):

        frame = self.frame
        self.image = self.image_scaled.copy()
        pg.draw.lines( self.image, closed=True, color=pg.Color('blue'),
                       points=[ (frame.x, frame.y),
                                (frame.x + frame.w, frame.y),
                                (frame.x + frame.w, frame.y + frame.h),
                                (frame.x, frame.y + frame.h)],
                       width=2 )

    def _draw_buttons( self ):
        self.screen.blit( self.left_button, self.left_btn_rect )
        self.screen.blit( self.right_button, self.right_btn_rect )

    def _save_resized_image( self ):

        w, h = self.image.get_size()

        disk_image = imread( str(self.orig_image_fp) )

        if len(disk_image.shape) == 2:
            oh, ow = disk_image.shape
        elif len(disk_image.shape) == 3:
            oh, ow, _ = disk_image.shape
        else:
            raise ValueError(f'disk_image_size: {disk_image.size}')

        j1 = int( (self.frame.left / w) * ow )
        j2 = int( (self.frame.right / w) * ow )

        i1 = int( (self.frame.top / h) * oh )
        i2 = int( (self.frame.bottom / h) * oh )

        cropped = disk_image[i1:i2, j1:j2, ...]

        print( f"cropped proportions: {(j2 - j1)/(i2 - i1)}")

        out_sz_hw = CFG.target_size[1], CFG.target_size[0]

        resized = (resize( cropped, out_sz_hw, order=3, anti_aliasing=True )
                   * 255.0).astype(np.uint8)
        out_fpath = CFG.target_dir / (self.orig_image_fp.stem + '.jpg')
        print( f"saving resized image: {out_fpath}")
        imsave( out_fpath, resized, quality=CFG.jpeg_quality )
        # %%


def _is_in_rect( pos: Tuple[int], rect: pg.Rect ) -> bool:
    return (rect.x <= pos[0] <= rect.x + rect.h) and (rect.y <= pos[1] <= rect.y + rect.h)


# if __name__ == "__main__":
#     _main()
