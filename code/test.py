# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 11:02:17 2021

@author: 11453
"""

import h5py
import torch
import os
import faiss
from clip import clip
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# run redis
#r = redis.Redis(host='localhost',port=6379,db=0,password=123456)

# h5 dataset
h5_path = "dataset.h5"
dataset = h5py.File(h5_path,'r')
image_features = dataset['feature'][:]
filenames = dataset['filename'][:]
dataset.close()

get_image_num = 5

def main(model,device):
        
    text_data = "a person"
    # text data to torch.tensor
    text_inputs = torch.cat([clip.tokenize(str(text_data))]).to(device)
    # get text feature
    with torch.no_grad():
        text_features = model.encode_text(text_inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    # device cuda to cpu
    text_features = text_features.cpu().numpy().astype("float32")
    print(text_features.dtype)

    # Hash Image Retrieval
    dimension = 512
    #hash_search = faiss.IndexFlatL2(dimension)

    nlist = 100
    m = 8
    quantizer = faiss.IndexFlatL2(dimension)
    hash_search = faiss.IndexIVFPQ(quantizer,dimension,nlist,m,8,faiss.METRIC_INNER_PRODUCT)
    #hash_search = faiss.index_cpu_to_all_gpus(hash_search)
    print(faiss.get_num_gpus())
    hash_search.train(image_features)

    hash_search.add(image_features)
    # k nearest neighbors
    k = 20
    import time
    start = time.time()
    values,indices = hash_search.search(text_features,k)
    end = time.time()
    print(end-start)

    image_paths = filenames[indices]
    print(image_paths)
    print(values)
    '''
    # get similarity
     similarity = (100.0 * text_features @ image_features.T).softmax(dim=-1)
    # get top n similarity images index
    values, indices = similarity[0].topk(get_image_num)    
    # get image path by index
    image_paths = filenames[indices]
    
    print(image_paths)
    '''



if __name__ == '__main__':
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load('ViT-B/32',device=device,jit=False)
    main(model,device=device)