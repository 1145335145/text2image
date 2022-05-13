# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 11:02:17 2021

@author: 11453
"""
import redis
import PIL
import h5py
import base64
import torch
import numpy
import faiss
import os
from io import BytesIO
from clip import clip

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# run redis
r = redis.Redis(host='localhost',port=6379,db=0,password=123456)

device = "cuda" if torch.cuda.is_available() else "cpu"

# h5 dataset
h5_path = "dataset.h5"
dataset = h5py.File(h5_path,'r')
image_features = dataset['feature'][:]
filenames = dataset['filename'][:]
dataset.close()

# Hash Image Retrieval
'''
resources = faiss.StandardGpuResources()
dimension = 512
nlist = 10
m = 8
'''

dimension = 512
hash_search = faiss.IndexFlatL2(dimension)
hash_search.add(image_features)
'''
flat_config = faiss.GpuIndexIVFPQConfig()
flat_config.device = 1
hash_search = faiss.GpuIndexIVFPQ(resources, dimension, nlist, m, 8, faiss.METRIC_L2, flat_config)
print("training...")
hash_search.train(image_features)
print("training end")
'''

'''
flat_config = faiss.GpuIndexFlatConfig()
flat_config.device = 1
hash_search = faiss.GpuIndexFlatL2(resources,dimension,flat_config)
hash_search.add(image_features)
'''
# k nearest neighbors
k = 20

print("start")

def main(model):
    while 1:
        # listening port and pop first data
        task_id_meta = r.blpop('taskQueue', timeout=100)
        if task_id_meta:
            import time
            start = time.time()
            # get redis task id 
            task_id = task_id_meta[1]
            task_id = str(task_id, encoding = "utf-8")

            text_data = r.hget('processHashPoll',task_id)
            
            # text data to torch.tensor
            text_inputs = torch.cat([clip.tokenize(str(text_data))]).to(device)
            # get text feature
            with torch.no_grad():
                s1 = time.time()
                text_features = model.encode_text(text_inputs)
                e1 = time.time()
                print(e1-s1)
                text_features /= text_features.norm(dim=-1, keepdim=True)
            # device cuda to cpu
            text_features = text_features.cpu().numpy().astype("float32")
            s = time.time()
            values, indices = hash_search.search(text_features, k)
            e = time.time()
            print(e-s)
            
            image_paths = filenames[indices][0]
            values = values[0]
            print(image_paths)
            print(values)
            # redis得到返回数据
            for i in range(k):
                r.lpush("result_list_"+str(task_id),str(image_paths[i]) + "***" + str(values[i]))
                #r.lpush("result_list_" + str(task_id), image_paths[i])
            

            end = time.time()
            print(end-start)


if __name__ == '__main__':
    model, preprocess = clip.load('./ViT-B/32',device=device,jit=False)
    main(model)