from PIL import Image, ImageOps # Python Imaging Library
import numpy as np # Numpy for numerical operations
import os # For path handling
import glob # For file handling
from scipy import spatial # For KDTree
import random
import pickle

class Mosaic:
    """ Class for photomosaic building
    Contruct a mosaic objet
    1- Use process_dataset() to treat and compute criteria from the dataset
    2- Use build_mosaic() to perform matching with the image in input
        and the processed dataset, then build and write a mosaic image
    """

    def __init__(self, image_in_location: str, image_out_location: str, \
                dataset_location: str,\
                fast: bool = False, auto_resize: bool = True,\
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
        self.images = None
        self.tree = None
        self.fast = fast
        self.auto_resize = auto_resize

        self.image_in = self.load_image(image_in_location)
        self.height = self.image_in.shape[0]
        self.width = self.image_in.shape[1]
        
        if (self.auto_resize):
            self.compute_targeted_resolution()
        ## Create a mosaic template 
        self.mosaic_template = \
        self.image_in[:: round(self.height / self.target_res[0]), \
        :: round(self.width / self.target_res[1])]
        
    
    def compute_targeted_resolution(self):
        """ Compute target res from a give target res height """
        
        target_res_h = self.target_res[0]
        target_res_w = (self.height * self.target_res[0]) // self.width
        self.target_res = (target_res_w, target_res_h)

    def load_image(self, source: str) -> np.ndarray:
        ''' Opens an image from specified source and 
        returns a numpy array with image rgb data 
        '''

        with Image.open(source) as source:
            array = np.asarray(source)
        return array


    def resize_image(self, image: Image, size: tuple) -> np.ndarray:
        '''Takes an image and resizes to a given size (width, height) 
        as passed to the size parameter 
        '''
        
        resized_image = ImageOps.fit(image, size, Image.LANCZOS, \
            centering=(0.5, 0.5))
        return np.array(resized_image)


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


    def fitness(self, image_A, image_B):
        return np.sum(image_A - image_B)

    def global_fitness(self, index_array):
        global_fitness = 0

        for i in range(self.target_res[0]):
            for j in range(self.target_res[1]):
                global_fitness += fitness(self.mosaic_template[i, j], self.images[index_array[i*self.target_res[1] + j]])
    
    def random_based_matching(self):
        """ Implement this matching algorithm -> 
        H. Narasimhan and S. Satheesh, 
        "A randomized iterative improvement algorithm for photomosaic generation," 
        2009 World Congress on Nature & Biologically Inspired Computing (NaBIC), 
        Coimbatore, India, 2009, pp. 777-781, 
        doi: 10.1109/NABIC.2009.5393882.
        """
        rng = numpy.random.default_rng()

        full_size = self.target_res[0] * self.target_res[1]
        index_array = np.arange(full_size, dtype=np.uint32) 
        np.random.shuffle(index_array)

        best_index = index_array

        fitness_best_index = global_fitness(best_index)

        while(fitness_best_index > 10000):
            neighbor = index_array
            random_tile_idx = rng.integers(full_size)


    def match_fast(self, i: int, j: int, template: list):
        """ Fast match but tile can repeat"""
    
        match = self.tree.query(template, p=1, k=40)

        pick = random.randint(0, 39)
        self.image_index[i, j] = match[1][pick]

    
    def match_slow(self, i: int, j: int, template: list, flag: np.ndarray):
        """ Slow match but tile can't repeat """
        
        found = False
        depth = 2  ## Depht of the search
        cnt = 0 ## Counter for the search
        
        while not found:
            match = self.tree.query(template, p=1, k=depth)
            
            for k in range(cnt, depth):
                ## If the image is not already used
                ## use it and break the loop
                if(not flag[match[1][k]]):
                    flag[match[1][k]] = 1
                    self.image_index[i, j] = match[1][k]
                    found = True
                    k = depth
            cnt = depth
            depth += 1


    def match_blocks(self):
        """Perform a matching"""

        ## Create an empty array to store the index of the image 
        # to use for each pixel in the mosaic.
        self.image_index = np.zeros(self.target_res, dtype=np.uint32) 

        flag = np.zeros(self.images.shape[0])
        print(self.images.shape)

        ## For each pixel in the mosaic template, 
        # find the closest match in the dataset and store the index
        for i in range(self.target_res[0]):
            for j in range(self.target_res[1]):
                
                template = self.mosaic_template[i, j]
                
                # Ensure template is of length 3 (RGB) and not 4 (RGBA)
                if len(template) == 4:
                    template = template[:3]
                
                if (self.fast):
                    self.match_fast(i, j, template)                
                else:
                    self.match_slow(i, j, template, flag)
                    
        
    def build_mosaic(self):
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
        self.image_out = Image.new('RGB', \
                (self.mosaic_size[1] * self.target_res[1], \
                self.mosaic_size[0] * self.target_res[0]))

       ## For each pixel in the mosaic, 
       # paste the corresponding image from the dataset
        for i in range(self.target_res[0]):
            for j in range(self.target_res[1]):
                tile = self.images[self.image_index[i, j]]
                x, y = j * self.mosaic_size[1], i * self.mosaic_size[0]
                image = Image.fromarray(tile)
                self.image_out.paste(image, (x,y))

        ## Write image in output
        self.image_out.save(self.image_out_location)   

