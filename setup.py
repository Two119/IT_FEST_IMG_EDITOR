from distutils.core import setup
import py2exe
import pygame, sys, imghdr
from tkinter import filedialog
from pygame.locals import *
from PIL import Image, ImageDraw
import face_recognition
setup(windows=['main.py'])