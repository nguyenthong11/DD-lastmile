# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 15:57:14 2022

@author: quoc-thong.nguyen
"""
import numpy as np
import pandas as pd
from k_means_constrained import KMeansConstrained

# max number of BACS per vehicle
def Clustering_constraint(CLIENTSi, Nbac, flag_time): 
    CLIENTSk = CLIENTSi[CLIENTSi['# BACS']>1]
    for ID in CLIENTSk['ID']: # replicate the locations
        k = (CLIENTSk[CLIENTSk['ID'] == ID]['# BACS']).values[0]
        CLIENTSi = CLIENTSi.append([CLIENTSi[CLIENTSi['ID'] == ID]]*(k-1)
                                   ,ignore_index=True)
    if flag_time==1:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE','begin_time']]
    elif flag_time==0:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE']]
    else:
        dfCOORi = CLIENTSi[['begin_time']]
    Ncluster = int(np.ceil(len(dfCOORi)/Nbac))
    clf = KMeansConstrained(n_clusters=Ncluster,size_min=3,size_max=Nbac
                            ,random_state=0)
    clf.fit_predict(dfCOORi.to_numpy())
    CLIENTSi['CLUSTER'] = clf.labels_
    '''explain: if one client is clustered into more than one cluster,
        that client is merged into one cluter, meaning 1 client to ONLY 1 cluster'''
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
        sum_clus  = sum_clus.append([pd.DataFrame([[temp['# BACS'].sum()
                                                    ,len(temp),c]],columns=Name)]
                                    , ignore_index=True)
    return CLIENTSi, sum_clus, clf.cluster_centers_
# ----------------------------------------------------------------------------------------------------
# -------------------------- Clustreing constraint velocargo -----------------------------------------
def Clustering_constraint_velo(CLIENTSi, Nbac, flag_time): 
    CLIENTSk = CLIENTSi[CLIENTSi['# BACS']>1]
    for ID in CLIENTSk['ID']: # replicate the locations
        k = (CLIENTSk[CLIENTSk['ID'] == ID]['# BACS']).values[0]
        CLIENTSi = CLIENTSi.append([CLIENTSi[CLIENTSi['ID'] == ID]]*(k-1)
                                   ,ignore_index=True)
    if flag_time==1:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE','begin_time']]
    else:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE']]
    Ncluster = int(np.around(len(dfCOORi)/Nbac))+1
    clf = KMeansConstrained(n_clusters=Ncluster,size_min=3,size_max=Nbac
                            ,random_state=0)
    clf.fit_predict(dfCOORi.to_numpy())
    CLIENTSi['CLUSTER'] = clf.labels_
    '''explain: in case one client clustered to more than one cluster
        that client is considered as multiple clients with different size of BAC'''
    CLIENTSi_new = pd.DataFrame(columns=CLIENTSi.columns)
    for c in CLIENTSi['CLUSTER'].unique():
        temp = CLIENTSi[CLIENTSi['CLUSTER'] == c]
        for cliID in temp['ID'].unique():
            temp2 = temp[temp['ID'] == cliID]
            temp2['# BACS'] = len(temp2)
            CLIENTSi_new = CLIENTSi_new.append(temp2.iloc[0])

    #CLIENTSi = CLIENTSi.drop_duplicates(ignore_index=True)
    Name = ['nb_client','label']
    sum_clus = pd.DataFrame(dtype=np.int8)
    for c in CLIENTSi_new['CLUSTER'].unique():
        temp = CLIENTSi_new[CLIENTSi_new['CLUSTER'] == c]
        sum_clus  = sum_clus.append([pd.DataFrame([[len(temp),c]],columns=Name)]
                                    , ignore_index=True)
    return CLIENTSi_new, sum_clus, clf.cluster_centers_

# client contraint
def Clustering_(CLIENTSi, max_client, flag_time): 
    if flag_time==1:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE','begin_time']]
    elif flag_time==0:
        dfCOORi = CLIENTSi[['LATITUDE','LONGITUDE']]
    else:
        dfCOORi = CLIENTSi[['begin_time']]
    # Ncluster = int(np.round((max(CLIENTSi['begin_time'])-min(CLIENTSi['begin_time']))/time_slot))
    Ncluster = int(np.ceil(len(dfCOORi)/max_client))
    
    clf = KMeansConstrained(n_clusters=Ncluster,size_min=2,size_max=max_client,random_state=0)

    clf.fit_predict(dfCOORi.to_numpy())
    CLIENTSi['CLUSTER'] = clf.labels_

    Name = ['nb_BAC', 'nb_client','label']
    sum_clus = pd.DataFrame(dtype=np.int8)
    for c in CLIENTSi['CLUSTER'].unique():
        temp = CLIENTSi[CLIENTSi['CLUSTER'] == c]
        sum_clus  = sum_clus.append([pd.DataFrame([[temp['# BACS'].sum()
                                                    ,len(temp),c]],columns=Name)]
                                    , ignore_index=True)
    return CLIENTSi, sum_clus, clf.cluster_centers_