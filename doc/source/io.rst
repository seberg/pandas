
.. _io:

.. currentmodule:: pandas

.. ipython:: python
   :suppress:

   import os
   import csv
   from StringIO import StringIO

   import numpy as np
   np.random.seed(123456)
   randn = np.random.randn
   np.set_printoptions(precision=4, suppress=True)

   import matplotlib.pyplot as plt
   plt.close('all')

   from pandas import *
   import pandas.util.testing as tm
   clipdf = DataFrame({'A':[1,2,3],'B':[4,5,6],'C':['p','q','r']},
                      index=['x','y','z'])

*******************************
IO Tools (Text, CSV, HDF5, ...)
*******************************

Clipboard
---------

.. _io.clipboard:

A handy way to grab data is to use the ``read_clipboard`` method, which takes
the contents of the clipboard buffer and passes them to the ``read_table``
method described in the next section. For instance, you can copy the following
text to the clipboard (CTRL-C on many operating systems):

.. code-block:: python

     A B C
   x 1 4 p
   y 2 5 q
   z 3 6 r

And then import the data directly to a DataFrame by calling:

.. code-block:: python

   clipdf = read_clipboard(sep='\s*')

.. ipython:: python

   clipdf

.. _io.read_csv_table:

CSV & Text files
----------------

The two workhorse functions for reading text files (a.k.a. flat files) are
:func:`~pandas.io.parsers.read_csv` and :func:`~pandas.io.parsers.read_table`.
They both use the same parsing code to intelligently convert tabular
data into a DataFrame object. They can take a number of arguments:

  - ``filepath_or_buffer``: Either a string path to a file, or any object with a
    ``read`` method (such as an open file or ``StringIO``).
  - ``sep`` or ``delimiter``: A delimiter / separator to split fields
    on. `read_csv` is capable of inferring the delimiter automatically in some
    cases by "sniffing." The separator may be specified as a regular
    expression; for instance you may use '\s*' to indicate arbitrary
    whitespace.
  - ``dialect``: string or :class:`python:csv.Dialect` instance to expose more ways to specify
    the file format
  - ``header``: row number to use as the column names, and the start of the data.
    Defaults to 0 (first row); specify None if there is no header row.
  - ``skiprows``: A collection of numbers for rows in the file to skip. Can
    also be an integer to skip the first ``n`` rows
  - ``index_col``: column number, column name, or list of column numbers/names,
    to use as the ``index`` (row labels) of the resulting DataFrame. By default,
    it will number the rows without using any column, unless there is one more
    data column than there are headers, in which case the first column is taken
    as the index.
  - ``names``: List of column names to use. If file contains no header row,
    then you should explicitly pass header=None (behavior changed in v0.10.0).
  - ``na_values``: optional list of strings to recognize as NaN (missing
    values), either in addition to or in lieu of the default set.
  - ``keep_default_na``: whether to include the default set of missing values
    in addition to the ones specified in ``na_values``
  - ``parse_dates``: if True then index will be parsed as dates
    (False by default). You can specify more complicated options to parse
    a subset of columns or a combination of columns into a single date column
    (list of ints or names, list of lists, or dict)
    [1, 2, 3] -> try parsing columns 1, 2, 3 each as a separate date column
    [[1, 3]] -> combine columns 1 and 3 and parse as a single date column
    {'foo' : [1, 3]} -> parse columns 1, 3 as date and call result 'foo'
  - ``keep_date_col``: if True, then date component columns passed into
    ``parse_dates`` will be retained in the output (False by default).
  - ``date_parser``: function to use to parse strings into datetime
    objects. If ``parse_dates`` is True, it defaults to the very robust
    ``dateutil.parser``. Specifying this implicitly sets ``parse_dates`` as True.
    You can also use functions from community supported date converters from
    date_converters.py
  - ``dayfirst``: if True then uses the DD/MM international/European date format
    (This is False by default)
  - ``thousands``: sepcifies the thousands separator. If not None, then parser
    will try to look for it in the output and parse relevant data to integers.
    Because it has to essentially scan through the data again, this causes a
    significant performance hit so only use if necessary.
  - ``comment``: denotes the start of a comment and ignores the rest of the line.
    Currently line commenting is not supported.
  - ``nrows``: Number of rows to read out of the file. Useful to only read a
    small portion of a large file
  - ``iterator``: If True, return a ``TextParser`` to enable reading a file
    into memory piece by piece
  - ``chunksize``: An number of rows to be used to "chunk" a file into
    pieces. Will cause an ``TextParser`` object to be returned. More on this
    below in the section on :ref:`iterating and chunking <io.chunking>`
  - ``skip_footer``: number of lines to skip at bottom of file (default 0)
  - ``converters``: a dictionary of functions for converting values in certain
    columns, where keys are either integers or column labels
  - ``encoding``: a string representing the encoding to use if the contents are
    non-ascii
  - ``verbose``: show number of NA values inserted in non-numeric columns
  - ``squeeze``: if True then output with only one column is turned into Series

