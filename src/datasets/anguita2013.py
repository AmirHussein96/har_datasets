import pandas as pd
from os.path import join
from tqdm import tqdm

from ..utils import (
    load_data, build_time, build_seq_list,
    index_decorator, label_decorator, fold_decorator, data_decorator
)

from ..base import Dataset


class anguita2013(Dataset):
    def __init__(self):
        self.win_len = 128
        
        super(anguita2013, self).__init__(
            name='anguita2013',
            unzip_path=lambda s: s.replace('%20', ' ')
        )
    
    @label_decorator
    def build_labels(self, path, *args, **kwargs):
        labels = []
        for fold in ('train', 'test'):
            fold_labels = load_data(join(path, fold, f'y_{fold}.txt'))
            labels.extend([l for l in fold_labels for _ in range(self.win_len)])
        return self.dataset.inv_lookup, pd.DataFrame(dict(labels=labels))
    
    @fold_decorator
    def build_folds(self, path, *args, **kwargs):
        fold = []
        fold.extend([-1 for _ in load_data(join(path, 'train', 'y_train.txt')) for _ in range(self.win_len)])
        fold.extend([+1 for _ in load_data(join(path, 'test', 'y_test.txt')) for _ in range(self.win_len)])
        return pd.DataFrame(dict(fold=fold)).astype(int)
    
    @index_decorator
    def build_index(self, path, *args, **kwargs):
        sub = []
        for fold in ('train', 'test'):
            sub.extend(load_data(join(path, fold, f'subject_{fold}.txt')))
        index = pd.DataFrame(dict(
            sub=[si for si in sub for _ in range(self.win_len)],
            sub_seq=build_seq_list(subs=sub, win_len=self.win_len),
            time=build_time(subs=sub, win_len=self.win_len, fs=float(self.dataset.meta['fs'])),
        ))
        return index
    
    @data_decorator
    def build_data(self, path, modality, location, *args, **kwargs):
        x_data = []
        y_data = []
        z_data = []
        modality = dict(
            accel='acc',
            gyro='gyro',
        )[modality]
        for fold in ('train', 'test'):
            for l, d in zip((x_data, y_data, z_data), ('x', 'y', 'z')):
                ty = ['body', 'total'][modality in {'accel', 'acc'}]
                acc = load_data(join(path, fold, 'Inertial Signals', f'{ty}_{modality}_{d}_{fold}.txt'), astype='np')
                l.extend(acc.ravel().tolist())
        data = pd.DataFrame(dict(x=x_data, y=y_data, z=z_data))
        return data