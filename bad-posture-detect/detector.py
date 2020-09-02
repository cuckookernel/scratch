"""Periodically capture images from camera

Prerequisites:
  - sudo apt-get install libgtk2.0-dev
  - conda install -c conda-forge opencv=4.1.0
  - pip install opencv-contrib-python  : Needed to get cv2.data submodule
"""
import os
import cv2
import time
import datetime as dt
from pathlib import Path

import numpy as np
from cv2 import VideoCapture
import pygame

# type alias
Image = np.ndarray  # A CV2-images is really just an array

CAMERA_IDX = 2  # Necessary when there is more than one webcam in the system, otherwise just use 0
SLOUCH_THRESHOLD = 0.3
ALERT_SOUND_FILE = os.getenv('HOME') + '/suspend-error.oga'
FACE_DETECT_MODEL_SPEC = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

DATA_PATH = Path(os.getenv('HOME')) / '_data/bad-posture-detect'
DATA_PATH.mkdir(parents=True, exist_ok=True)
# %%


def _interactive_testing():
    # %%
    runfile('bad-posture-detect/detector.py')
    # %%
    face_cascade = cv2.CascadeClassifier(FACE_DETECT_MODEL_SPEC)
    # Load the cascade detector (this is classical computer vision, not neural-network based!)
    # face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # %%
    # Read the input image
    cam = VideoCapture( CAMERA_IDX )
    # %% GUI sound production
    pygame.mixer.init()

    # %%
    img = _capture_img(cam)
    # an (color) image is just a Width x Height x NumChannels 'matrix', really a rank-3 tensor
    # channels are Blue, Green, Red (CV2 ideasyncratic ordering...)
    print( type(img),  img.shape )   # =>  <ndarray>  (480, 640, 3)
    # _interactive_show_img( img )
    # Convert into grayscale
    # an grayscale image is just a Width x Height x NumChanels matrix, really a rank-2 tensor
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(type(gray), gray.shape)   # =>  <ndarray>  (480, 640)
    # %%
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    print( faces )

    _draw_face_frames( faces, img )
    # %%
    cv2.imwrite( str(DATA_PATH / "img_and_faces.jpg"), img )
    # %%
    cam.release()  # close the webcam
    # %%
    play_alert_sound()
    # %%


def _draw_face_frames( faces, img ):
    """Draw rectangles around the faces"""
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
    # %%


def _capture_img( cam: cv2.VideoCapture ):
    s, img = cam.read()
    if not s:
        raise RuntimeError('Failed to get img from camera')
    return img
    # %%


def _interactive_show_img( img, window_title='cam-img' ):
    cv2.imshow(window_title, img)
    cv2.waitKey()
    # %%


def play_alert_sound():
    # %%
    sound = pygame.mixer.Sound( ALERT_SOUND_FILE )
    sound.play()
    # %%


class SlouchDetector:

    def __init__(self, thresh: float ):
        self.reference_y = None
        self.thresh = thresh

    def detect(self, faces):

        now = dt.datetime.now()

        if len(faces) > 0:
            face_height = faces[0][3]
            current_y = ( faces[0][1] + face_height * 0.5 )

            if self.reference_y is None:
                self.reference_y = current_y

            ratio = -(current_y - self.reference_y) / face_height

            if ratio < -self.thresh:
                print(f'{now} {current_y} {face_height} ratio:{ratio:.4f} you are slouching!!!' )
                play_alert_sound()
            else:
                print(f'{now}, {current_y}, {ratio:.4f} you are OK')
        else:
            print(now, 'no faces detected')
# %%


def main():
    # %%
    face_cascade = cv2.CascadeClassifier( FACE_DETECT_MODEL_SPEC )
    pygame.mixer.init()
    cam = VideoCapture( CAMERA_IDX )

    detector = SlouchDetector( SLOUCH_THRESHOLD )

    try:
        while True:
            img = _capture_img(cam)
            # an (color) image is just a Width x Height x NumChannels 'matrix',
            # really a rank-3 tensor
            # channels are Blue, Green, Red (CV2 ideasyncratic ordering...)
            # print( type(img),  img.shape )   # =>  <ndarray>  (480, 640, 3)
            # Convert into grayscale
            # an grayscale image is just a Width x Height x NumChanels matrix,
            # really a rank-2 tensor
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # print(type(gray), gray.shape)   # =>  <ndarray>  (480, 640)

            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            detector.detect( faces )
            time.sleep(2)

    except Exception as exc:
        cam.release()  # close the webcam
        raise exc

main()
