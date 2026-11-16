import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve('.');
process.env.RUNTIME_NODE_MODULES ??= path.join(workspaceDir,'work/node_modules');
const root=path.join(workspaceDir,'outputs/Projet9');
const SKILL_DIR='C:/Users/ayoub/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const RUNTIME_PYTHON='C:/Users/ayoub/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const read=async p=>JSON.parse(await fs.readFile(path.join(root,p),'utf8'));
const audit=await read('data/audit.json'),baseline=await read('results/baseline_metrics.json'),ocr=await read('results/ocr_metrics.json'),e2e=await read('results/pipeline_metrics.json');
const metrics={};for(const t of ['transport','route','stop'])metrics[t]=await read(`results/${t}_metrics.json`);
const pct=x=>(100*x).toFixed(1).replace('.',',')+' %';
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const navy='#142D42',teal='#007E83',gray='#455B6C';
let sn=0;
function text(s,txt,x,y,w,h,size=28,color=navy,bold=false){let q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=txt;q.text.style={fontFamily:'Arial',fontSize:size,color,bold};return q;}
function slide(title,notes=''){let s=pres.slides.add();s.background.fill='#FFFFFF';sn++;text(s,title,64,48,1150,112,44,navy,true);text(s,'PROJET 9   /   16 NOVEMBRE 2026',64,675,1000,25,16,gray);text(s,String(sn).padStart(2,'0'),1160,670,60,30,20,gray);s.speakerNotes.text=notes;return s;}
function para(s,lines,x=64,y=195,w=1100,size=29,gap=110){lines.forEach((t,i)=>text(s,t,x,y+i*gap,w,gap-15,size));}
async function image(s,p,x,y,w,h){s.images.add({blob:new Uint8Array(await fs.readFile(path.join(root,p))),contentType:p.endsWith('.png')?'image/png':'image/jpeg',fit:'contain',alt:p,position:{left:x,top:y,width:w,height:h}});}
function table(s,values,y=215,widths=null){const w=1152;let t=s.tables.add({rows:values.length,columns:values[0].length,left:64,top:y,width:w,height:values.length*65,values,columnWidths:widths??Array(values[0].length).fill(w/values[0].length)});t.borders.assign({style:'solid',fill:'#D6E0E5',width:1});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){const cell=t.getCell(r,c);cell.fill=r===0?navy:r%2?'#F1F5F7':'#FFFFFF';cell.text.style={fontFamily:'Arial',fontSize:25,color:r===0?'#FFFFFF':navy,bold:r===0};}return t;}

let s=slide('Reconnaissance des\nmoyens de transport','Introduction, 45 secondes. Présenter le contexte d’inclusion du cahier des charges, puis annoncer que les résultats sont mesurés sur les données fournies. Ajouter oralement les noms et contributions réelles du groupe. Source : docs/cahier_des_charges.pdf.');
s.background.fill=navy; s.shapes.items[0].text.style={fontFamily:'Arial',fontSize:55,bold:true,color:'#FFFFFF'};
s.shapes.items[0].position={left:64,top:48,width:1150,height:150};
s.shapes.items[1].text.style={fontFamily:'Arial',fontSize:16,color:'#C9DEE8'};
s.shapes.items[2].text.style={fontFamily:'Arial',fontSize:20,color:'#C9DEE8'};
text(s,'Véhicules, numéros de ligne\net informations d’arrêt',64,240,530,140,32,'#FFFFFF');
text(s,'Prototype universitaire\nPython et OpenCV',64,455,530,100,25,'#C9DEE8');
await image(s,'examples/transport.jpg',650,210,560,390);

s=slide('Objectifs et périmètre','45 secondes. Les sept exigences du professeur sont couvertes par les modules, mais identifier un arrêt au sens de sa catégorie ne fournit pas son nom. Source : cahier des charges et README.');
para(s,['Reconnaître bus, métro et tramway dans une image.','Repérer les afficheurs de ligne et tenter de lire leur texte.','Détecter les arrêts et restituer les informations visibles.','Évaluer les erreurs et proposer une application locale.'],64,190,1100,29,105);

s=slide('Les trois jeux de données','60 secondes. Source : data/audit.json. Les proportions portent sur des groupes de sources et non sur le nombre d’images. Les 725 images sont fournies avec le dossier technique. Provenance : docs/SOURCES.md et data_raw/*/data.yaml.');
table(s,[['Dataset','Images','Train','Validation','Test'],...Object.entries(audit).map(([t,a])=>[t==='transport'?'Public Transport':t==='route'?'Bus Route Number':'BusStop',a.images,a.splits.train.images,a.splits.val.images,a.splits.test.images])],210,[392,190,190,190,190]);
text(s,'Aucune transcription exhaustive des lignes ou des noms d’arrêt.',64,525,1140,80,28,gray);

