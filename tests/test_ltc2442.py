#!/usr/bin/env python

"""Tests for `ltc2442` package."""


import unittest
import sys
import mock

from ltc2442 import ltc2442





class TestLtc2442(unittest.TestCase):
    """Tests for `ltc2442` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

  #  def test_open(self):
#        sys.modules['spidev'] = mock.MagicMock()

#        l = ltc2442.ltc2442(0, 1)
#        l.open()


    def test_readsingleended(self):
        l = ltc2442.ltc2442(0, 1)
        l.open()
#        l.set_osr_speed(4,2)
        l.read_single(0)
        l.read_single(0)
        l.read_single(0)
        print "Results=",l._rawdata, l._adc_code
        v=l.code_to_voltage()
        print "Results=",v
        l.close()
        
    def test_differential(self):
        l = ltc2442.ltc2442(0, 1)
        l.open()
#        l.set_osr_speed(4,2)
        l.read_differential(0,1)
        l.read_differential(0,1)
        l.read_differential(0,1)

        print "Results=",l._rawdata, l._adc_code
        v=l.code_to_voltage()
        print "Results=",v
        l.close()


