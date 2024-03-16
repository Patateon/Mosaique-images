from PIL import Image, ImageOps # Python Imaging Library
import numpy as np # Numpy for numerical operations
import glob # For file handling
from scipy import spatial # For KDTree
import random
import time # For timing

def load_image(source : str) -> np.ndarray:
    ''' Opens an image from specified source and returns a numpy array with image rgb data '''
    with Image.open(source) as source:
        array = np.asarray(source)
    return array

def resize_image(img : Image, size : tuple) -> np.ndarray:
    '''Takes an image and resizes to a given size (width, height) as passed to the size parameter '''
    
    resz_img = ImageOps.fit(img, size, Image.LANCZOS, centering=(0.5, 0.5))
    return np.array(resz_img)

start_time = time.time()
print('Starting...')
ImgIn = load_image('./ImgTest.jpg')

width = ImgIn.shape[0]
height = ImgIn.shape[1]

target_res = (100, 100) ## Number of images to make up final image (width, height)

mos_template = ImgIn[::(height//target_res[0]),::(height//target_res[1])] ## Create a mosaic template
mos_template[:,:, -1].size ## Number of pixels in the mosaic template

images = []

print('Loading images...')
## Load images from the dataset as numpy arrays
for file in glob.glob('./dataset/DIV2K_train_LR_bicubic/X2/*'):
    im = load_image(file)
    images.append(im)
    
images = [i for i in images if i.ndim==3] ## Remove any images that are not RGB

mosaic_size = (40, 40) ## Defines size of each mosiac image
images = [resize_image(Image.fromarray(i), mosaic_size) for i in images]
images_array = np.asarray(images)
images_array.shape
image_values = np.apply_over_axes(np.mean, images_array, [1,2]).reshape(len(images),3) ## Calculate the mean of each image and reshape to 3D array
tree = spatial.KDTree(image_values) ## Create a KDTree for the image values

image_idx = np.zeros(target_res, dtype=np.uint32) ## Create an empty array to store the index of the image to use for each pixel in the mosaic

print('Finding matches...')
## For each pixel in the mosaic template, find the closest match in the dataset and store the index
for i in range(target_res[0]):
    for j in range(target_res[1]):
        
        template = mos_template[i, j]
        
        match = tree.query(template, k=40)
        pick = random.randint(0, 39)
        image_idx[i, j] = match[1][pick]
        
        
ImgOut = Image.new('RGB', (mosaic_size[0]*target_res[0], mosaic_size[1]*target_res[1])) ## Create a new image to store the final mosaic

print('Creating mosaic...')
## For each pixel in the mosaic, paste the corresponding image from the dataset
for i in range(target_res[0]):
    for j in range(target_res[1]):
        arr = images[image_idx[j, i]]
        x, y = i*mosaic_size[0], j*mosaic_size[1]
        im = Image.fromarray(arr)
        ImgOut.paste(im, (x,y))
        
ImgOut.save('./result.jpg')

print('Mosaic created')
print('Time taken:', round(time.time()-start_time, 2), "seconds")