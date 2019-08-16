from os.path import join

import pandas as pd
import numpy as np

from scipy.io import loadmat

from tqdm import trange

from ..base import Dataset
from ..utils import index_decorator, label_decorator, fold_decorator, data_decorator


def uschad_iterator(path, columns=None, cols=None, callback=None, desc=None):
    print(path)
    
    data_list = []
    
    ii = 0
    
    for sub_id in trange(1, 14 + 1, desc=desc):
        for act_id in range(1, 12 + 1):
            for trail_id in range(1, 5 + 1):
                fname = join(
                    path, f'Subject{sub_id}', f'a{act_id}t{trail_id}.mat'
                )
                
                data = loadmat(fname)['sensor_readings']
                
                if callback:
                    data = callback(ii, sub_id, act_id, trail_id, data)
                elif cols:
                    data = data[cols]
                else:
                    raise ValueError
                
                data_list.extend(data)
                ii += 1
                
    df = pd.DataFrame(data_list)
    if columns:
        df.columns = columns
    return df


class uschad(Dataset):
    def __init__(self):
        super(uschad, self).__init__(
            name='uschad',
        )
    
    @label_decorator
    def build_labels(self, path, *args, **kwargs):
        def callback(ii, sub_id, act_id, trial_id, data):
            return np.zeros((data.shape[0], 1)) + act_id
        
        return self.dataset.inv_lookup, uschad_iterator(path, callback=callback, desc='Labels')
    
    @fold_decorator
    def build_folds(self, path, *args, **kwargs):
        def callback(ii, sub_id, act_id, trial_id, data):
            return np.zeros((data.shape[0], 1)) + sub_id > 10
        
        return uschad_iterator(path, callback=callback, desc='Folds')
    
    @index_decorator
    def build_index(self, path, *args, **kwargs):
        def callback(ii, sub_id, act_id, trial_id, data):
            return np.c_[
                np.zeros((data.shape[0], 1)) + sub_id,
                np.zeros((data.shape[0], 1)) + ii,
                np.arange(data.shape[0]) / self.dataset.meta['fs']
            ]
        
        return uschad_iterator(path, callback=callback, columns=['sub', 'sub_seq', 'time'], desc='Index')
    
    @data_decorator
    def build_data(self, path, modality, location, *args, **kwargs):
        cols = dict(
            accel=[0, 1, 2],
            gyro=[3, 4, 5]
        )[modality]
        
        def callback(ii, sub_id, act_id, trial_id, data):
            return data[:, cols]
        
        return uschad_iterator(path, callback=callback, desc='Data')