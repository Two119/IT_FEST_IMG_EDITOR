import pygame, json, webbrowser, time, random, sys
from tkinter import filedialog
from PIL import Image, ImageDraw
global current;
class AppObj:
    def __init__(self):
        self.update_args = []
    def update(self):
        pass
class CurrentImage(AppObj):
    def __init__(self, surf, screenpos):
        self.texture = surf;
        self.update_args = screenpos;
        self.gif = False;
    def update(self):
        if not self.gif:
            self.update_args[1].blit(self.texture, self.update_args[0]);
            pygame.display.update();
        else:
            for frame in self.texture:
                self.update_args[1].fill((0, 0, 0));
                self.update_args[1].blit(frame, self.update_args[0]);
                pygame.display.update();
                time.sleep(0.04);
        return

class ImageEditor:
    def scale_image(img, factor=4):
        size = round(img.get_width() * factor), round(img.get_height() * factor);
        return pygame.transform.scale(img, size);
    def save_image(img, filename):
        pygame.image.save(img, filename);
        return;
    def FileDialog():
        filepath = filedialog.askopenfilename(title="Open file")
        return filepath
class STD_IMG(AppObj):
    def __init__(self, img):
        self.texture = img;
    def update(self):
        self.update_args[1].fill((0, 0, 0));
        self.update_args[1].blit(self.texture, self.update_args[0]);
        pygame.display.update();
        return
class GIF(AppObj):
    def __init__(self, frames):
        self.frames = frames;
        self.num_frames = len(frames);
    def update(self):
        for frame in self.frames:
            self.update_args[1].fill((0, 0, 0));
            self.update_args[1].blit(frame, self.update_args[0]);
            pygame.display.update();
            time.sleep(0.04);
        return;
class GifProcesser(ImageEditor):
    def pil_to_game(img):
        data = img.tobytes("raw", "RGBA");
        return pygame.image.fromstring(data, img.size, "RGBA");
    def get_gif_frame(img, frame):
        img.seek(frame);
        return  img.convert("RGBA");
    
    def load_gif(gif, scale=1):
        current_frame1 = 0;
        cycles1 = 0;
        gif_img1 = Image.open(gif);
        output = [];
        for i in range(gif_img1.n_frames):
            cycles1+=1;
            if cycles1 == gif_img1.n_frames:
                    break;
            frame1 = ImageEditor.scale_image(GifProcesser.pil_to_game(GifProcesser.get_gif_frame(gif_img1, current_frame1)), scale);
            output.append(frame1);
            current_frame1 = (current_frame1 + 1) % gif_img1.n_frames;
        return GIF(output);
    def crop_gif(gif, new_dimensions):
        for i in range(gif.num_frames):
            newframe = pygame.Surface(new_dimensions);
            newframe.blit(gif.frames[i], [0, 0]);
            gif.frames[i] = newframe;
    def swap_color_in_gif(gif, colors, threshold=(0, 0, 0, 0)):
        for frame in gif.frames:
            pygame.transform.threshold(frame,frame,colors[0], threshold, colors[1], 1, None, True);
    def split_gif_to_frames(gif):
        return gif.frames;
    def save_images_to_gif(images, filename, optimiz):     
       image = []
       for img__ in images:
            image.append(Image.open(img__));
       image[0].save(str(filename), save_all=True, append_images=image[1:], optimize=optimiz, duration=40, loop=0)
class Button(AppObj):
    def __init__(self, position, textures, function, screen):
        self.textures = textures;
        self.onlick = function[0];
        self.args = function[1];
        self.pos = position;
        self.screen = screen;
        self.current = 0;
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);
        self.click_delay = 0;
        self.max_delay = 100;
        self.delaying = False;
    def update(self):
        self.current = 0;
        if self.delaying:
            self.click_delay += 1;
        if self.click_delay >= self.max_delay:
            self.delaying = False;
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.delaying:
                    self.onlick(self.args)
                self.delaying = True;
            self.current = 1;
        self.screen.blit(self.textures[self.current], self.pos)
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);
class interface(AppObj):
    def __init__(self):
        global scale;
        self.positions = [[10*scale["w"], 50*scale["h"]], [10*scale["w"], 100*scale["h"]]];
        self.ButtonLoader();
        self.button_dicts = {};
    def update(self):
        global current;
        for ui in range(len(self.buttons)):
            self.buttons[ui].update();
        current.update();
    def ButtonLoader(self):
        
        def load_image(args):
            to_load = ImageEditor.FileDialog();
            if (to_load.find(".gif")):
                global current;
                current.texture = (GifProcesser.load_gif(to_load).frames);
                current.gif = True;
            if not (to_load.find(".gif")):
                current.texture = (pygame.image.load(to_load));
                current.gif = False;
        self.button_textures = [[pygame.image.load("Assets\\Images\\UI\\load.png")], [pygame.image.load("Assets\\Images\\UI\\exit.png")]];
        for TexList in self.button_textures:
            surf = pygame.Surface((TexList[0].get_width(), TexList[0].get_height()));
            pygame.draw.rect(surf, [128, 128, 128], TexList[0].get_rect(topleft=(0, 0)));
            surf.set_alpha(100);
            TexList[0].set_colorkey((128, 255, 128));
            new = (TexList[0].copy())
            new.blit(surf, (0, 0));
            new.set_colorkey((128, 206, 128));
            TexList.append(new)
            
        self.buttons = [];
        button_num = -1;
        for tex in self.button_textures:
            button_num += 1;
            self.buttons.append(Button(self.positions[button_num], tex, [load_image, []], win));
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN);
current_h_w = [win.get_width(), win.get_height()];
default_h_w = [1366, 768];
global scale;
scale = {"w":current_h_w[0]/default_h_w[0], "h":current_h_w[1]/default_h_w[1]};
win = pygame.display.set_mode((400*scale["w"], 600*scale["h"]))
current = CurrentImage(pygame.Surface((10, 10)), [[20, 50], win]);
Interface = interface();
while True:
    win.fill((0, 0, 0));
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit();
    Interface.update();
    pygame.display.update();