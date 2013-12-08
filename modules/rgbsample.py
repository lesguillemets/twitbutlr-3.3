#!/usr/bin/env python3

import os
import numpy as np
import PIL.Image as Image

pwd = os.path.dirname(__file__)
tmpfilename = os.path.join(pwd, '..', 'tmp', 'rgbsample.png') 

N = 300 # returns image of N*N pixels.


def make_rgb_sample(r,g,b):
    imga = np.array([(r,g,b) for i in range(N*N)], dtype=np.uint8).reshape(N,N,-1)
    img = Image.fromarray(imga)
    img.save(tmpfilename)
    return os.path.abspath(tmpfilename)

