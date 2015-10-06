#!/usr/bin/env python
# coding: utf-8
# coding: utf-8
#
#  Copyright 2015 by Leipzig University Library, http://ub.uni-leipzig.de
#                 by The Finc Authors, http://finc.info
#                 by Martin Czygan, <martin.czygan@uni-leipzig.de>
#
# This file is part of some open source application.
#
# Some open source application is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Some open source application is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#

"""
Format add-ons
==============

Format related functions and classes. Highlights: A TSV class, that helps
to work with tabular data.

Example:

    def run(self):
        with self.output().open('w') as output:
            output.write_tsv('Ubik', '1969', '67871286')

    def output(self):
        return luigi.LocalTarget(path=self.path(), format=TSV)

"""

from gluish.utils import random_string
import collections
import functools
import luigi

__all__ = ['TSV']

def write_tsv(output_stream, *tup):
    """
    Write argument list in `tup` out as a tab-separeated row to the stream.
    """
    output_stream.write('\t'.join([str(s) for s in tup]) + '\n')

def iter_tsv(input_stream, cols=None):
    """
    If a tuple is given in cols, use the elements as names to construct
    a namedtuple.

    Columns can be marked as ignored by using ``X`` or ``0`` as column name.

    Example (ignore the first four columns of a five column TSV):

    ::

        def run(self):
            with self.input().open() as handle:
                for row in handle.iter_tsv(cols=('X', 'X', 'X', 'X', 'iln')):
                    print(row.iln)
    """
    if cols:
        cols = [c if not c in ('x', 'X', 0, None) else random_string(length=5)
                for c in cols]
        Record = collections.namedtuple('Record', cols)
        for line in input_stream:
            yield Record._make(line.rstrip('\n').split('\t'))
    else:
        for line in input_stream:
            yield tuple(line.rstrip('\n').split('\t'))

class TSVFormat(luigi.format.Format):
    """
    A basic CSV/TSV format.
    Discussion: https://groups.google.com/forum/#!topic/luigi-user/F813st16xqw
    """
    def hdfs_reader(self, input_pipe):
        raise NotImplementedError()

    def hdfs_writer(self, output_pipe):
        raise NotImplementedError()

    def pipe_reader(self, input_pipe):
        input_pipe.iter_tsv = functools.partial(iter_tsv, input_pipe)
        return input_pipe

    def pipe_writer(self, output_pipe):
        output_pipe.write_tsv = functools.partial(write_tsv, output_pipe)
        return output_pipe

TSV = TSVFormat()