.. ipython:: python
   :suppress:

   f = open('foo.csv','w')
   f.write('date,A,B,C\n20090101,a,1,2\n20090102,b,3,4\n20090103,c,4,5')
   f.close()

Consider a typical CSV file containing, in this case, some time series data:

.. ipython:: python

   print open('foo.csv').read()

The default for `read_csv` is to create a DataFrame with simple numbered rows:

.. ipython:: python

   read_csv('foo.csv')

In the case of indexed data, you can pass the column number or column name you
wish to use as the index:

.. ipython:: python

   read_csv('foo.csv', index_col=0)

.. ipython:: python

   read_csv('foo.csv', index_col='date')

You can also use a list of columns to create a hierarchical index:

.. ipython:: python

   read_csv('foo.csv', index_col=[0, 'A'])

.. _io.dialect:

The ``dialect`` keyword gives greater flexibility in specifying the file format.
By default it uses the Excel dialect but you can specify either the dialect name
or a :class:`python:csv.Dialect` instance.

.. ipython:: python
   :suppress:

   data = ('label1,label2,label3\n'
           'index1,"a,c,e\n'
           'index2,b,d,f')

Suppose you had data with unenclosed quotes:

.. ipython:: python

   print data

By default, ``read_csv`` uses the Excel dialect and treats the double quote as
the quote character, which causes it to fail when it finds a newline before it
finds the closing double quote.

We can get around this using ``dialect``

.. ipython:: python

   dia = csv.excel()
   dia.quoting = csv.QUOTE_NONE
   read_csv(StringIO(data), dialect=dia)

The parsers make every attempt to "do the right thing" and not be very
fragile. Type inference is a pretty big deal. So if a column can be coerced to
integer dtype without altering the contents, it will do so. Any non-numeric
columns will come through as object dtype as with the rest of pandas objects.

.. _io.parse_dates:

Specifying Date Columns
~~~~~~~~~~~~~~~~~~~~~~~

To better facilitate working with datetime data, :func:`~pandas.io.parsers.read_csv` and :func:`~pandas.io.parsers.read_table`
uses the keyword arguments ``parse_dates`` and ``date_parser`` to allow users
to specify a variety of columns and date/time formats to turn the input text
data into ``datetime`` objects.

The simplest case is to just pass in ``parse_dates=True``:

.. ipython:: python

   # Use a column as an index, and parse it as dates.
   df = read_csv('foo.csv', index_col=0, parse_dates=True)
   df

   # These are python datetime objects
   df.index

.. ipython:: python
   :suppress:

   os.remove('foo.csv')

It is often the case that we may want to store date and time data separately,
or store various date fields separately. the ``parse_dates`` keyword can be
used to specify a combination of columns to parse the dates and/or times from.

You can specify a list of column lists to ``parse_dates``, the resulting date
columns will be prepended to the output (so as to not affect the existing column
order) and the new column names will be the concatenation of the component
column names:

