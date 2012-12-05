mopen
=====

This small but powerful Python module allows for the reading of multiple files
as if they were one. File borders are managed transparently behind the
scenes allowing effortless reads across many files.

Currently, only reads are supported. The files are by default sorted
by the stat.ST_INO and stat.ST_SIZE. On Windows, ST_INO is not supported thus
the files will be sorted by size only.

Example
-------

Concatening files is simple...

.. code-block:: python

    from glob import glob
    from mopen import mopen
    
    if __name__ == '__main__':
    
        files = glob("./files/*.txt")
        with open("concat.txt", "w") as out:
            with mopen(files, "r") as fh:
                out.write(fh.read())
    
        print "Done."

Use Cases
---------

Besides the obvious concatenation usage, I've also used this
module in tandem with multiprocessing to read GBs of data across
several files by splitting the workload into managable chunks.
You can make quick work of lots data by using
process pools with each worker handling a portion of the 
data. This module removes the need to manage all of those files
separately by doing it for you.

Performance
-----------

* Performance overhead of ``mopen`` is very low
* However, reading lines one-by-one (ie. ``readline()``) is slow. Use ``readlines(size)`` whenever possible.
