import pygame, json, webbrowser, time, random
from PIL import Image
import aspose.words as aw
class ImageEditor:
    def __init__(self):
        pass
    def scale_image(self, img, factor=4):
        size = round(img.get_width() * factor), round(img.get_height() * factor);
        return pygame.transform.scale(img, size);
    def save_image(self, img, filename):
        pygame.image.save(img, filename);
        return;
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
    def __init__(self):
        pass;
    def pil_to_game(self, img):
        data = img.tobytes("raw", "RGBA");
        return pygame.image.fromstring(data, img.size, "RGBA");
    def get_gif_frame(self, img, frame):
        img.seek(frame);
        return  img.convert("RGBA");
    
    def load_gif(self, gif, scale=1):
        current_frame1 = 0;
        cycles1 = 0;
        gif_img1 = Image.open(gif);
        output = [];
        for i in range(gif_img1.n_frames):
            cycles1+=1;
            if cycles1 == gif_img1.n_frames:
                    break;
            frame1 = self.scale_image(self.pil_to_game(self.get_gif_frame(gif_img1, current_frame1)), scale);
            output.append(frame1);
            current_frame1 = (current_frame1 + 1) % gif_img1.n_frames;
        return GIF(output);
    def crop_gif(self, gif, new_dimensions):
        for i in range(gif.num_frames):
            newframe = pygame.Surface(new_dimensions);
            newframe.blit(gif.frames[i], [0, 0]);
            gif.frames[i] = newframe;
    def swap_color_in_gif(self, gif, colors):
        for frame in gif.frames:
            pygame.transform.threshold(frame,frame,colors[0], (0,0,0,0), colors[1], 1, None, True);
    def split_gif_to_frames(self, gif):
        return gif.frames;
    def save_images_to_gif(self, images):     
        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        shapes = [builder.insert_image(fileName) for fileName in images]
        pageSetup = builder.page_setup
        pageSetup.page_width = max(shape.width for shape in shapes)
        pageSetup.page_height = sum(shape.height for shape in shapes)
        pageSetup.top_margin = 0
        pageSetup.left_margin = 0
        pageSetup.bottom_margin = 0
        pageSetup.right_margin = 0 
        doc.save("Output.gif")
win = pygame.display.set_mode((900, 900));
GIFprocessor = GifProcesser();
test_gif = GIFprocessor.load_gif("excited-animated-gif.gif");
while True:
    win.fill((0, 0, 0));
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit;
    test_gif.play([0, 0], win);
    pygame.display.update();