.. ipython:: python
   :suppress:

   data =  ("KORD,19990127, 19:00:00, 18:56:00, 0.8100\n"
            "KORD,19990127, 20:00:00, 19:56:00, 0.0100\n"
            "KORD,19990127, 21:00:00, 20:56:00, -0.5900\n"
            "KORD,19990127, 21:00:00, 21:18:00, -0.9900\n"
            "KORD,19990127, 22:00:00, 21:56:00, -0.5900\n"
            "KORD,19990127, 23:00:00, 22:56:00, -0.5900")

   with open('tmp.csv', 'w') as fh:
       fh.write(data)

.. ipython:: python

    print open('tmp.csv').read()
    df = read_csv('tmp.csv', header=None, parse_dates=[[1, 2], [1, 3]])
    df

By default the parser removes the component date columns, but you can choose
to retain them via the ``keep_date_col`` keyword:

.. ipython:: python

   df = read_csv('tmp.csv', header=None, parse_dates=[[1, 2], [1, 3]],
                 keep_date_col=True)
   df

Note that if you wish to combine multiple columns into a single date column, a
nested list must be used. In other words, ``parse_dates=[1, 2]`` indicates that
the second and third columns should each be parsed as separate date columns
while ``parse_dates=[[1, 2]]`` means the two columns should be parsed into a
single column.

You can also use a dict to specify custom name columns:

.. ipython:: python

   date_spec = {'nominal': [1, 2], 'actual': [1, 3]}
   df = read_csv('tmp.csv', header=None, parse_dates=date_spec)
   df

It is important to remember that if multiple text columns are to be parsed into
a single date column, then a new column is prepended to the data. The `index_col`
specification is based off of this new set of columns rather than the original
data columns:


.. ipython:: python

   date_spec = {'nominal': [1, 2], 'actual': [1, 3]}
   df = read_csv('tmp.csv', header=None, parse_dates=date_spec,
                 index_col=0) #index is the nominal column
   df

**Note**: When passing a dict as the `parse_dates` argument, the order of
the columns prepended is not guaranteed, because `dict` objects do not impose
an ordering on their keys. On Python 2.7+ you may use `collections.OrderedDict`
instead of a regular `dict` if this matters to you. Because of this, when using a
dict for 'parse_dates' in conjunction with the `index_col` argument, it's best to
specify `index_col` as a column label rather then as an index on the resulting frame.

Date Parsing Functions
~~~~~~~~~~~~~~~~~~~~~~
Finally, the parser allows you can specify a custom ``date_parser`` function to
take full advantage of the flexiblity of the date parsing API:

.. ipython:: python

   import pandas.io.date_converters as conv
   df = read_csv('tmp.csv', header=None, parse_dates=date_spec,
                 date_parser=conv.parse_date_time)
   df

You can explore the date parsing functionality in ``date_converters.py`` and
add your own. We would love to turn this module into a community supported set
of date/time parsers. To get you started, ``date_converters.py`` contains
functions to parse dual date and time columns, year/month/day columns,
and year/month/day/hour/minute/second columns. It also contains a
``generic_parser`` function so you can curry it with a function that deals with
a single date rather than the entire array.

.. ipython:: python
   :suppress:

   os.remove('tmp.csv')

.. _io.dayfirst:

International Date Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~
While US date formats tend to be MM/DD/YYYY, many international formats use
DD/MM/YYYY instead. For convenience, a ``dayfirst`` keyword is provided:

.. ipython:: python
   :suppress:

   data = "date,value,cat\n1/6/2000,5,a\n2/6/2000,10,b\n3/6/2000,15,c"
   with open('tmp.csv', 'w') as fh:
        fh.write(data)

.. ipython:: python

   print open('tmp.csv').read()

   read_csv('tmp.csv', parse_dates=[0])

   read_csv('tmp.csv', dayfirst=True, parse_dates=[0])

.. _io.thousands:

