# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 19:48:21 2021

@author: 11453
"""

import torch
import torchvision
import os
import h5py
import numpy as np
from clip import clip
from PIL import Image


# load clip model
model, preprocess = clip.load('ViT-B/32',device="cpu",jit=False)

h5_path = "dataset1.h5"

def get_feature(image_input):
    with torch.no_grad():
        image_features = model.encode_image(image_input)
    image_features /= image_features.norm(dim=-1, keepdim=True).numpy()
    return image_features


def main(root_path):
    
    features = None
    names = []
    for file_list in os.listdir(root_path):
        file_list = root_path + '/' + file_list
        for filename in os.listdir(file_list):
            try:
                filename = file_list + '/' + filename
                print(filename)
                image_input = preprocess(Image.open(filename)).unsqueeze(0)
                image_feature = get_feature(image_input)
                names.append(filename)
                if features is None:
                    features = image_feature
                else:
                    features = np.vstack((features,image_feature))
            except:
                pass
    
    
    print(len(names))
    print(names)
    print(np.string_(names))
    # resize dataset
    f = h5py.File(h5_path,'a')
    now_feature_length = len(f['feature'][:])
    new_feature_length = len(features)
    index = now_feature_length + new_feature_length
    f['feature'].resize((index,512))
    f['filename'].resize((index,))
    
    # add to dataset
    f['feature'][now_feature_length:index] = features
    f['filename'][now_feature_length:index] = np.string_(names)
    f.close()
    
    '''
    feature_num = features.shape[0]
    print(feature_num)
    f = h5py.File(h5_path,'a')
    f.create_dataset("feature", [feature_num,512], maxshape=[None,512], chunks=True, data=features)
    f.create_dataset("filename", [feature_num], maxshape=[None], chunks=True, data=np.string_(names))
    '''
    
    '''
    #create dataset
    test = "../data/CUHK/cam_a/000_45.bmp"
    image_input = preprocess(Image.open(test)).unsqueeze(0)
    image_feature = get_feature(image_input)
    
    feature_list = np.array(image_feature)
    feature_num = feature_list.shape[0]
    print(feature_num)
    f = h5py.File(h5_path,'a')
    f.create_dataset("feature", [feature_num,512], maxshape=[None,512], chunks=True, data=feature_list)
    f.create_dataset("filename", [feature_num], maxshape=[None], chunks=True, data=np.string_(test))
    '''


if __name__=="__main__":
    root_path = "../data/CUHK"
    main(root_path)