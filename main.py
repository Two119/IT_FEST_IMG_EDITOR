import numpy as np
import pygame, sys, cv2, threading
from tkinter import filedialog
from pygame.locals import *
from PIL import Image, ImageDraw
import face_recognition
global current;
global cur_dict;
cur_dict = {"other.png":"photo.png", "photo.png":"other.png"}
global saving;
saving = False
pygame.init()
class AppObj:
    def __init__(self):
        self.update_args = []
        self.filepath = '';
    def update(self):
        pass
class DropDownButton(AppObj):
    def __init__(self, color, rec, menu, index):
        self.color = color
        self.rect = rec
        self.menu = menu
        self.index = index
        self.font = pygame.font.SysFont(self.menu.font_name, 22)
        self.text = self.font.render(self.menu.options[self.index],True,(0, 0, 0), (255, 255, 255))
        self.hover_text = self.font.render(self.menu.options[self.index],True,(0, 0, 0), [self.color[0]-50, self.color[1]-50, self.color[2]-50])
    def update(self):
        pygame.draw.rect(win, self.color, self.rect)
        win.blit(self.text, [self.rect.x, self.rect.y])
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(win, [self.color[0]-50, self.color[1]-50, self.color[2]-50], self.rect)
            win.blit(self.hover_text, [self.rect.x, self.rect.y])
            if pygame.mouse.get_pressed()[0]:
                self.menu.selected = self.index;
                
class DropDown(AppObj):
    def __init__(self, title, options, position, dimensions=[80, 40], color=[255, 255, 255], font="Calibri"):
        self.options = options
        self.position = position
        self.dimensions = dimensions
        self.color = color
        self.title = title
        self.font_name = font
        self.showing = True
        self.selected = None;
        self.rect = pygame.Rect(position[0], position[1], dimensions[0], dimensions[1])
        self.buttons = []
        self.font = pygame.font.SysFont(font, 22)
        self.text = self.font.render(self.title,True,(0, 0, 0), (255, 255, 255))
        self.hover_text = self.font.render(self.title,True,(0, 0, 0), [self.color[0]-50, self.color[1]-50, self.color[2]-50])
    def update(self):
        pygame.draw.rect(win, self.color, self.rect)
        win.blit(self.text, [self.rect.x, self.rect.y])
        if self.showing:
            for i in range(0, len(self.options)):
                    self.buttons.append(DropDownButton(self.color, pygame.Rect(self.rect.left, self.rect.top+((40)*(i+1)), self.rect.width, self.rect.height), self, i))
            for button in self.buttons:
                button.update();
            self.buttons = []
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(win, [self.color[0]-50, self.color[1]-50, self.color[2]-50], self.rect)
            win.blit(self.hover_text, [self.rect.x, self.rect.y])
            if pygame.mouse.get_pressed()[0]:
                self.showing = not self.showing
        
