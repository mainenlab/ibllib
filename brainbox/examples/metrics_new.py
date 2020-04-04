# -*- coding: utf-8 -*-
r"""
Created on Wed Apr  1 21:46:59 2020

@author: Steinmetz Lab User
Example:
  # define alf and ks directories:
>>>alf_dir = r'C:\Users\Steinmetz Lab User\Documents\Lab\SpikeSortingOutput\Hopkins_CortexLab\test_path_alf'
>>>ks_dir = r'C:\Users\Steinmetz Lab User\Documents\Lab\SpikeSortingOutput\Hopkins_CortexLab'

  # run gen_metrics_labels
>>>from metrics_new import gen_metrics_labels
>>>gen_metrics_labels(alf_dir, ks_dir)
"""


import time
from pathlib import Path
import numpy as np
import alf.io as aio
import matplotlib.pyplot as plt
from max_acceptable_isi_viol_2 import max_acceptable_cont_2
import brainbox as bb
from phylib.stats import correlograms
import pandas as pd
from defined_metrics import FP_RP, noise_cutoff, peak_to_peak_amp




def gen_metrics_labels(alf_dir, ks_dir):
    spks_b = aio.load_object(alf_dir, 'spikes')
    clstrs_b = aio.load_object(alf_dir, 'clusters')
    units_b = bb.processing.get_units_bunch(spks_b)
    units = list(units_b.amps.keys())
    n_units = np.max(spks_b.clusters) + 1
    
    
    uidx=0
    label=np.empty([len(units)])
    RefPViol = np.empty([len(units)])
    NoiseCutoff = np.empty([len(units)])
    for unit in units:
        #unit = units[685] #635 max spike rate #681 1.43
        ts = units_b['times'][unit]
        amps = units_b['amps'][unit]
        ch = clstrs_b['channels'][int(unit)]  # channel of max amplitude
    
        RefPViol[int(unit)] = FP_RP(ts)
        NoiseCutoff[int(unit)] = noise_cutoff(amps,quartile_length=.25,std_cutoff = 2)
        
        if (FP_RP(ts) and not noise_cutoff(amps,quartile_length=.25,std_cutoff = 2)) : #to do: add and mean(amps)>50microvolts?
            label[int(unit)] = 1
        else:
            label[int(unit)] = 0
        
    try:
        refpvioldf = pd.DataFrame(RefPViol)
        refpvioldf.to_csv(Path(ks_dir, 'RefPViol.tsv'),
                                sep='\t', header=['RefPViol'])
    except Exception as err:
        print("Could not save 'RefPViol' to .tsv. Details: \n {}".format(err))
        
    try:
        noisecutoffdf = pd.DataFrame(NoiseCutoff)
        noisecutoffdf.to_csv(Path(ks_dir, 'NoiseCutoff.tsv'),
                                sep='\t', header=['NoiseCutoff'])
    except Exception as err:
        print("Could not save 'NoiseCutoff' to .tsv. Details: \n {}".format(err))
        
   
    try:
        labeldf = pd.DataFrame(label)
        labeldf.to_csv(Path(ks_dir, 'label.tsv'),
                                sep='\t', header=['label'])
    except Exception as err:
        print("Could not save 'label' to .tsv. Details: \n {}".format(err))
        
    numpass=int(sum(label))
    print("Number of units that pass: ", numpass)
