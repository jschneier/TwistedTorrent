class ReadOnceBuffer(bytearray):
    """Data structure that automatically deletes the piece of a bytearray that
    you slice. Peek can be used to avoid deletion."""

    def __init__(self, data=None):
        self.bytes = bytearray() if data is None else bytearray(data)

    def peek(self, start=None, stop=None, step=None):
        if stop is None:
            return self.bytes.__getitem__(start)
        else:
            return self.bytes.__getitem__(slice(start, stop, step))

    def __add__(self, data):
        return ReadOnceBuffer(self.bytes + data)

    def __iadd__(self, data):
        self.bytes += data
        return self

    def __str__(self):
        return str(self.bytes)

    def __repr__(self):
        return 'ReadOnceBuffer(b\'' + repr(str(self.bytes)) + '\')'

    def __len__(self):
        return len(self.bytes)

    def __eq__(self, other):
        return self.bytes == other

    def __getitem__(self, slicer):
        if isinstance(slicer, int):
            if slicer >= len(self):
                raise IndexError(slicer)

        ret = self.bytes.__getitem__(slicer)
        self.bytes.__delitem__(slicer)

        return ret
