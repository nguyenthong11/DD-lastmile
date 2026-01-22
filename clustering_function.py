"""
Created on Wed Feb  2 15:57:14 2022

@author: quoc-thong.nguyen
"""
import numpy as np
import pandas as pd
from k_means_constrained import KMeansConstrained

def Clustering_constraint(CLIENTSi, Nbac: int, flag_time: bool = True):
    """
    Parameters:
    -----------
    CLIENTSi : DataFrame with '# BACS', 'ID', 'LATITUDE', 'LONGITUDE', and optionally 'begin_time'
    Nbac : int, maximum bins per vehicle
    flag_time : bool, include timestamp? If True -> ('LAT', 'LON', 'time'); False -> ('LAT', 'LON')
    
    Returns:
    --------
    CLIENTSi : clustered data
    sum_clus : cluster summary (nb_BAC, nb_client, label)
    cluster_centers : cluster centroids
    """

    # ==================== STEP 1: Replicate clients with multiple BACs ====================

    CLIENTSk = CLIENTSi[CLIENTSi['# BACS']>1]
    duplicates = CLIENTSi[CLIENTSi['# BACS'] > 1]

    if not duplicates.empty():
        for _, row in duplicates.iterrows():
            ID = row['ID']
            k = row['# BACS']
            # Add k-1 duplicates
            CLIENTSi = pd.concat([
                CLIENTSi,
                CLIENTSi[CLIENTSi['ID'] == ID].copy()] * (k - 1),
                ignore_index=True)

    # ==================== STEP 2: Select coordinates to cluster ====================
    if flag_time:
        coordinates = CLIENTSi[['LATITUDE','LONGITUDE','begin_time']]
    else: 
        coordinates = CLIENTSi[['LATITUDE','LONGITUDE']]

    # ==================== STEP 3: Constrained KMeans ====================

    Ncluster = int(np.ceil(len(coordinates)/Nbac))
    duplicates = CLIENTSi[CLIENTSi['# BACS'] > 1]

    if not duplicates.empty():
        for _, row in duplicates.iterrows():
            ID = row['ID']
            k = row['# BACS']
            # Add k-1 duplicates
            CLIENTSi = pd.concat([
                CLIENTSi,
                CLIENTSi[CLIENTSi['ID'] == ID].copy()] * (k - 1),
                ignore_index=True)

    # ==================== STEP 2: Select coordinates to cluster ====================
    if flag_time:
        coordinates = CLIENTSi[['LATITUDE','LONGITUDE','begin_time']]
    else: 
        coordinates = CLIENTSi[['LATITUDE','LONGITUDE']]

    # ==================== STEP 3: Constrained KMeans ====================

    Ncluster = int(np.ceil(len(coordinates)/Nbac))
    clf = KMeansConstrained(n_clusters=Ncluster,
                            size_min=3,
                            size_max=Nbac,
                            random_state=0)
    clf.fit_predict(coordinates.to_numpy())
    clf.fit_predict(coordinates.to_numpy())
    CLIENTSi['CLUSTER'] = clf.labels_

    # ==================== STEP 4: Merge clients across clusters ====================

    # ==================== STEP 4: Merge clients across clusters ====================
    '''explain: if one client is labeled into more than one cluster,
        that client is merged into one cluster ONLY'''
    
    client_clusters = CLIENTSi.groupby('ID')['CLUSTER'].unique().to_dict()
    
    for ID, cluster_ids in client_clusters.items():
        # If client is in multiple clusters, find the largest cluster
        if len(cluster_ids) > 1:
            # Get cluster sizes once (not multiple times in loop)
            cluster_sizes = CLIENTSi['CLUSTER'].value_counts()
            min_cluster = cluster_sizes.idxmin()
            
            # Assign all client's records to this cluster
            CLIENTSi.loc[CLIENTSi['ID'] == ID, 'CLUSTER'] = min_cluster

    # ==================== STEP 5: Remove duplicates ====================
    
    client_clusters = CLIENTSi.groupby('ID')['CLUSTER'].unique().to_dict()
    
    for ID, cluster_ids in client_clusters.items():
        # If client is in multiple clusters, find the largest cluster
        if len(cluster_ids) > 1:
            # Get cluster sizes once (not multiple times in loop)
            cluster_sizes = CLIENTSi['CLUSTER'].value_counts()
            min_cluster = cluster_sizes.idxmin()
            
            # Assign all client's records to this cluster
            CLIENTSi.loc[CLIENTSi['ID'] == ID, 'CLUSTER'] = min_cluster

    # ==================== STEP 5: Remove duplicates ====================
    CLIENTSi = CLIENTSi.drop_duplicates(ignore_index=True)

    # ==================== STEP 6: Summarize clusters ====================
    cluster_stats = []
    for cluster_id in CLIENTSi['CLUSTER'].unique():
        cluster_data = CLIENTSi[CLIENTSi['CLUSTER'] == cluster_id]
        total_bacs = cluster_data['# BACS'].sum()
        num_clients = len(cluster_data)
        
        cluster_stats.append({
            'nb_BAC': total_bacs,
            'nb_client': num_clients,
            'label': cluster_id
        })
    
    sum_clus = pd.DataFrame(cluster_stats)
    cluster_centers = clf.cluster_centers_

    # ==================== STEP 6: Summarize clusters ====================
    cluster_stats = []
    for cluster_id in CLIENTSi['CLUSTER'].unique():
        cluster_data = CLIENTSi[CLIENTSi['CLUSTER'] == cluster_id]
        total_bacs = cluster_data['# BACS'].sum()
        num_clients = len(cluster_data)
        
        cluster_stats.append({
            'nb_BAC': total_bacs,
            'nb_client': num_clients,
            'label': cluster_id
        })
    
    sum_clus = pd.DataFrame(cluster_stats)
    cluster_centers = clf.cluster_centers_

    return CLIENTSi, sum_clus, cluster_centers
    return CLIENTSi, sum_clus, cluster_centers
