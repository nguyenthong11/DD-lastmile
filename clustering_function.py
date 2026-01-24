"""
Created on Wed Feb  2 15:57:14 2022

@author: quoc-thong.nguyen
"""
import numpy as np
import pandas as pd
from k_means_constrained import KMeansConstrained

def Clustering_constraint(CLIENTSi, Nbac: int, include_time: bool = True):
    """
    Parameters:
    -----------
    CLIENTSi : DataFrame with '# BACS', 'ID', 'LATITUDE', 'LONGITUDE', and optionally 'begin_time'
    Nbac : int, number of bins per cluster
    include_time : bool, include timestamp? If True -> ('LAT', 'LON', 'time'); False -> ('LAT', 'LON')
    
    Returns:
    --------
    CLIENTSi : clustered data
    cluster_summary : cluster summary (cluster_id, total_bacs, num_clients)
    cluster_centers : cluster centroids
    """

    # ==================== STEP 1: Replicate clients with multiple BACs ====================
    repeat_counts = CLIENTSi['# BACS'].fillna(1).astype(int).clip(lower=1)
    repeated_indices = np.repeat(CLIENTSi.index, repeat_counts)
    CLIENTSi = CLIENTSi.loc[repeated_indices].reset_index(drop=True)

    # ==================== STEP 2: Select coordinates to cluster ====================
    if include_time:
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
    CLIENTSi['CLUSTER'] = clf.labels_

    # ==================== STEP 4: Merge clients across clusters ====================
    '''explain: if one client is labeled into more than one cluster,
        that client is merged into one cluster ONLY'''
    
    cluster_sizes = CLIENTSi['CLUSTER'].value_counts()
    CLIENTSi['_size'] = CLIENTSi['CLUSTER'].map(cluster_sizes)

    # Get target cluster per client
    target = CLIENTSi.sort_values('_size', ascending=True).groupby('ID')['CLUSTER'].first()

    # Assign all client records to target cluster
    CLIENTSi['CLUSTER'] = CLIENTSi['ID'].map(target)
    CLIENTSi.drop('_size', axis=1, inplace=True)

    # ==================== STEP 5: Remove duplicates ====================
    CLIENTSi = CLIENTSi.drop_duplicates(ignore_index=True)

    # ==================== STEP 6: Summarize clusters ====================
    cluster_summary = (
        CLIENTSi
        .groupby('CLUSTER')
        .agg(
            total_bacs=('# BACS', 'sum'),
            num_clients=('ID', 'count')
        )
        .reset_index()
        .rename(columns={'CLUSTER': 'cluster_id'})
    )
    cluster_centers = clf.cluster_centers_

    return CLIENTSi, cluster_summary, cluster_centers