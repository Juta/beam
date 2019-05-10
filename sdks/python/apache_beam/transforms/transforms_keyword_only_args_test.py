#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Unit tests for side inputs."""

from __future__ import absolute_import

import logging
import sys
import unittest

import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that
from apache_beam.testing.util import equal_to

@unittest.skipIf(sys.version_info[0] == 2,
                 'Keyword-Only Arguments are not supported in python 2')
# @unittest.skip('TODO BEAM-5878: support kwonly args in python 3')
class KeywordOnlyArgsTests(unittest.TestCase):
  # Enable nose tests running in parallel
  _multiprocess_can_split_ = True

  def test_side_input_keyword_only_args(self):
    pipeline = TestPipeline()

    # Keyword-only arguments are not available on Python 2
    # pylint: disable=syntax-error
    def sort_with_side_inputs(x, *s, reverse=False):
      for y in s:
        yield sorted([x] + y, reverse=reverse)

    pcol = pipeline | 'start' >> beam.Create([1, 2])
    side = pipeline | 'side' >> beam.Create([3, 4])  # 2 values in side input.
    result1 = pcol | 'compute1' >> beam.FlatMap(
        sort_with_side_inputs,
        beam.pvalue.AsList(side), reverse=True)
    assert_that(result1, equal_to([[4,3,1], [4,3,2]]), label='assert1')

    result2 = pcol | 'compute2' >> beam.FlatMap(
      sort_with_side_inputs,
      beam.pvalue.AsIter(side))
    assert_that(result2, equal_to([[1,3,4], [2,3,4]]), label='assert2')

    result3 = pcol | 'compute3' >> beam.FlatMap(
      sort_with_side_inputs)
    assert_that(result3, equal_to([]), label='assert3')

    result4 = pcol | 'compute4' >> beam.FlatMap(
      sort_with_side_inputs, reverse=True)
    assert_that(result4, equal_to([]), label='assert4')

    pipeline.run()

  def test_combine_keyword_only_args(self):
    pipeline = TestPipeline()

    # Keyword-only arguments are not available on Python 2
    # pylint: disable=syntax-error
    def bounded_sum(values, *s, bound=500):
      return min(sum(values) + sum(s), bound)

    pcoll = pipeline | 'start' >> beam.Create([6, 3, 1])
    result1 = pcoll | 'sum1' >> beam.CombineGlobally(bounded_sum, 5, 8, bound=20)
    result2 = pcoll | 'sum2' >> beam.CombineGlobally(bounded_sum, 5, 8)
    result3 = pcoll | 'sum3' >> beam.CombineGlobally(bounded_sum)
    result4 = pcoll | 'sum4' >> beam.CombineGlobally(bounded_sum, bound=12)

    assert_that(result1, equal_to([20]), label='assert1')
    assert_that(result2, equal_to([23]), label='assert2')
    assert_that(result3, equal_to([10]), label='assert3')
    assert_that(result4, equal_to([10]), label='assert4')

    pipeline.run()

  def test_do_fn_keyword_only_args(self):
    pipeline = TestPipeline()

    class MyDoFn(beam.DoFn):
      # Keyword-only arguments are not available on Python 2
      # pylint: disable=syntax-error
      def process(self, element, *s, bound=500):
        return [min(sum(s) + element, bound)]

    pcoll = pipeline | 'start' >> beam.Create([6, 3, 1])
    result1 = pcoll | 'sum1' >> beam.ParDo(MyDoFn(), 5, 8, bound=15)
    result2 = pcoll | 'sum2' >> beam.ParDo(MyDoFn(), 5, 8)
    result3 = pcoll | 'sum3' >> beam.ParDo(MyDoFn())
    result4 = pcoll | 'sum4' >> beam.ParDo(MyDoFn(), bound=10)

    assert_that(result1, equal_to([15,15,14]), label='assert1')
    assert_that(result2, equal_to([19,16,14]), label='assert2')
    assert_that(result3, equal_to([6,3,1]), label='assert3')
    assert_that(result4, equal_to([6,3,1]), label='assert4')
    pipeline.run()


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.DEBUG)
  unittest.main()