Thousand Separators
~~~~~~~~~~~~~~~~~~~
For large integers that have been written with a thousands separator, you can
set the ``thousands`` keyword to ``True`` so that integers will be parsed
correctly:

.. ipython:: python
   :suppress:

   data =  ("ID|level|category\n"
            "Patient1|123,000|x\n"
            "Patient2|23,000|y\n"
            "Patient3|1,234,018|z")

   with open('tmp.csv', 'w') as fh:
       fh.write(data)

By default, integers with a thousands separator will be parsed as strings

.. ipython:: python

    print open('tmp.csv').read()
    df = read_csv('tmp.csv', sep='|')
    df

    df.level.dtype

The ``thousands`` keyword allows integers to be parsed correctly

.. ipython:: python

    print open('tmp.csv').read()
    df = read_csv('tmp.csv', sep='|', thousands=',')
    df

    df.level.dtype

.. ipython:: python
   :suppress:

   os.remove('tmp.csv')

.. _io.comments:

Comments
~~~~~~~~
Sometimes comments or meta data may be included in a file:

.. ipython:: python
   :suppress:

   data =  ("ID,level,category\n"
            "Patient1,123000,x # really unpleasant\n"
            "Patient2,23000,y # wouldn't take his medicine\n"
            "Patient3,1234018,z # awesome")

   with open('tmp.csv', 'w') as fh:
       fh.write(data)

.. ipython:: python

   print open('tmp.csv').read()

By default, the parse includes the comments in the output:

.. ipython:: python

   df = read_csv('tmp.csv')
   df

We can suppress the comments using the ``comment`` keyword:

.. ipython:: python

   df = read_csv('tmp.csv', comment='#')
   df

.. ipython:: python
   :suppress:

   os.remove('tmp.csv')

Returning Series
~~~~~~~~~~~~~~~~

Using the ``squeeze`` keyword, the parser will return output with a single column
as a ``Series``:

.. ipython:: python
   :suppress:

   data =  ("level\n"
            "Patient1,123000\n"
            "Patient2,23000\n"
            "Patient3,1234018")

   with open('tmp.csv', 'w') as fh:
       fh.write(data)

.. ipython:: python

   print open('tmp.csv').read()

   output =  read_csv('tmp.csv', squeeze=True)
   output

   type(output)

.. ipython:: python
   :suppress:

   os.remove('tmp.csv')

.. _io.fwf:

