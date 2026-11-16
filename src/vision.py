"""Traitements classiques, géométrie et normalisation OCR."""
import re
import cv2
import numpy as np

def preprocess(image):
    if image is None or image.size==0: raise ValueError('Image vide')
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) if image.ndim==3 else image.copy()
    denoise=cv2.bilateralFilter(gray,7,50,50)
    contrast=cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(denoise)
    _,binary=cv2.threshold(contrast,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    edges=cv2.Canny(denoise,60,150)
    contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    regions=[cv2.boundingRect(c) for c in contours if cv2.contourArea(c)>=30]
    return dict(gray=gray,denoise=denoise,contrast=contrast,binary=binary,edges=edges,
                histogram=cv2.calcHist([gray],[0],None,[256],[0,256]).ravel(),regions=regions)

def crop(image,box,pad=.04):
    h,w=image.shape[:2]; x1,y1,x2,y2=map(float,box); dx=(x2-x1)*pad; dy=(y2-y1)*pad
    x1,y1=max(0,int(x1-dx)),max(0,int(y1-dy)); x2,y2=min(w,int(np.ceil(x2+dx))),min(h,int(np.ceil(y2+dy)))
    if x2<=x1 or y2<=y1: raise ValueError('ROI vide')
    return image[y1:y2,x1:x2].copy()

def route_candidates(text):
    # Préserve les lignes alphanumériques; aucune correction arbitraire O/0.
    return re.findall(r'(?<!\w)[A-Z]?\d{1,4}[A-Z]?(?!\w)',text.upper())

def edit_distance(a,b):
    prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        curr=[i]
        for j,y in enumerate(b,1): curr.append(min(curr[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=curr
    return prev[-1]
