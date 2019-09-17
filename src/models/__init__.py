from .sklearn import scale_log_reg

__all__ = [
    'load_model',
    'scale_log_reg',
]


def load_model(*args, **kwargs):
    visualisations = {kk: globals()[kk] for kk in __all__}
    assert args[0] in visualisations
    return visualisations[args[0]](*args[1:], **kwargs)
