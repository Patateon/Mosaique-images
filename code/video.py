from PIL import Image, ImageOps # Python Imaging Library
import numpy as np # Numpy for numerical operations
import os # For path handling
import glob # For file handling
from scipy import spatial # For KDTree
import cv2 # For video handling
import random
import pickle

class Video:
    """ Class for videomosaic building
    Contruct a mosaic objet
    1- Use process_dataset() to treat and compute criteria from the dataset
    2- Use mosaic_frame() to perform matching with the image in input
        and the processed dataset, then build and write a mosaic image
    """

    def __init__(self, image_in_location: str, image_out_location: str, \
                dataset_location: str, auto_resize: bool = True,\
                target_res=(50, 50), mosaic_size=(32, 32)):
        """Initialize all parameters for mosaic building.
        image_in_location -> Path to the image in input.
        image_out_location -> Path to the mosaic in output.
        dataset_location -> Path to the dataset.
        target_res -> Number of blocks of the mosaic.
        mosaic_size -> Size of each tile.
        """

        self.image_in_location = image_in_location
        self.image_out_location = image_out_location
        self.dataset_location = dataset_location
        self.target_res = target_res
        self.mosaic_size = mosaic_size
        self.auto_resize = auto_resize
        self.images = None
        self.tree = None
        
        self.divide_video()
        
    
    def compute_targeted_resolution(self):
        """ Compute target res from a give target res height """
        
        #target_res_h = self.target_res[0]
        #target_res_w = (self.height * self.target_res[0]) // self.width
        #self.target_res = (target_res_w, target_res_h)

    def load_image(self, source: str) -> np.ndarray:
        ''' Opens an image from specified source and 
        returns a numpy array with image rgb data 
        '''

        with Image.open(source) as source:
            array = np.asarray(source)
        return array


    def load_cifar(self):
        """ Load cifat10 dataset in self.images attributs """

        for i in range(1, 6):   
            current_batch = os.path.join(self.dataset_location, "data_batch_{}".format(i))         
            with open(current_batch, 'rb') as fo:
                dict = pickle.load(fo, encoding='bytes')
                im_arr = np.moveaxis(dict[b'data'].reshape(10000, 3, 32, 32), 1, -1)
                if (i == 1):
                    self.images = im_arr
                else:
                    self.images = np.vstack((self.images, im_arr))

        current_batch = os.path.join(self.dataset_location, "test_batch")
        with open(current_batch, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
            im_arr = np.moveaxis(dict[b'data'].reshape(10000, 3, 32, 32), 1, -1)
            self.images = np.vstack((self.images, im_arr))


    def load_from_dir(self):
        """ Load every images from a folder, resize them and
        put them in self.images attributs

        ! Way slower than load_cifar
        """

        self.images = []
        for file in glob.glob(self.dataset_location):
            image = self.load_image(file)
            self.images.append(image)

        self.images = [i for i in self.images if i.ndim==3] ## Remove any non color images
        self.images = [self.resize_image(Image.fromarray(i), self.mosaic_size) \
            for i in self.images] ## Resize images to the tile size

        self.images = np.asarray(self.images)  


    def load_dataset(self):
        """Load dataset"""

        if(os.path.basename(self.dataset_location) == 'cifar-10-batches-py'):
            self.load_cifar()
        else:
            self.load_from_dir()


    def process_dataset(self):
        """Compute criteria for every image from the dataset
        Store thoses values in a KDTree
        """

        ## Load dataset
        self.load_dataset()

        ## Use mean as a criteria
        image_values = np.apply_over_axes(np.mean, self.images, [1, 2])\
            .reshape(self.images.shape[0], 3)

        ## Create a KDTree for the image values
        self.tree = spatial.KDTree(image_values)


    def match(self, i: int, j: int, template: list):
        """ Fast match but tile can repeat"""
    
        match = self.tree.query(template, p=1, k=40)

        ## pick = random.randint(0, 39)
        ## self.image_index[i, j] = match[1][pick]
        self.image_index[i, j] = match[1][0] ## Always pick the closest match


    def match_blocks(self):
        """Perform a matching"""

        ## Create an empty array to store the index of the image 
        # to use for each pixel in the mosaic.
        self.image_index = np.zeros(self.target_res, dtype=np.uint32) 

        ## For each pixel in the mosaic template, 
        # find the closest match in the dataset and store the index
        for i in range(self.target_res[0]):
            for j in range(self.target_res[1]):
                
                template = self.mosaic_template[i, j]
                
                # Ensure template is of length 3 (RGB) and not 4 (RGBA)
                if len(template) == 4:
                    template = template[:3]
                
                self.match(i, j, template)     
                
    def mosaic_frame(self):
        """Build mosaic"""

        if self.images is None:
            print("Need to load dataset")
            exit()

        if self.tree is None:
            print("Need to compute criteria")
            exit()

        ## Match tiles with images from the dataset
        self.match_blocks()

        ## Create a new image to store the final mosaic
        frame = Image.new('RGB', \
            (self.mosaic_size[1] * self.target_res[1], \
            self.mosaic_size[0] * self.target_res[0]))

       ## For each pixel in the mosaic, 
       # paste the corresponding image from the dataset
        for i in range(self.target_res[0]):
            for j in range(self.target_res[1]):
                tile = self.images[self.image_index[i, j]]
                x, y = j * self.mosaic_size[1], i * self.mosaic_size[0]
                image = Image.fromarray(tile)
                frame.paste(image, (x,y))
                
        return frame           
                    
    def divide_video(self):
        """Divide video into frames and store them in a numpy array"""
        
        # Get video properties
        cap = cv2.VideoCapture(self.image_in_location)
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Create buffer to store frames
        self.buffer = np.empty((self.frameCount, self.frameHeight, self.frameWidth, 3), np.dtype('uint8'))
        i = 0
        # Read every frames
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                self.buffer[i] = frame
                i += 1
            else:
                break
        cap.release()

    def build_mosaic(self):
        """Make a mosaic video from a video input"""
        
        # video output
        self.video_out = np.empty((self.frameCount, self.mosaic_size[0] * self.target_res[0], self.mosaic_size[1] * self.target_res[1], 3), np.dtype('uint8'))
        
        # For each frame in the video
        for i in range(self.frameCount):
            self.image_in = self.buffer[i]
            self.mosaic_template = \
            self.image_in[:: round(self.frameHeight // self.target_res[0]), \
            :: round(self.frameWidth // self.target_res[1])]
            frame = self.mosaic_frame() ## Build mosaic for the frame
            self.video_out[i] = frame ## Store the mosaic in the buffer
        
        ## Build video from frames
        self.build_video()
    
    def build_video(self):
        """Build video from frames"""
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.image_out_location, fourcc, self.fps, (self.mosaic_size[1] * self.target_res[1], self.mosaic_size[0] * self.target_res[0]))
        
        # Write every frame in the output video
        for i in range(self.frameCount):
            out.write(self.video_out[i])
                
        
        out.release()
        cv2.destroyAllWindows()

