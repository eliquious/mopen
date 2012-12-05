
mopen
=====

This small but powerful module allows for the reading of multiple files
as if they were one. File borders are merged transparently behind the
scenes allowing effortless reads across many files.

Currently, only reads are supported. The files are by default sorted
by the stat.ST_INO and stat.ST_SIZE. On Windows, ST_INO is not supported thus
the files will be sorted by size only.

.. code-block:: python

    import glob
    import mopen
    files = glob.glob("./path/to/files/*.txt")
    data = ""
    with mopen(files, "rb") as fh:
        data = fh.read()

Performance
-----------

* Performance overhead of ``mopen`` is very low
* However, reading lines one-by-one (ie. ``readline()``) is slow. Use ``readlines(size)`` whenever possible.
