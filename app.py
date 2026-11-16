"""Application locale. Lancer : python -m streamlit run app.py"""
import json
import hashlib
import cv2
import numpy as np
import streamlit as st
from src.pipeline import Pipeline
from src.vision import preprocess
st.set_page_config(page_title='Projet 9 - Transports',layout='wide')
st.title('Reconnaissance des transports publics')
st.write('Bus, métro, tramway, panneaux de ligne et arrêts. Prototype universitaire.')
st.info('Les lectures peuvent être incorrectes. Un arrêt détecté ne fournit pas une position ni un nom certifié.')
@st.cache_resource
def load(ocr): return Pipeline(ocr)
ocr=st.checkbox('Lire les textes avec OCR',value=True)
threshold=st.slider('Seuil de confiance de détection',.05,.95,.25,.05)
mode=st.radio('Image à analyser',['Importer une image','Exemple fourni'])
raw=None
if mode=='Importer une image':
    file=st.file_uploader('Image JPG ou PNG',type=['jpg','jpeg','png'])
    if file: raw=file.getvalue()
else:
    from pathlib import Path
    examples=sorted((Path(__file__).parent/'examples').glob('*.jpg'))
    if examples:
        chosen=st.selectbox('Exemple',examples,format_func=lambda p:p.name);raw=chosen.read_bytes()
if raw:
    im=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
    if im is None: st.error('Impossible de lire cette image.')
    else:
        analysis_key=(hashlib.sha256(raw).hexdigest(),ocr,threshold)
        analyse=st.button('Analyser',type='primary')
        try:
            if analyse:
                with st.spinner('Analyse en cours…'): result,annotated=load(ocr).predict(im,threshold)
                st.session_state['analysis']=(analysis_key,result,annotated)
            saved=st.session_state.get('analysis')
            if saved and saved[0]==analysis_key:
                _,result,annotated=saved
                st.image(cv2.cvtColor(annotated,cv2.COLOR_BGR2RGB),caption='Détections du système')
                st.write(f"Durée mesurée : {result['seconds']:.2f} s (hors chargement des modèles)")
                if not result['detections']: st.warning('Aucun objet détecté au seuil choisi.')
                for d in result['detections']:
                    st.write(f"{d['label']} : {d['confidence']:.2f}")
                    if d['route_candidates']: st.write('Lignes candidates : '+', '.join(d['route_candidates']))
                    if d['text']: st.write('Texte OCR : '+' / '.join(t['text'] for t in d['text']))
                st.download_button('Télécharger les résultats JSON',json.dumps(result,indent=2,ensure_ascii=False),'resultats.json','application/json')
                with st.expander('Traitements OpenCV'):
                    pp=preprocess(im)
                    for k in ['gray','denoise','contrast','binary','edges']: st.image(pp[k],caption=k)
                    st.bar_chart(pp['histogram'])
        except Exception as e: st.error(f'Analyse impossible : {e}. Vérifiez les modèles et le README.')
