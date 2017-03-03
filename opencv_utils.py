'''
Utilities module for video operations and image conversions 

@author: Sunil Mallya
'''

import cv2
import os
from PIL import Image

def get_frame_rate(video):
    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
     
    if int(major_ver)  < 3 :
        fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        fps = video.get(cv2.CAP_PROP_FPS)
    print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)

    return fps

def get_all_frames(video, path_output_dir):
    vidcap = cv2.VideoCapture(video)
    count = 0
    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            cv2_im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            count += 1
        else:
            break
    cv2.destroyAllWindows()
    vidcap.release()

def get_frames_every_x_sec(video, secs=1, fmt='opencv'):
    vidcap = cv2.VideoCapture(video)
    fps = get_frame_rate(vidcap)
    inc = int(fps * secs)
    length = int(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    count = 0
    while vidcap.isOpened() and count <= length:
        if count % inc == 0:
            success, image = vidcap.read()
            if success:
                cv2_im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                if fmt == 'PIL':
                    im = Image.fromarray(cv2_im)
                #elif fmt == 'DISK':
                    #cv2.imwrite(os.path.join(path_output_dir, '%d.png') % count, image)
                else:
                    im = cv2_im
                yield count, im 
            else:
                break
        count += 1
    cv2.destroyAllWindows()
    vidcap.release()

# image region: img = img[c1:c1+25,r1:r1+25] # roi = gray[y1:y2, x1:x2]

def write_labels(video, label_dict, secs=1):
    cap = cv2.VideoCapture(video)
    w=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH ))
    h=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT ))
    out = cv2.VideoWriter('output.mp4', -1, 20.0, (w,h))

    f_no = 0
    fps = get_frame_rate(cap)
    inc = int(fps * secs)
   
    f_nos = label_dict.keys()
    lbl = ''
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            if f_no in f_nos:
                try:
                    lbls = label_dict[f_no]
                    lbl = ",".join(lbls.keys())
                except:
                    pass

            cv2.putText(frame,lbl,(105, 105),cv2.FONT_HERSHEY_COMPLEX_SMALL,2,(0,0,255))
            #out.write(frame)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
        #inc
        f_no += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()

#if __name__ == '__main__' :
#    get_frames_every_x_sec('video.mp4', '.')
