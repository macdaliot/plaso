#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Systemd Journal parser."""

import unittest

from plaso.parsers import systemd_journal

from tests.parsers import test_lib


class SystemdJournalParserTest(test_lib.ParserTestCase):
  """Tests for the Systemd Journal parser."""

  def testParse(self):
    """Tests the Parse function."""
    parser = systemd_journal.SystemdJournalParser()
    storage_writer = self._ParseFile([
        'systemd', 'journal', 'system.journal'], parser)

    self.assertEqual(storage_writer.number_of_warnings, 0)
    self.assertEqual(storage_writer.number_of_events, 2101)

    events = list(storage_writer.GetEvents())

    expected_event_values = {
        'timestamp': '2017-01-27 09:40:55.913258'}

    self.CheckEventValues(storage_writer, events[0], expected_event_values)

    expected_message = (
        'test-VirtualBox [systemd, pid: 1] Started User Manager for '
        'UID 1000.')

    event_data = self._GetEventDataOfEvent(storage_writer, events[0])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_message)

    # This event uses XZ compressed data
    expected_event_values = {
        'timestamp': '2017-02-06 16:24:32.564585'}

    self.CheckEventValues(storage_writer, events[2098], expected_event_values)

    expected_message = 'test-VirtualBox [root, pid: 22921] {0:s}'.format(
        'a' * 692)
    expected_short_message = '{0:s}...'.format(expected_message[:77])

    event_data = self._GetEventDataOfEvent(storage_writer, events[2098])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_short_message)

  def testParseLZ4(self):
    """Tests the Parse function on a journal with LZ4 compressed events."""
    parser = systemd_journal.SystemdJournalParser()
    storage_writer = self._ParseFile([
        'systemd', 'journal', 'system.journal.lz4'], parser)

    self.assertEqual(storage_writer.number_of_warnings, 0)
    self.assertEqual(storage_writer.number_of_events, 85)

    events = list(storage_writer.GetEvents())

    expected_event_values = {
        'timestamp': '2018-07-03 15:00:16.682340'}

    self.CheckEventValues(storage_writer, events[0], expected_event_values)

    expected_message = 'testlol [systemd, pid: 822] Reached target Paths.'

    event_data = self._GetEventDataOfEvent(storage_writer, events[0])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_message)

    # This event uses LZ4 compressed data

    expected_event_values = {
        'timestamp': '2018-07-03 15:19:04.667807'}

    self.CheckEventValues(storage_writer, events[84], expected_event_values)

    # source: https://github.com/systemd/systemd/issues/6237
    # The text used in the test message was triplicated to make it long enough
    # to trigger the LZ4 compression.
    expected_message = (
        'testlol [test, pid: 34757]  textual user names.'+
        ('  Yes, as you found out 0day is not a valid username. I wonder which '
         'tool permitted you to create it in the first place. Note that not '
         'permitting numeric first characters is done on purpose: to avoid '
         'ambiguities between numeric UID and textual user names.'*3))
    expected_short_message = '{0:s}...'.format(expected_message[:77])

    event_data = self._GetEventDataOfEvent(storage_writer, events[84])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_short_message)

  def testParseDirty(self):
    """Tests the Parse function on a 'dirty' journal file."""
    storage_writer = self._CreateStorageWriter()
    parser_mediator = self._CreateParserMediator(storage_writer)
    parser = systemd_journal.SystemdJournalParser()

    path_segments = [
        'systemd', 'journal',
        'system@00053f9c9a4c1e0e-2e18a70e8b327fed.journalTILDE']
    file_entry = self._GetTestFileEntry(path_segments)
    file_object = file_entry.GetFileObject()

    parser.ParseFileObject(parser_mediator, file_object)

    self.assertEqual(storage_writer.number_of_warnings, 1)
    self.assertEqual(storage_writer.number_of_events, 2211)

    events = list(storage_writer.GetEvents())

    expected_event_values = {
        'timestamp': '2016-10-24 13:20:01.063423'}

    self.CheckEventValues(storage_writer, events[0], expected_event_values)

    expected_message = (
        'test-VirtualBox [systemd-journald, pid: 569] Runtime journal '
        '(/run/log/journal/) is 1.2M, max 9.9M, 8.6M free.')
    expected_short_message = '{0:s}...'.format(expected_message[:77])

    event_data = self._GetEventDataOfEvent(storage_writer, events[0])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_short_message)

    self.assertEqual(storage_writer.number_of_warnings, 1)

    warnings = list(storage_writer.GetExtractionWarnings())
    warning = warnings[0]
    expected_warning_message = (
        'Unable to parse journal entry at offset: 0x0041bfb0 with error: '
        'object offset should be after hash tables (0 < 2527472)')
    self.assertEqual(warning.message, expected_warning_message)


if __name__ == '__main__':
  unittest.main()
