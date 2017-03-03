'''
Reference code to label images in a video with Amazon Rekognition

@author: Sunil Mallya

'''

import boto3
import json
import pickle
import io
import os
import opencv_utils

from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock

# Rekognition client
rekognition = boto3.client('rekognition', region_name='us-west-2')

# Globals 
d_index = {} # label dict index
label_counts = {} # label counts
lock = Lock()

# Extract features helper
def get_labels(params):
    '''
    image : bytearray
    '''
    f, image = params

    try:
        resp = rekognition.detect_labels(Image={'Bytes': image.getvalue()})
        labels = resp['Labels']
        
        dt = {}
        for v in labels:
            l = v['Name'].lower() 
            c = v['Confidence']
           
            #skip labels
            if l == "person":
                continue

            # Choose an appopriate confidence level based on your application
            if c < 60:
                continue
            
            # insert features
            dt[l] = c
            
            # count label freq for word cloud generation
            try:
                label_counts[l]
            except KeyError:
                label_counts[l] = 0
            label_counts[l] += 1

        lock.acquire()
        d_index[f] = dt
        lock.release()
    except Exception, e:
        print e
    
def generate_wordcloud():
    from wordcloud import WordCloud
    wordcloud = WordCloud(background_color="white")

    from operator import itemgetter
    item1 = itemgetter(1)
    frequencies = sorted(label_counts.items(), key=item1, reverse=True)
    wordcloud.generate_from_frequencies(frequencies)

    # save image
    import matplotlib.pyplot as plt
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig('photo_tags')

if __name__ == '__main__' :

    # sample video 

    video_file = 'video.mp4'
    frames = []
    for f_no, img in opencv_utils.get_frames_every_x_sec(video_file, secs=1, fmt="PIL"):
        b_img = io.BytesIO()
        img.save(b_img, format='PNG')
        frames.append([f_no, b_img]) 

    N_THREADS = 25 
    pool = ThreadPool(N_THREADS)
    results = pool.map(get_labels, frames)
    pool.close()
    pool.join()
    print "done"
    generate_wordcloud()

    # Play the video with labels annotated on the frame
    opencv_utils.write_labels(video_file, d_index)

