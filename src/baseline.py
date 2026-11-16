"""Classification de ROI annotées: HOG + SVM, sans localisation automatique."""
import json,time
from pathlib import Path
import cv2,numpy as np,joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score,f1_score,confusion_matrix,classification_report
from src.vision import crop
from src.pipeline import ROOT

def features(image):
    gray=cv2.cvtColor(cv2.resize(image,(64,64)),cv2.COLOR_BGR2GRAY)
    return cv2.HOGDescriptor((64,64),(16,16),(8,8),(8,8),9).compute(gray).ravel()

def load(split):
    X=[];y=[]
    for p in sorted((ROOT/f'data/transport/{split}/images').glob('*.jpg')):
        im=cv2.imread(str(p));h,w=im.shape[:2]
        for line in (p.parent.parent/'labels'/f'{p.stem}.txt').read_text().splitlines():
            if not line.strip():continue
            c,x,yy,bw,bh=map(float,line.split())
            roi=crop(im,[(x-bw/2)*w,(yy-bh/2)*h,(x+bw/2)*w,(yy+bh/2)*h],pad=0)
            X.append(features(roi));y.append(int(c))
    return np.array(X),np.array(y)

if __name__=='__main__':
    start=time.perf_counter();X,y=load('train');V,vy=load('val');T,ty=load('test')
    scores=[];models=[]
    for c in [.01,.1,1]:
        model=make_pipeline(StandardScaler(),LinearSVC(C=c,random_state=42,max_iter=10000))
        model.fit(X,y);scores.append(f1_score(vy,model.predict(V),average='macro'));models.append(model)
    idx=int(np.argmax(scores));best=models[idx];pred=best.predict(T)
    joblib.dump(best,ROOT/'models/hog_svm.joblib')
    report=dict(protocol='Classification on ground-truth transport crops; not detection',train_n=len(y),val_n=len(vy),test_n=len(ty),
                selected_C=[.01,.1,1][idx],validation_macro_f1=scores,test_accuracy=accuracy_score(ty,pred),test_macro_f1=f1_score(ty,pred,average='macro'),
                confusion_matrix=confusion_matrix(ty,pred,labels=[0,1,2]).tolist(),class_order=['Bus','Metro','Tram'],
                classification_report=classification_report(ty,pred,labels=[0,1,2],target_names=['Bus','Metro','Tram'],output_dict=True,zero_division=0),seconds=time.perf_counter()-start)
    (ROOT/'results/baseline_metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
