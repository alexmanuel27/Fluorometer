"""Training stage: opens ONLY 11Samples.xlsx, then freezes the selected model.

All model selection, including nested LOO diagnostics, uses these 11 samples.
The existing, fixed feature catalogue is reused; its main analysis is not run.
"""
from pathlib import Path
import csv
import hashlib
import json
import sys

import numpy as np
from sklearn.cross_decomposition import PLSRegression

OUT=Path(__file__).resolve().parent
DATA=OUT.parent
sys.path.insert(0,str(DATA/'comparacion_modelos_11_a_9'))
from comparar import candidates, load, metrics


def predict(spec,train_x,train_y,test_x):
    if spec.get('components'):
        estimator=PLSRegression(n_components=spec['components'],scale=True)
        estimator.fit(train_x,train_y)
        return estimator.predict(test_x).reshape(-1)
    coef=np.linalg.lstsq(train_x,train_y,rcond=None)[0]
    return test_x@coef


def loo(spec,X,y):
    p=np.empty(len(y))
    for i in range(len(y)):
        keep=np.arange(len(y))!=i
        p[i]=predict(spec,X[keep],y[keep],X[i:i+1])[0]
    return p


def choose(records):
    best=min(r['rmse'] for r in records)
    tied=[r for r in records if abs(r['rmse']-best)<=1e-8]
    return min(tied,key=lambda r:(r['complexity'],r['blank']!='No',r['id']))


def main():
    g,source_hash=load('11')
    y=g['c']
    specs={s['id']:s for s in candidates()}
    Xs={key:np.c_[np.ones(len(y)),s['fn'](g)] for key,s in specs.items()}
    raw=np.column_stack([g[str(nm)] for nm in (460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940)])
    for n in (1,2,3):
        key=f'pls_{n}'
        specs[key]={'id':key,'label':f'PLS {n} components','blank':'No','components':n}
        Xs[key]=raw
    records=[]
    for key,spec in specs.items():
        p=loo(spec,Xs[key],y);m=metrics(y,p)
        records.append({'id':key,'label':spec['label'],'blank':spec['blank'],
                        'complexity':spec.get('components',Xs[key].shape[1]),
                        'rmse':m['rmse_ug_ml'],'r2':m['r2'],'mae':m['mae_ug_ml']})
    winner=choose(records)

    # Outer LOO estimates the entire procedure, including inner model selection.
    nested=np.empty(len(y));outer_models=[]
    for i in range(len(y)):
        keep=np.arange(len(y))!=i
        scores=[]
        for key,spec in specs.items():
            p=loo(spec,Xs[key][keep],y[keep])
            scores.append({'id':key,'complexity':spec.get('components',Xs[key].shape[1]),
                           'blank':spec['blank'],'rmse':float(np.sqrt(np.mean((p-y[keep])**2)))})
        chosen=choose(scores)['id']
        nested[i]=predict(specs[chosen],Xs[chosen][keep],y[keep],Xs[chosen][i:i+1])[0]
        outer_models.append(chosen)
    key=winner['id'];spec=specs[key];X=Xs[key]
    frozen={'protocol':'fit and select using only 11Samples.xlsx; evaluate other data in a separate stage',
            'training_source':'11Samples.xlsx','training_sha256':source_hash,'candidate_count':len(specs),
            'selected_id':key,'selected_label':spec['label'],'blank':spec['blank'],
            'selection_rule':'minimum LOO RMSE; numerical ties within 1e-8 favor lower complexity then no blank',
            'cv_selected_model':{k:v for k,v in winner.items() if k in ('rmse','r2','mae')},
            'nested_cv_selection_procedure':metrics(y,nested),'nested_fold_models':outer_models}
    if spec.get('components'):
        frozen['components']=spec['components']
        estimator=PLSRegression(n_components=spec['components'],scale=True).fit(X,y)
        # Evaluation recreates this selected estimator using training data only.
        fitted=estimator.predict(X).reshape(-1)
    else:
        coef=np.linalg.lstsq(X,y,rcond=None)[0]
        frozen['features']=spec['formula_features']
        frozen['coefficients']=[float(v) for v in coef]
        fitted=X@coef
    frozen['training_fit']=metrics(y,fitted)
    ranked=sorted(records,key=lambda r:(r['rmse'],r['complexity'],r['blank']!='No',r['id']))
    # Fix the eight finalists and their order before the comparison stage.
    frozen['finalists']=[]
    for record in ranked[:8]:
        sid=record['id'];s=specs[sid]
        finalist={'id':sid,'label':s['label'],'blank':s['blank'],'rmse_cv11':record['rmse']}
        if s.get('components'):finalist['components']=s['components']
        else:
            finalist['features']=s['formula_features']
            finalist['coefficients']=[float(v) for v in np.linalg.lstsq(Xs[sid],y,rcond=None)[0]]
        frozen['finalists'].append(finalist)
    with (OUT/'ranking_cv_11.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(ranked[0]));wr.writeheader();wr.writerows(ranked)
    with (OUT/'predicciones_cv_11.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f);wr.writerow(['sample','reference','nested_prediction','nested_selected_model'])
        for i in range(len(y)):wr.writerow([int(g['id'][i]),y[i],nested[i],outer_models[i]])
    (OUT/'modelo_fijado.json').write_text(json.dumps(frozen,indent=2),encoding='utf-8')
    assert hashlib.sha256((DATA/'11Samples.xlsx').read_bytes()).hexdigest()==source_hash
    assert key==choose(records)['id']
    print(json.dumps({'frozen_model':frozen,'top_cv11':ranked[:8]},indent=2))


if __name__=='__main__':main()
