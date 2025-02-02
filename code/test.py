# Standard lib
import os # For path handling
import time # For timing

# Personal lib
from mosaic import *
from video import *

CWD = os.getcwd()

image_in_location = os.path.join(CWD, 'images_test', 'VidTest.mp4')
image_out_location = os.path.join(CWD, 'images_test', 'VidResult.mp4')
dataset_location = os.path.join(CWD, 'dataset', \
    'DIV2K_train_LR_bicubic', 'X2', '*')

dataset_location = os.path.join(CWD, 'dataset', \
    'cifar-10-batches-py')

video = Video(image_in_location, image_out_location, dataset_location)

start_time = time.time()
print('Starting...')
print('Loading images...')

video.process_dataset()

print('Finding matches...')

video.build_mosaic()

print('Mosaic created')
print('Time taken:', round(time.time()-start_time, 2), "seconds")