s=slide('Une séparation par image source','60 secondes. Les noms avant .rf. et les empreintes de pixels servent au regroupement. Des scènes proches peuvent néanmoins porter d’autres noms. Ne pas présenter les groupes comme des scènes indépendantes. Sources : src/prepare.py, manifestes et tests.');
text(s,'725',64,200,330,100,78,teal,true);text(s,'images contrôlées',64,315,360,50,27);
text(s,'239',480,200,330,100,78,teal,true);text(s,'polygones convertis',480,315,360,50,27);
text(s,'0',895,200,200,100,78,teal,true);text(s,'groupe partagé\nentre les lots',895,315,330,100,27);
text(s,'Même source et variantes dans le même lot.\nSeed 42, stratification par classes, manifestes conservés.',64,490,1120,110,30);

s=slide('Traitements classiques avec OpenCV','60 secondes. Montrer que la binarisation et les contours fournissent des régions candidates, sans reconnaître leur classe. Les images montrent le premier exemple de transport, avec Canny. Source : src/vision.py et results/demo.');
await image(s,'results/demo/transport_gray.png',64,190,540,300);await image(s,'results/demo/transport_edges.png',660,190,540,300);
text(s,'Niveaux de gris et filtrage',64,510,540,50,28);text(s,'Contours Canny',660,510,540,50,28);
text(s,'Histogramme, filtre bilatéral, CLAHE, Otsu et régions de contours.',64,585,1135,50,25,gray);

s=slide('Détection et lecture des régions','60 secondes. Trois détecteurs distincts car les annotations sont incomplètes pour les autres tâches dans chaque dataset. L’OCR est préentraîné et n’est pas réentraîné ici. Sources : src/pipeline.py ; https://docs.ultralytics.com/modes/train/ ; https://www.jaided.ai/easyocr/documentation/.');
para(s,['01   Image entière : trois détecteurs YOLOv8n spécialisés.','02   Boîtes prédites : classe, position et score de détection.','03   ROI des afficheurs et arrêts : contraste puis OCR.','04   Sortie : objets, textes bruts et lignes candidates.'],64,190,1130,29,105);

s=slide('Référence HOG et SVM','60 secondes. Source : results/baseline_metrics.json. Attention : classification sur boîtes vérité terrain, pas localisation automatique. 111 ROI train, 25 validation, 31 test. C=0,01 choisi sur validation. Les lignes du tableau sont les classes réelles.');
text(s,pct(baseline.test_accuracy),64,170,480,100,70,teal,true);text(s,'Exactitude sur 31 véhicules recadrés',64,285,1100,55,30);
table(s,[['Réel / prédit','Bus','Metro','Tram'],...baseline.class_order.map((n,i)=>[n,...baseline.confusion_matrix[i]])],370,[432,240,240,240]);

s=slide('Entraînement effectivement exécuté','60 secondes. Sources : results/environment.json, results/*_metrics.json, args.yaml et results.csv. Le meilleur modèle dépend de validation. Le test n’est pas utilisé pour choisir le checkpoint. Expliquer le budget CPU et ne pas prétendre à une convergence exhaustive.');
para(s,['YOLOv8n préentraîné, puis adaptation à chaque dataset.',`${metrics.transport.epochs_completed} époques transport, ${metrics.route.epochs_completed} panneaux et ${metrics.stop.epochs_completed} arrêts.`, 'CPU, images 320 px, batch 8, seed 42.', 'Meilleur checkpoint sur validation, puis mesure sur test.'],64,190,1120,29,105);

s=slide('Résultats de détection sur test','75 secondes. Sources : results/transport_metrics.json, route_metrics.json et stop_metrics.json. mAP50-95 moyenne les seuils IoU de 0,50 à 0,95. Les mAP ne sont pas des exactitudes par image. Les jeux de test sont petits et hétérogènes.');
table(s,[['Détecteur','Images test','mAP50','mAP50-95'],...Object.entries(metrics).map(([t,m])=>[t,audit[t].splits.test.images,pct(m.test_metrics['metrics/mAP50(B)']),pct(m.test_metrics['metrics/mAP50-95(B)'])])],215,[360,240,276,276]);
text(s,'Mesures sur les partitions livrées.\nLa généralisation à un réseau local reste à vérifier.',64,530,1130,90,28,gray);

