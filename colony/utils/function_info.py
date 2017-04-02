from inspect import signature


class FunctionInfo(object):

    def __init__(self, func):
        self.func = func

    @property
    def num_args(self):
        sig = self.signature
        return len([x for x in sig.parameters.values() if x.default == sig.empty])

    @property
    def num_kwargs(self):
        return len(self.kwargs)

    @property
    def kwargs(self):
        sig = self.signature
        return [x for x in sig.parameters.values() if x.default != sig.empty]

    @property
    def signature(self):
        return signature(self.func)