Files with Fixed Width Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
While `read_csv` reads delimited data, the :func:`~pandas.io.parsers.read_fwf`
function works with data files that have known and fixed column widths.
The function parameters to `read_fwf` are largely the same as `read_csv` with
two extra parameters:

  - ``colspecs``: a list of pairs (tuples), giving the extents of the
    fixed-width fields of each line as half-open intervals [from, to[
  - ``widths``: a list of field widths, which can be used instead of
    ``colspecs`` if the intervals are contiguous

.. ipython:: python
   :suppress:

   f = open('bar.csv', 'w')
   data1 = ("id8141    360.242940   149.910199   11950.7\n"
            "id1594    444.953632   166.985655   11788.4\n"
            "id1849    364.136849   183.628767   11806.2\n"
            "id1230    413.836124   184.375703   11916.8\n"
            "id1948    502.953953   173.237159   12468.3")
   f.write(data1)
   f.close()

Consider a typical fixed-width data file:

.. ipython:: python

   print open('bar.csv').read()

In order to parse this file into a DataFrame, we simply need to supply the
column specifications to the `read_fwf` function along with the file name:

.. ipython:: python

   #Column specifications are a list of half-intervals
   colspecs = [(0, 6), (8, 20), (21, 33), (34, 43)]
   df = read_fwf('bar.csv', colspecs=colspecs, header=None, index_col=0)
   df

Note how the parser automatically picks column names X.<column number> when
``header=None`` argument is specified. Alternatively, you can supply just the
column widths for contiguous columns:

.. ipython:: python

   #Widths are a list of integers
   widths = [6, 14, 13, 10]
   df = read_fwf('bar.csv', widths=widths, header=None)
   df

The parser will take care of extra white spaces around the columns
so it's ok to have extra separation between the columns in the file.

.. ipython:: python
   :suppress:

   os.remove('bar.csv')

Files with an "implicit" index column
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ipython:: python
   :suppress:

   f = open('foo.csv', 'w')
   f.write('A,B,C\n20090101,a,1,2\n20090102,b,3,4\n20090103,c,4,5')
   f.close()

Consider a file with one less entry in the header than the number of data
column:

.. ipython:: python

   print open('foo.csv').read()

In this special case, ``read_csv`` assumes that the first column is to be used
as the index of the DataFrame:

.. ipython:: python

   read_csv('foo.csv')

Note that the dates weren't automatically parsed. In that case you would need
to do as before:

.. ipython:: python

   df = read_csv('foo.csv', parse_dates=True)
   df.index

.. ipython:: python
   :suppress:

   os.remove('foo.csv')


Reading DataFrame objects with ``MultiIndex``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _io.csv_multiindex:

Suppose you have data indexed by two columns:

.. ipython:: python

   print open('data/mindex_ex.csv').read()

The ``index_col`` argument to ``read_csv`` and ``read_table`` can take a list of
column numbers to turn multiple columns into a ``MultiIndex``:

.. ipython:: python

   df = read_csv("data/mindex_ex.csv", index_col=[0,1])
   df
   df.ix[1978]

.. _io.sniff:

Automatically "sniffing" the delimiter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``read_csv`` is capable of inferring delimited (not necessarily
comma-separated) files. YMMV, as pandas uses the :class:`python:csv.Sniffer`
class of the csv module.

.. ipython:: python
   :suppress:

   df = DataFrame(np.random.randn(10, 4))
   df.to_csv('tmp.sv', sep='|')
   df.to_csv('tmp2.sv', sep=':')

.. ipython:: python

    print open('tmp2.sv').read()
    read_csv('tmp2.sv')

.. _io.chunking:

Iterating through files chunk by chunk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose you wish to iterate through a (potentially very large) file lazily
rather than reading the entire file into memory, such as the following:


.. ipython:: python

   print open('tmp.sv').read()
   table = read_table('tmp.sv', sep='|')
   table


By specifiying a ``chunksize`` to ``read_csv`` or ``read_table``, the return
value will be an iterable object of type ``TextParser``:

.. ipython:: python

   reader = read_table('tmp.sv', sep='|', chunksize=4)
   reader

   for chunk in reader:
       print chunk


Specifying ``iterator=True`` will also return the ``TextParser`` object:

.. ipython:: python

   reader = read_table('tmp.sv', sep='|', iterator=True)
   reader.get_chunk(5)

.. ipython:: python
   :suppress:

   os.remove('tmp.sv')
   os.remove('tmp2.sv')

Writing to CSV format
~~~~~~~~~~~~~~~~~~~~~

.. _io.store_in_csv:

The Series and DataFrame objects have an instance method ``to_csv`` which
allows storing the contents of the object as a comma-separated-values file. The
function takes a number of arguments. Only the first is required.

  - ``path``: A string path to the file to write
    ``nanRep``: A string representation of a missing value (default '')
  - ``cols``: Columns to write (default None)
  - ``header``: Whether to write out the column names (default True)
  - ``index``: whether to write row (index) names (default True)
  - ``index_label``: Column label(s) for index column(s) if desired. If None
    (default), and `header` and `index` are True, then the index names are
    used. (A sequence should be given if the DataFrame uses MultiIndex).
  - ``mode`` : Python write mode, default 'w'
  - ``sep`` : Field delimiter for the output file (default ",")
  - ``encoding``: a string representing the encoding to use if the contents are
    non-ascii, for python versions prior to 3

Writing a formatted string
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _io.formatting:

The DataFrame object has an instance method ``to_string`` which allows control
over the string representation of the object. All arguments are optional:

  - ``buf`` default None, for example a StringIO object
  - ``columns`` default None, which columns to write
  - ``col_space`` default None, minimum width of each column.
  - ``na_rep`` default ``NaN``, representation of NA value
  - ``formatters`` default None, a dictionary (by column) of functions each of
    which takes a single argument and returns a formatted string
  - ``float_format`` default None, a function which takes a single (float)
    argument and returns a formatted string; to be applied to floats in the
    DataFrame.
  - ``sparsify`` default True, set to False for a DataFrame with a hierarchical
    index to print every multiindex key at each row.
  - ``index_names`` default True, will print the names of the indices
  - ``index`` default True, will print the index (ie, row labels)
  - ``header`` default True, will print the column labels
  - ``justify`` default ``left``, will print column headers left- or
    right-justified

The Series object also has a ``to_string`` method, but with only the ``buf``,
``na_rep``, ``float_format`` arguments. There is also a ``length`` argument
which, if set to ``True``, will additionally output the length of the Series.


Writing to HTML format
~~~~~~~~~~~~~~~~~~~~~~

.. _io.html:

DataFrame object has an instance method ``to_html`` which renders the contents
of the DataFrame as an html table. The function arguments are as in the method
``to_string`` described above.


Excel files
----------------

The ``ExcelFile`` class can read an Excel 2003 file using the ``xlrd`` Python
module and use the same parsing code as the above to convert tabular data into
a DataFrame. To use it, create the ``ExcelFile`` object:

.. code-block:: python

   xls = ExcelFile('path_to_file.xls')

Then use the ``parse`` instance method with a sheetname, then use the same
additional arguments as the parsers above:

.. code-block:: python

   xls.parse('Sheet1', index_col=None, na_values=['NA'])

To read sheets from an Excel 2007 file, you can pass a filename with a ``.xlsx``
extension, in which case the ``openpyxl`` module will be used to read the file.

It is often the case that users will insert columns to do temporary computations
in Excel and you may not want to read in those columns. `ExcelFile.parse` takes
a `parse_cols` keyword to allow you to specify a subset of columns to parse.

If `parse_cols` is an integer, then it is assumed to indicate the last column
to be parsed.

.. code-block:: python

   xls.parse('Sheet1', parse_cols=2, index_col=None, na_values=['NA'])

If `parse_cols` is a list of integers, then it is assumed to be the file column
indices to be parsed.

.. code-block:: python

   xls.parse('Sheet1', parse_cols=[0, 2, 3], index_col=None, na_values=['NA'])

To write a DataFrame object to a sheet of an Excel file, you can use the
``to_excel`` instance method.  The arguments are largely the same as ``to_csv``
described above, the first argument being the name of the excel file, and the
optional second argument the name of the sheet to which the DataFrame should be
written.  For example:

.. code-block:: python

   df.to_excel('path_to_file.xlsx', sheet_name='sheet1')

Files with a ``.xls`` extension will be written using ``xlwt`` and those with
a ``.xlsx`` extension will be written using ``openpyxl``.
The Panel class also has a ``to_excel`` instance method,
which writes each DataFrame in the Panel to a separate sheet.

In order to write separate DataFrames to separate sheets in a single Excel file,
one can use the ExcelWriter class, as in the following example:

.. code-block:: python

   writer = ExcelWriter('path_to_file.xlsx')
   df1.to_excel(writer, sheet_name='sheet1')
   df2.to_excel(writer, sheet_name='sheet2')
   writer.save()

.. _io-hdf5:

HDF5 (PyTables)
---------------

``HDFStore`` is a dict-like object which reads and writes pandas to the high
performance HDF5 format using the excellent `PyTables
<http://www.pytables.org/>`__ library.

.. ipython:: python
   :suppress:
   :okexcept:

   os.remove('store.h5')

.. ipython:: python

   store = HDFStore('store.h5')
   print store

Objects can be written to the file just like adding key-value pairs to a dict:

.. ipython:: python

   index = date_range('1/1/2000', periods=8)
   s = Series(randn(5), index=['a', 'b', 'c', 'd', 'e'])
   df = DataFrame(randn(8, 3), index=index,
                  columns=['A', 'B', 'C'])
   wp = Panel(randn(2, 5, 4), items=['Item1', 'Item2'],
              major_axis=date_range('1/1/2000', periods=5),
              minor_axis=['A', 'B', 'C', 'D'])

   # store.put('s', s) is an equivalent method
   store['s'] = s

   store['df'] = df

   store['wp'] = wp

   # the type of stored data
   store.handle.root.wp._v_attrs.pandas_type

   store

In a current or later Python session, you can retrieve stored objects:

.. ipython:: python

   # store.get('df') is an equivalent method
   store['df']

Deletion of the object specified by the key

.. ipython:: python

   # store.remove('wp') is an equivalent method
   del store['wp']

   store

.. ipython:: python
   :suppress:

   store.close()
   import os
   os.remove('store.h5')


These stores are **not** appendable once written (though you can simply remove them and rewrite). Nor are they **queryable**; they must be retrieved in their entirety.


Storing in Table format
~~~~~~~~~~~~~~~~~~~~~~~

``HDFStore`` supports another ``PyTables`` format on disk, the ``table`` format. Conceptually a ``table`` is shaped
very much like a DataFrame, with rows and columns. A ``table`` may be appended to in the same or other sessions.
In addition, delete & query type operations are supported. You can create an index with ``create_table_index``
after data is already in the table (this may become automatic in the future or an option on appending/putting a ``table``).

.. ipython:: python
   :suppress:
   :okexcept:

   os.remove('store.h5')

.. ipython:: python

   store = HDFStore('store.h5')
   df1 = df[0:4]
   df2 = df[4:]

   # append data (creates a table automatically)
   store.append('df', df1)
   store.append('df', df2)
   store

   # select the entire object
   store.select('df')

   # the type of stored data
   store.handle.root.df._v_attrs.pandas_type

   # create an index
   store.create_table_index('df')
   store.handle.root.df.table

Hierarchical Keys
~~~~~~~~~~~~~~~~~

Keys to a store can be specified as a string. These can be in a hierarchical path-name like format (e.g. ``foo/bar/bah``), which will generate a hierarchy of sub-stores (or ``Groups`` in PyTables parlance). Keys can be specified with out the leading '/' and are ALWAYS absolute (e.g. 'foo' refers to '/foo'). Removal operations can remove everying in the sub-store and BELOW, so be *careful*.

.. ipython:: python

   store.put('foo/bar/bah', df)
   store.append('food/orange', df)
   store.append('food/apple',  df)
   store

   # a list of keys are returned
   store.keys()

   # remove all nodes under this level
   store.remove('food')
   store

Storing Mixed Types in a Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Storing mixed-dtype data is supported. Strings are store as a fixed-width using the maximum size of the appended column. Subsequent appends will truncate strings at this length.
Passing ``min_itemsize = { column_name : size }`` as a paremeter to append will set a larger minimum for the column. Storing ``floats, strings, ints, bools`` are currently supported.

.. ipython:: python

    df_mixed             = df.copy()
    df_mixed['string']   = 'string'
    df_mixed['int']      = 1
    df_mixed['bool']     = True

    store.append('df_mixed',df_mixed)
    df_mixed1 = store.select('df_mixed')
    df_mixed1
    df_mixed1.get_dtype_counts()


Querying a Table
~~~~~~~~~~~~~~~~

``select`` and ``delete`` operations have an optional criteria that can be specified to select/delete only
a subset of the data. This allows one to have a very large on-disk table and retrieve only a portion of the data.

A query is specified using the ``Term`` class under the hood.

   - 'index' and 'column' are supported indexers of a DataFrame
   - 'major_axis' and 'minor_axis' are supported indexers of the Panel

Valid terms can be created from ``dict, list, tuple, or string``. Objects can be embeded as values. Allowed operations are: ``<, <=, >, >=, =``. ``=`` will be inferred as an implicit set operation (e.g. if 2 or more values are provided). The following are all valid terms.

       - ``dict(field = 'index', op = '>', value = '20121114')``
       - ``('index', '>', '20121114')``
       - ``'index>20121114'``
       - ``('index', '>', datetime(2012,11,14))``
       - ``('index', ['20121114','20121115'])``
       - ``('major', '=', Timestamp('2012/11/14'))``
       - ``('minor_axis', ['A','B'])``

Queries are built up using a list of ``Terms`` (currently only **anding** of terms is supported). An example query for a panel might be specified as follows.
``['major_axis>20000102', ('minor_axis', '=', ['A','B']) ]``. This is roughly translated to: `major_axis must be greater than the date 20000102 and the minor_axis must be A or B`

.. ipython:: python

   store.append('wp',wp)
   store.select('wp',[ 'major_axis>20000102', ('minor_axis', '=', ['A','B']) ])

Delete from a Table
~~~~~~~~~~~~~~~~~~~

.. ipython:: python

   store.remove('wp', 'index>20000102' )
   store.select('wp')

Notes & Caveats
~~~~~~~~~~~~~~~

   - Selection by items (the top level panel dimension) is not possible; you always get all of the items in the returned Panel
   - Once a ``table`` is created its items (Panel) / columns (DataFrame) are fixed; only exactly the same columns can be appended
   - You can not append/select/delete to a non-table (table creation is determined on the first append, or by passing ``table=True`` in a put operation)
   - ``PyTables`` only supports fixed-width string columns in ``tables``. The sizes of a string based indexing column (e.g. *column* or *minor_axis*) are determined as the maximum size of the elements in that axis or by passing the parameter ``min_itemsize`` on the first table creation (``min_itemsize`` can be an integer or a dict of column name to an integer). If subsequent appends introduce elements in the indexing axis that are larger than the supported indexer, an Exception will be raised (otherwise you could have a silent truncation of these indexers, leading to loss of information). This is **ONLY** necessary for storing ``Panels`` (as the indexing column is stored directly in a column)

     .. ipython:: python

        store.append('wp_big_strings', wp, min_itemsize = 30)
	wp = wp.rename_axis(lambda x: x + '_big_strings', axis=2)
        store.append('wp_big_strings', wp)
        store.select('wp_big_strings')


Performance
~~~~~~~~~~~

   - ``Tables`` come with a performance penalty as compared to regular stores. The benefit is the ability to append/delete and query (potentially very large amounts of data).
     Write times are generally longer as compared with regular stores. Query times can be quite fast, especially on an indexed axis.
   - ``Tables`` can (as of 0.10.0) be expressed as different types.

     - ``AppendableTable`` which is a similiar table to past versions (this is the default).
     - ``WORMTable`` (pending implementation) - is available to faciliate very fast writing of tables that are also queryable (but CANNOT support appends)

   - To delete a lot of data, it is sometimes better to erase the table and rewrite it. ``PyTables`` tends to increase the file size with deletions
   - In general it is best to store Panels with the most frequently selected dimension in the minor axis and a time/date like dimension in the major axis, but this is not required. Panels can have any major_axis and minor_axis type that is a valid Panel indexer.
   - No dimensions are currently indexed automagically (in the ``PyTables`` sense); these require an explict call to ``create_table_index``
   - ``Tables`` offer better performance when compressed after writing them (as opposed to turning on compression at the very beginning)
     use the pytables utilities ``ptrepack`` to rewrite the file (and also can change compression methods)
   - Duplicate rows can be written, but are filtered out in selection (with the last items being selected; thus a table is unique on major, minor pairs)

.. ipython:: python
   :suppress:

   store.close()
   import os
   os.remove('store.h5')