s=slide('Lecture OCR sur des panneaux connus','75 secondes. Huit ROI lisibles, neuf exclues sur dix-sept régions examinées. Une image par groupe de source. Les transcriptions ont été établies visuellement avant OCR. Ce petit sous-ensemble ne représente pas tous les panneaux. Sources : examples/ocr_rois/annotations.json et results/ocr_metrics.json.');
text(s,'5 / 8',64,180,430,100,76,teal,true);text(s,'lectures exactes',64,295,450,60,32);
text(s,'CER : '+pct(ocr.CER),64,390,500,70,32);text(s,'Recadrages annotés fournis à l’OCR.\nNeuf régions ambiguës exclues.',64,490,565,110,27,gray);
await image(s,'examples/ocr_rois/03.jpg',700,195,220,230);await image(s,'examples/ocr_rois/08.jpg',970,195,220,230);
text(s,'505 : succès',700,450,250,55,27,teal);text(s,'516 : échec',970,450,250,55,27,'#A24B25');

s=slide('Lecture après détection automatique','60 secondes. Source : results/pipeline_metrics.json. Sous-ensemble de huit panneaux lisibles positifs, seuil de détection 0,25, IoU minimal 0,5. La première ligne candidate doit être exactement correcte. Ce n’est pas un taux global de fiabilité ni une mesure de faux positifs.');
text(s,`${e2e.localized} / ${e2e.n}`,64,190,420,90,66,teal,true);text(s,'panneaux localisés',64,285,490,65,29);
text(s,`${e2e.correct} / ${e2e.n}`,64,390,420,90,66,teal,true);text(s,'lignes exactement lues',64,485,520,65,29);
await image(s,'results/demo/route_readable_prediction.jpg',635,190,570,360);
text(s,'Évaluation exploratoire sur des cas lisibles.',635,575,570,65,24,gray);

s=slide('Arrêts et informations associées','45 secondes. Source : dataset BusStop, src/pipeline.py et results/demo. Les annotations génériques ne contiennent ni nom ni coordonnées. Même si un texte est lu, le programme ne certifie pas l’identité d’un arrêt.');
await image(s,'results/demo/stop_prediction.jpg',64,190,580,380);
para(s,['Détection de la catégorie bus-stop.','Lecture du texte visible si possible.','Nom et position non certifiés.'],700,205,510,30,125);

s=slide('Démonstration de l’application','Démonstration, 2 minutes. Dans Projet9 : python -m streamlit run app.py --server.address 127.0.0.1. Choisir Exemple fourni, route_readable.jpg, puis Analyser. Lire le texte brut et la ligne candidate sans cacher un échec. Ouvrir les traitements OpenCV. Comparer route.jpg, transport.jpg et stop.jpg. Télécharger le JSON. Si la démonstration live échoue, ouvrir results/demo/predictions.json et les images correspondantes. Source : docs/DEMONSTRATION.md.');
let shot='results/app_screenshot.png';try{await fs.access(path.join(root,shot));}catch{shot='results/demo/route_prediction.jpg';}
await image(s,shot,64,185,710,425);
para(s,['1  Choisir une image','2  Lancer l’analyse','3  Examiner les erreurs','4  Exporter le JSON'],825,200,390,27,100);

s=slide('Limites et prochaines étapes','60 secondes. Ne pas annoncer un système de guidage validé. Le futur travail exige des données et des annotations supplémentaires avant une optimisation des scores. Mentionner la configuration OCR anglais/français sans couverture arabe. Sources : rapport, section limites.');
para(s,['Petits datasets et scènes parfois proches malgré le regroupement.','Panneaux LED, flou et recadrages partiels difficiles à lire.','Aucun référentiel de noms d’arrêt, aucune validation en circulation.','Suite : corpus local annoté, textes bilingues et essais utilisateurs.'],64,185,1130,28,110);

s=slide('Bilan du projet','45 secondes. Conclure sur les réalisations vérifiables et leurs limites. Les contributions individuelles doivent être complétées avec les étudiants, sans attribution inventée. Chaque membre remet les trois livrables individuellement. Sources : rapport et README.');
para(s,['Une chaîne Python complète, exécutable et documentée.','Des modèles entraînés, des métriques et des erreurs conservées.','Une application locale et une démonstration reproductible.','Un prototype à enrichir avant toute utilisation d’orientation réelle.'],64,190,1130,29,105);

await fs.mkdir(path.join(workspaceDir,'work/slides'),{recursive:true});
for(const [i,s] of pres.slides.items.entries()){
  const png=await pres.export({slide:s,format:'png',scale:1});
  await fs.writeFile(path.join(workspaceDir,`work/slides/slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(workspaceDir,'work/deck_draft.pptx');await(await PresentationFile.exportPptx(pres)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir,candidatePath:candidate,finalPath:path.join(workspaceDir,'outputs/Presentation_Projet9.pptx'),pythonExecutable:RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(workspaceDir,'work/deck_validation.json')});
console.log(JSON.stringify(result));


