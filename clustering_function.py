# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 15:57:14 2022

@author: quoc-thong.nguyen
"""
import numpy as np
import pandas as pd
from k_means_constrained import KMeansConstrained

# max number of bins per vehicle
def Clustering_constraint(CLIENTSi, Nbac: int, flag_time: bool=1):

    CLIENTSk = CLIENTSi[CLIENTSi['# BACS']>1]
    for ID in CLIENTSk['ID']: # replicate the locations
        k = (CLIENTSk[CLIENTSk['ID'] == ID]['# BACS']).values[0]
        CLIENTSi = pd.concat([CLIENTSi,pd.concat([CLIENTSi[CLIENTSi['ID'] == ID]]*(k-1))],
                             ignore_index=True)
    if flag_time==1:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE','begin_time']]
    elif flag_time==0:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE']]
    else:
        dfCOORi = CLIENTSi[['begin_time']]
    Ncluster = int(np.ceil(len(dfCOORi)/Nbac))
    clf = KMeansConstrained(n_clusters=Ncluster,
                            size_min=3,
                            size_max=Nbac,
                            random_state=0)
    clf.fit_predict(dfCOORi.to_numpy())
    CLIENTSi['CLUSTER'] = clf.labels_
    '''explain: if one client is labeled into more than one cluster,
        that client is merged into one cluster ONLY'''
    df_temp = CLIENTSi.drop_duplicates(ignore_index=True)
    for ID in df_temp['ID'].unique():
        temp = df_temp[df_temp['ID'] == ID]
        if len(temp) > 1:
            S_clus = []
            clusterS = list(temp['CLUSTER'])
            for c in clusterS:
                S_clus.append(len(CLIENTSi[CLIENTSi['CLUSTER'] == c]))
                t = CLIENTSi[CLIENTSi['ID'] == ID]
                t['CLUSTER'] = clusterS[S_clus.index(min(S_clus))]
                CLIENTSi[CLIENTSi['ID'] == ID] = t
    CLIENTSi = CLIENTSi.drop_duplicates(ignore_index=True)
    Name = ['nb_BAC', 'nb_client','label']
    sum_clus = pd.DataFrame(dtype=np.int8)
    for c in CLIENTSi['CLUSTER'].unique():
        temp = CLIENTSi[CLIENTSi['CLUSTER'] == c]
        d = pd.DataFrame([[temp['# BACS'].sum(),len(temp),c]],columns=Name)
        sum_clus  = pd.concat([sum_clus, d], ignore_index=True)

    return CLIENTSi, sum_clus, clf.cluster_centers_