class CurrentImage(AppObj):
    def __init__(self, surf, screenpos):
        self.filepath = ""
        self.texture = surf;
        self.update_args = screenpos;
        self.gif = False;
        self.optimize = False;
        self.duration = 40;
        self.per_frame = 14;
        self.comparison_photo = None;
        self.loop = 0;
        self.raw = None;
        self.comp_raw = None;
    def update(self):
        if not self.gif:
            self.update_args[1].blit(self.texture, self.update_args[0]);
            pygame.display.update();
            if self.comparison_photo != None:
                self.update_args[1].blit(self.comparison_photo, [self.update_args[0][0], self.update_args[0][1]+self.texture.get_height()]);
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
        global scale, drop, current, formats, cur_dict;
        self.positions = [[10*scale["w"], 50*scale["h"]], [10*scale["w"], 100*scale["h"]], [10*scale["w"], 150*scale["h"]], [10*scale["w"], 200*scale["h"]], [10*scale["w"], 250*scale["h"]], [10*scale["w"], 300*scale["h"]], [10*scale["w"], 350*scale["h"]], [10*scale["w"], 400*scale["h"]], [10*scale["w"], 450*scale["h"]],[10*scale["w"], 500*scale["h"]]];
        self.ButtonLoader();
        self.button_dicts = {};
    def update(self):

        for ui in range(len(self.buttons)):
            self.buttons[ui].update();
        current.update();
        pygame.display.update()
        
    def ButtonLoader(self):

        def load_image(args):
            to_load = "photo.png"
            if current.filepath != '':
                current.comparison_photo = (pygame.image.load(to_load));
                current.gif = False;
            else:
                current.texture = pygame.image.load("photo.png")
                current.filepath = to_load
            return
        def load_compare(args):
            to_load = "other.png"
            if current.filepath != '':
                current.comparison_photo = (pygame.image.load(to_load));
                current.gif = False;
            else:
                current.texture = pygame.image.load("other.png")
                current.filepath = to_load
            return
        def save(args):
            ImageEditor.save_image(current.texture, "saves/1.png")
            if current.comparison_photo != None:
                ImageEditor.save_image(current.comparison_photo, "saves/2.png")
        def ex(args):
            sys.exit();

        def identify_face(args):
            
            image = np.array((current.raw).convert('RGB'))
            face_locations = face_recognition.face_locations(image, 5, "hog")
            pil_image = Image.open(current.filepath)
            for face_location in face_locations:
                top, right, bottom, left = face_location
                
                draw = ImageDraw.Draw(pil_image)
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0))
            pil_image.save("output.png")
            current.texture = pygame.image.load("output.png")
            if current.comparison_photo != None:
                image2 = face_recognition.load_image_file("other.png")
                face_locations2 = face_recognition.face_locations(image2, 5, "hog")
                pil_image2 = Image.open(cur_dict[current.filepath])
                for face_location2 in face_locations2:
                    top2, right2, bottom2, left2 = face_location2
                    
                    draw2 = ImageDraw.Draw(pil_image2)
                    draw2.rectangle(((left2, top2), (right2, bottom2)), outline=(0, 255, 0))
                pil_image2.save("output.png")
                current.comparison_photo = pygame.image.load("output.png")
        def compare(args):
            
            results = face_recognition.compare_faces([face_recognition.face_encodings(current.raw)[0]], face_recognition.face_encodings(face_recognition.load_image_file("other.png"))[0])
            if results[0]:                
                image = np.array((current.raw).convert('RGB'))
                face_locations = face_recognition.face_locations(image, 5, "hog")
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    pil_image = Image.open(current.filepath)
                    draw = ImageDraw.Draw(pil_image)
                    draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0))
                    pil_image.save("output.png")
                    current.texture = pygame.image.load("output.png")
                image2 = face_recognition.load_image_file(cur_dict[current.filepath])
                face_locations2 = face_recognition.face_locations(image2, 5, "hog")
                for face_location2 in face_locations2:
                    top2, right2, bottom2, left2 = face_location2
                    pil_image2 = Image.open(cur_dict[current.filepath])
                    draw2 = ImageDraw.Draw(pil_image2)
                    draw2.rectangle(((left2, top2), (right2, bottom2)), outline=(0, 255, 0))
                    current.comparison_photo = GifProcesser.pil_to_game(pil_image2)
                torender = drop.font.render("It's a match",True,(0, 0, 0), (0, 255, 0))
                current.texture.blit(torender, [0, 0])
            else:           
                image = np.array((current.raw).convert('RGB'))
                face_locations = face_recognition.face_locations(image, 5, "hog")
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    pil_image = Image.open(current.filepath)
                    draw = ImageDraw.Draw(pil_image)
                    draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0))
                    current.texture = GifProcesser.pil_to_game(pil_image)
                image2 = face_recognition.load_image_file(cur_dict[current.filepath])
                face_locations2 = face_recognition.face_locations(image2, 5, "hog")
                for face_location2 in face_locations2:
                    top2, right2, bottom2, left2 = face_location2
                    pil_image2 = Image.open(cur_dict[current.filepath])
                    draw2 = ImageDraw.Draw(pil_image2)
                    draw2.rectangle(((left2, top2), (right2, bottom2)), outline=(255, 0, 0))
                    pil_image2.save("output.png")
                    current.comparison_photo = pygame.image.load("output.png")
                torender = drop.font.render("It's not a match",True,(0, 0, 0), (255, 0, 0))
                current.texture.blit(torender, [0, 0])
            return results[0]
        def outline_features(args):

            image = np.array((current.raw).convert('RGB'))
            face_landmarks_list = face_recognition.face_landmarks(image)
            pil_image = Image.fromarray(image)
            d = ImageDraw.Draw(pil_image)
            for face_landmarks in face_landmarks_list:
                for facial_feature in face_landmarks.keys():
                    d.line(face_landmarks[facial_feature], width=2)
            current.texture = GifProcesser.pil_to_game(pil_image)
            if current.comparison_photo != None:
                image2 = face_recognition.load_image_file("other.png")
                face_landmarks_list2 = face_recognition.face_landmarks(image2)
                pil_image2 = Image.fromarray(image2)
                d2 = ImageDraw.Draw(pil_image2)
                for face_landmarks2 in face_landmarks_list2:
                    for facial_feature2 in face_landmarks2.keys():
                        d2.line(face_landmarks2[facial_feature2], width=2)
                current.comparison_photo = GifProcesser.pil_to_game(pil_image2)
        def reset(args):
            current.texture = pygame.image.load(current.filepath)
            if current.comparison_photo != None:
                current.comparison_photo = pygame.image.load(cur_dict[current.filepath])
        def add_makeup(args):
            image = np.array((current.raw).convert('RGB'))

            # Find all facial features in all the faces in the image
            face_landmarks_list = face_recognition.face_landmarks(image)

            pil_image = Image.fromarray(image)
            for face_landmarks in face_landmarks_list:
                d = ImageDraw.Draw(pil_image, 'RGBA')

                # Make the eyebrows into a nightmare
                d.polygon(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 128))
                d.polygon(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 128))
                d.line(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 150), width=5)
                d.line(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 150), width=5)

                # Gloss the lips
                d.polygon(face_landmarks['top_lip'], fill=(150, 0, 0, 128))
                d.polygon(face_landmarks['bottom_lip'], fill=(150, 0, 0, 128))
                d.line(face_landmarks['top_lip'], fill=(150, 0, 0, 64), width=8)
                d.line(face_landmarks['bottom_lip'], fill=(150, 0, 0, 64), width=8)

                # Sparkle the eyes
                d.polygon(face_landmarks['left_eye'], fill=(255, 255, 255, 30))
                d.polygon(face_landmarks['right_eye'], fill=(255, 255, 255, 30))

                # Apply some eyeliner
                d.line(face_landmarks['left_eye'] + [face_landmarks['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
                d.line(face_landmarks['right_eye'] + [face_landmarks['right_eye'][0]], fill=(0, 0, 0, 110), width=6)
            pil_image.save("output.png")
            current.texture = pygame.image.load("output.png")
            if current.comparison_photo != None:
                image2 = face_recognition.load_image_file("other.png")

                # Find all facial features in all the faces in the image
                face_landmarks_list2 = face_recognition.face_landmarks(image2)

                pil_image2 = Image.fromarray(image2)
                for face_landmarks2 in face_landmarks_list2:
                    d2 = ImageDraw.Draw(pil_image2, 'RGBA')

                    # Make the eyebrows into a nightmare
                    d2.polygon(face_landmarks2['left_eyebrow'], fill=(68, 54, 39, 128))
                    d2.polygon(face_landmarks2['right_eyebrow'], fill=(68, 54, 39, 128))
                    d2.line(face_landmarks2['left_eyebrow'], fill=(68, 54, 39, 150), width=5)
                    d2.line(face_landmarks2['right_eyebrow'], fill=(68, 54, 39, 150), width=5)

                    # Gloss the lips
                    d2.polygon(face_landmarks2['top_lip'], fill=(150, 0, 0, 128))
                    d2.polygon(face_landmarks2['bottom_lip'], fill=(150, 0, 0, 128))
                    d2.line(face_landmarks2['top_lip'], fill=(150, 0, 0, 64), width=8)
                    d2.line(face_landmarks2['bottom_lip'], fill=(150, 0, 0, 64), width=8)

                    # Sparkle the eyes
                    d2.polygon(face_landmarks2['left_eye'], fill=(255, 255, 255, 30))
                    d2.polygon(face_landmarks2['right_eye'], fill=(255, 255, 255, 30))

                    # Apply some eyeliner
                    d2.line(face_landmarks2['left_eye'] + [face_landmarks2['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
                    d2.line(face_landmarks2['right_eye'] + [face_landmarks2['right_eye'][0]], fill=(0, 0, 0, 110), width=6)
                pil_image2.save("output.png")
                current.comparison_photo = pygame.image.load("output.png")
        def capture(args):
            camera = cv2.VideoCapture(0)
            def thr():
                while True:
                    current.comparison_photo = None
                    if pygame.mouse.get_pressed()[2]:
                        break
                    ret, frame = camera.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame)
                    current.texture = GifProcesser.pil_to_game(pil_img)
                    current.raw = pil_img
                pil_img.save("photo.png")
                current.filepath = "photo.png"
                return
            t = threading.Thread(target=thr)
            t.start()
            return
        self.button_textures = [[pygame.image.load("Assets\\Images\\UI\\load.png")], [pygame.image.load("Assets\\Images\\UI\\save.png")], [pygame.image.load("Assets\\Images\\UI\\split.png")], [pygame.image.load("Assets\\Images\\UI\\compare.png")], [pygame.image.load("Assets\\Images\\UI\\loadc.png")],[pygame.image.load("Assets\\Images\\UI\\outline.png")],[pygame.image.load("Assets\\Images\\UI\\makeup.png")],[pygame.image.load("Assets\\Images\\UI\\reset.png")],[pygame.image.load("Assets\\Images\\UI\\camera.png")],[pygame.image.load("Assets\\Images\\UI\\exit.png")]];
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
        self.button_functions = [load_image, save, identify_face, compare, load_compare, outline_features, add_makeup,reset, capture,ex];
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
win = pygame.Surface((1366*scale["w"], 768*scale["h"]))
current = CurrentImage(pygame.Surface((10, 10)), [[200, 50], win]);
Interface = interface();
delay = 0;
frame = -1;
form_init();
global drop
drop = DropDown("Save as", formats, [150, 50])
clock = pygame.time.Clock();
original_bg = pygame.image.load("background.png")
bg = pygame.transform.scale(original_bg, (1366*scale["w"], 768*scale["h"]))
while True:
    win.fill((0, 0, 0));
    win.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit();
    Interface.update();
    pygame.display.set_mode((win.get_width(), win.get_height())).blit(win, (0, 0))
    pygame.display.update();