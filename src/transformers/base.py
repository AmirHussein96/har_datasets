from os.path import join, exists
from os import symlink, remove
import tempfile

from .. import BaseGraph, TransformerMeta

from ..utils import Partition


def symlink_allowed():
    """
    Symbolic links are tricky in some
    :return:
    """
    try:
        with tempfile.NamedTemporaryFile() as fil:
            symlink(fil.name, fil.name + '-symlink')
    except OSError:
        return False
    return True


def make_symlink(in_path, out_path, ext):
    in_path = f'{in_path}.{ext}'
    out_path = f'{out_path}.{ext}'
    assert exists(in_path)
    if not exists(out_path):
        symlink(in_path, out_path)


class TransformerBase(BaseGraph):
    def __init__(self, name, parent, *args, **kwargs):
        super(TransformerBase, self).__init__(name=name)

        self.meta = TransformerMeta(name)
        self.parent = parent

        assert hasattr(parent.meta, 'fs')

        self.meta.add_category('fs', parent.meta['fs'])

    @property
    def identifier(self):
        return join(
            self.parent.identifier,
            self.name,
        )

    def compose_meta(self, name):
        assert name in {'label', 'index', 'fold'}

        if symlink_allowed():
            return self.node(
                node_name=self.build_path(name),
                func=make_symlink,
                kwargs=dict(
                    in_path=self.parent.build_path(name),
                    out_path=self.build_path(name),
                    ext=self.backends[self.default_backend].ext
                ),
            )

        def copy_file(key, index, data, **kwargs):
            return data

        return self.node(
            node_name=self.build_path(name),
            func=Partition(
                func=copy_file,
            ),
            sources=dict(
                index=self.parent.index,
                data=self.parent.get_index(name)
            ),
            kwargs=dict(
                key=self.build_path(name),
                fs=self.parent.meta.fs,
                **(self.extra_args or dict())
            ),
        )

    def make_node(self, in_key, out_key, func):
        return self.node(
            node_name=self.build_path(*out_key),
            func=Partition(
                func=func,
            ),
            sources=dict(
                index=self.parent.index,
                data=self.parent.outputs[in_key]
            ),
            kwargs=dict(
                key=out_key,
                fs=self.parent.meta.fs,
                **(self.extra_args or dict())
            ),
        )
