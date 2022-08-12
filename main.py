import pygame, sys, imghdr, threading
from tkinter import filedialog
from PIL import Image, ImageDraw
global current;
class AppObj:
    def __init__(self):
        self.update_args = []
    def update(self):
        pass
class DropDownButton(AppObj):
    def __init__(self, color, rec, menu, index):
        self.color = color
        self.rect = rec
        self.menu = menu
        self.index = index
    def update(self):
        pygame.draw.rect(win, self.color, self.rect)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(win, [self.color[0]-50, self.color[1]-50, self.color[2]-50], self.rect)
            if pygame.mouse.get_pressed()[0]:
                self.menu.selected = self.index;
class DropDown(AppObj):
    def __init__(self, title, options, position, dimensions=[80, 40], color=[255, 255, 255]):
        self.options = options
        self.position = position
        self.dimensions = dimensions
        self.color = color
        self.title = title
        self.showing = True
        self.selected = None;
        self.rect = pygame.Rect(position[0], position[1], dimensions[0], dimensions[1])
        self.buttons = []
        for i in range(1, len(options)+1):
            self.buttons.append(DropDownButton(self.color, pygame.Rect(self.rect.left, self.rect.top+40*i, self.rect.width, self.rect.height), self, i))

    def update(self):
        pygame.draw.rect(win, self.color, self.rect)
        if self.showing:
            for button in self.buttons:
                button.update();
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(win, [self.color[0]-50, self.color[1]-50, self.color[2]-50], self.rect)
            if pygame.mouse.get_pressed()[0]:
                self.showing = False
        
class CurrentImage(AppObj):
    def __init__(self, surf, screenpos):
        self.texture = surf;
        self.update_args = screenpos;
        self.gif = False;
        self.optimize = False;
        self.duration = 40;
        self.per_frame = 14;
        self.loop = 0;
        self.raw = None;
    def update(self):
        if not self.gif:
            self.update_args[1].blit(self.texture, self.update_args[0]);
            pygame.display.update();
        return
def form_init():
        global forms
        forms = [("gif files", "*.gif")];
        global formats;
        for form in formats:
            forms.append((form+" files", "*."+form))
class ImageEditor:
    def scale_image(img, factor=4):
        size = round(img.get_width() * factor), round(img.get_height() * factor);
        return pygame.transform.scale(img, size)
    def save_image(img, filename):
        pygame.image.save(img, filename);
        return;
    global forms
    def openFileDialog():
        filepath = filedialog.askopenfilename(initialdir="C:\\",title="Open file", filetypes = forms)
        return filepath
    def saveFileDialog():
        filepath = filedialog.asksaveasfilename(initialdir="C:\\",title="Save as", filetypes = forms)
        return filepath
class GIF(AppObj):
    def __init__(self, frames, raw):
        self.frames = frames;
        self.raw = raw;
        self.num_frames = len(frames);
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
        return GIF(output, gif_img1);
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
    def save_images_to_gif(images, filename, optimize=False, duration=40, loop=0, readable=False):
        if not readable:     
            image = []
            for img__ in images:
                    image.append(Image.open(img__));
            image[0].save(str(filename), save_all=True, append_images=image[1:], optimize=optimize, duration=duration, loop=loop)
        else:
            images[0].save(str(filename), save_all=True, append_images=images[1:], optimize=optimize, duration=duration, loop=loop)
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
        self.max_delay = 500;
        self.delaying = False;
        global current
    def update(self):
        self.current = 0;
        if self.delaying:
            self.click_delay += 1;
        if self.click_delay >= self.max_delay:
            self.delaying = False;
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.delaying:
                    self.onlick(self.args);
                self.delaying = True;
            self.current = 1;
        self.screen.blit(self.textures[self.current], self.pos);
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);
class Popup(AppObj):
    def __init__(self, title, text, dimensions, position, background):
        self.popup_surf = pygame.Surface(dimensions)
        self.popup_surf.blit(background, [0, 0])
class interface(AppObj):
    def __init__(self):
        global scale;
        self.positions = [[10*scale["w"], 50*scale["h"]], [10*scale["w"], 100*scale["h"]], [10*scale["w"], 150*scale["h"]]];
        self.ButtonLoader();
        self.button_dicts = {};
    def update(self):
        global current;
        for ui in range(len(self.buttons)):
            self.buttons[ui].update();
        current.update();
        pygame.display.update()
    def ButtonLoader(self):
        global formats
        def load_image(args):
            to_load = ImageEditor.openFileDialog();
            if to_load != '':
                if imghdr.what(to_load) == "gif":
                    global current;
                    current.texture = (GifProcesser.load_gif(to_load).frames);
                    current.raw = (GifProcesser.load_gif(to_load).raw);
                    current.gif = True;
                if (imghdr.what(to_load) in formats):
                    current.texture = (pygame.image.load(to_load));
                    current.gif = False;
            return
        def save(args):
            if current.gif:
                fram = [];
                num_frame = -1;
                for tex in current.texture:
                    num_frame += 1;
                    current.raw.seek(num_frame)
                    fram.append(current.raw.convert("RGBA"));
                GifProcesser.save_images_to_gif(fram, ImageEditor.saveFileDialog()+".gif", current.optimize, current.duration, current.loop, True);
            else:
                ImageEditor.save_image(current.texture, ImageEditor.saveFileDialog());
        def ex(args):
            sys.exit();
        self.button_textures = [[pygame.image.load("Assets\\Images\\UI\\load.png")], [pygame.image.load("Assets\\Images\\UI\\save.png")], [pygame.image.load("Assets\\Images\\UI\\exit.png")]];
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
        self.button_functions = [load_image, save, ex];
        button_num = -1;
        for tex in self.button_textures:
            button_num += 1;
            self.buttons.append(Button(self.positions[button_num], tex, [self.button_functions[button_num], []], win));
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN);
current_h_w = [win.get_width(), win.get_height()];
default_h_w = [1366, 768];
global scale;
scale = {"w":current_h_w[0]/default_h_w[0], "h":current_h_w[1]/default_h_w[1]};
global formats;
formats = ['rgb','pbm','pgm','ppm','tiff','rast','xbm','jpeg','bmp','png','webp','exr'];
win = pygame.display.set_mode((400*scale["w"], 600*scale["h"]))
current = CurrentImage(pygame.Surface((10, 10)), [[100, 50], win]);
Interface = interface();
delay = 0;
frame = -1;
form_init();
drop = DropDown("hallo", [1, 2, 3], [150, 100])
while True:
    #win.fill((0, 0, 0));
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit();
    if current.gif:
        if delay == 0:
            current.duration = current.per_frame*len(current.texture);
        delay += 1
        if delay %  current.per_frame == 0:
            frame += 1;
        if frame >= len(current.texture):
            frame = 0;
        current.update_args[1].blit(current.texture[frame], current.update_args[0]);
    Interface.update();   
    drop.update();    
    pygame.display.update();