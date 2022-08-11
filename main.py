import pygame, json, webbrowser, time, random
from tkinter import filedialog
from PIL import Image, ImageDraw
class ImageEditor:
    def scale_image(img, factor=4):
        size = round(img.get_width() * factor), round(img.get_height() * factor);
        return pygame.transform.scale(img, size);
    def save_image(img, filename):
        pygame.image.save(img, filename);
        return;
    def openFile():
        filepath = filedialog.askopenfilename(title="Open file")
        return filepath
class Img:
    def __init__(self, path):
        self.filepath = path;
class GIF:
    def __init__(self, frames):
        self.frames = frames;
        self.num_frames = len(frames);
    def play(self, position, screen):
        for frame in self.frames:
            win.fill((0, 0, 0));
            screen.blit(frame, position);
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
class Button:
    def __init__(self, position, textures, function, screen):
        self.textures = textures;
        self.onlick = function[0];
        self.args = function[1];
        self.pos = position;
        self.screen = screen;
        self.current = 0;
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);
    def update(self):
        self.current = 0;
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.onlick(self.args);
                self.current = 1;
        self.screen.blit(self.textures[self.current], self.pos)
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);
        
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN);
current_h_w = [win.get_width(), win.get_height()]
imag = [];
default_h_w = [1366, 768];
win = pygame.display.set_mode((400*current_h_w[0]/default_h_w[0], 600*current_h_w[1]/default_h_w[1]));
def test_function(ixy):
    print("clicked!");
for img_ in range(9):
    imag.append("frame_"+str(img_)+"_delay-0.06s.png");

GifProcesser.save_images_to_gif(imag, "output.gif", True);
test_gif = GifProcesser.load_gif(ImageEditor.openFile());
button_test = Button([270, 400], test_gif.frames, [test_function, 1], win)

while True:
    win.fill((0, 0, 0));
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit;
    button_test.update()
    pygame.display.update();