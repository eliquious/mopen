"""
mopen.py
========

This small but powerful module allows for the reading of multiple files
as if they were one. File borders are merged transparently behind the
scenes allowing effortless reads across many files.

"""
import os
from glob import glob

class mopen(object):
    """
    This class imitates the default Python file handle.

    :param files: list of filenames to include
    :type data: list
    :param iotype: IO operation
    :type iotype: str
    :param sort: if True, files are sorted
    :type sort: bool

    Currently, only reads are supported. The files are by default sorted
    by the stat.ST_INO and size. On Windows, ST_INO is not supported thus
    the files will be sorted by size only.

    .. code-block:: python
        :linenos:

        import glob
        files = glob.glob("./path/to/files/*.txt")
        data = ""
        with mopen(files, "rb") as fh:
            data = fh.read()

    .. note:: Performance

        Reading lines one-by-one is slow. Use readlines(size) whenever possible.

    """
    def __init__(self, files, iotype="rb", sort=True):
        super(mopen, self).__init__()
        self.type = iotype
        if not "r" in self.type:
            raise IOError("Only reads are supported")
        if type(files) is str:
            self.files = [files]

        self.files = files
        if sort:
            self.files = list(sorted(self.files, key=lambda f: (os.stat(f).st_ino, os.path.getsize(f)), reverse=True))
        self.sizes = list(self._sizes())
        self.inodes = list(self._inode())
        self.totalsize = sum(self.sizes)
        self.num = 0
        self.pos = 0

    def getfileat(self, pos):
        """
        Calculates which file the given position falls in.

        :param pos: byte position
        :type pos: int
        :returns: (file num, file name)
        :rtype: tuple
        """
        if len(self.files) < 1:
            return 0, None
        runningsize = 0
        i = 0
        fc = len(self.files) - 1
        for size in self.sizes:
            runningsize += size
            if runningsize > pos or i == fc:
                break
            i += 1
        return i, self.files[i]

    def tell(self):
        """
        Gives the current position in the files, measured in bytes from the beginning of the files.

        :returns: byte location in files
        :rtype: int
        """
        return self.pos

    def _partialread(self, size):
        data = ""
        self.num, filename = self.getfileat(self.pos)
        fh = open(filename, self.type)
        sizeplusprev = sum(self.sizes[:self.num + 1])
        start = self.sizes[self.num] + (self.pos - sizeplusprev)
        totalremaining = self.totalsize - self.pos
        remaining = sizeplusprev - self.pos
        if remaining == 0:
            return data

        if (self.pos - sizeplusprev) < 0 and start > 0:
            fh.seek(start)

        if size > remaining and remaining > 0:
            data += fh.read(remaining)
        else:
            data += fh.read(size)

        fh.close()
        return data

    def read(self, size=None):
        """
        Reads bytes up to the size of bytes given.

        :param size: maximum number of bytes to read
        :type size: int
        :returns: string of data read
        :rtype: str
        """
        data = ""
        if size is None:
            size = self.totalsize

        totalremaining = self.totalsize - self.pos
        if size > totalremaining:
            size = totalremaining
        remaining = size
        while remaining > 0:
            tmpdata = self._partialread(remaining)
            length = len(tmpdata)
            remaining -= length
            self.pos += length
            data += tmpdata
        return data

    def readlines(self, size=None):
        """
        Reads lines up to the size of bytes given. Reads are buffered at 32MB.

        :param size: maximum number of bytes to read
        :type size: int
        :returns: generator of strings
        :rtype: generator
        """
        step = 32 * 1024 * 1024
        if size is None:
            size = self.size()
        if step > size:
            step = size
        remaining = size
        data = ""
        while remaining > 0:
            remaining -= step
            data += self.read(step)
            tmp = data.split("\n")
            if len(tmp) < 2:
                if remaining == 0:
                    break
                else:
                    continue
            for line in tmp[:-1]:
                yield line
            data = tmp[-1]
        if len(data) > 0:
            yield data

    def readline(self):
        """Reads a line from the files and advances the file position

        :returns: next line
        :rtype: str
        """
        line = None
        self.num, filename = self.getfileat(self.pos)
        pos = self.sizes[self.num] - (sum(self.sizes[:self.num + 1]) - self.pos)
        with open(self.currentfile(), self.type) as fh:
            fh.seek(pos)
            line = fh.readline()
        self.pos += len(line)
        if not line and self.pos < self.totalsize:
            self.num += 1
            line = self.readline()
        return line

    def seek(self, pos):
        """"Seeks to a location in the files

        :param pos: byte location in files
        :type pos: int
        :returns: None
        """
        totalsize = sum(self.sizes)
        if pos > self.totalsize:
            pos = totalsize
        self.pos = pos
        self.num, filename = self.getfileat(self.pos)
        return None

    def _inode(self):
        for path in self.files:
            stat = os.stat(path)
            yield stat.st_ino

    def _sizes(self):
        for path in self.files:
            stat = os.stat(path)
            yield stat.st_size

    def size(self):
        """Total size of all files included

        :returns: size in bytes
        :rtype: int
        """
        return sum(self.sizes)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def available(self):
        """
        :returns: number of bytes remaining
        :rtype: int
        """
        return self.size() - self.pos

    def __iter__(self):
        for line in self.readlines():
            yield line

    def currentfile(self):
        """
        Gets the current file.

        :returns: name of file at the current location
        :rtype: str
        """
        if len(self.files) == 0:
            return None
        return self.getfileat(self.pos)[1]

    def close(self):
        """Closes the multi-file handle"""
        pass
