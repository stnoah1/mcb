import glob
import os
from os.path import join

import numpy as np
from scipy.misc import imread, imsave, imresize
from tqdm import tqdm


# todo: bugfix => some images are not printed.

imgroot = 'obj_img'
_saveroot = 'imgdump'

if not os.path.isdir(_saveroot):
    os.makedirs(_saveroot)

for nameclass in tqdm(os.listdir('labeled')):
    # For square
    objs = glob.glob(f'labeled/{nameclass}/*.obj')
    nums = len(objs)
    if not nums == 0:
        rows = int(np.ceil(np.log2(nums)))
        if rows == 0:
            rows = 1

        imrows = []
        Refresh = True
        for idx, obj in enumerate(objs):
            imgpath = join(imgroot, os.path.basename(obj).replace('.obj', '.png'))
            if idx == 0 or Refresh:
                img = imread(imgpath)
                img = imresize(img, (128, 128))
                Refresh = False
            else:
                tmp = imread(imgpath)
                tmp = imresize(tmp, (128, 128))
                img = np.concatenate([img, tmp], axis=1)

            if idx % rows == 0 and not idx == 0:
                imrows.append(img)
                Refresh = True

        for idx, tmp in enumerate(imrows):
            if idx == 0:
                img = tmp
                ref = img.shape
            else:
                h, w, c = tmp.shape
                if ref[1] != w:
                    tmp = np.concatenate([tmp, np.ones([h, ref[1] - w, c]) * 255], axis=1)

                img = np.concatenate([img, tmp], axis=0)

        savepath = join(_saveroot, nameclass + '.png')
        imsave(savepath, img)
