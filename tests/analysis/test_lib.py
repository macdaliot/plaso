# -*- coding: utf-8 -*-
"""Analysis plugin related functions and classes for testing."""

from __future__ import unicode_literals

from plaso.analysis import mediator as analysis_mediator
from plaso.containers import artifacts
from plaso.containers import events
from plaso.containers import sessions
from plaso.engine import knowledge_base
from plaso.parsers import interface as parsers_interface
from plaso.parsers import mediator as parsers_mediator
from plaso.storage.fake import writer as fake_writer

from tests import test_lib as shared_test_lib


class AnalysisPluginTestCase(shared_test_lib.BaseTestCase):
  """The unit test case for an analysis plugin."""

  def _AnalyzeEvents(self, test_events, plugin, knowledge_base_values=None):
    """Analyzes events using the analysis plugin.

    Args:
      test_events (list[tuple[EventObject, EventData]]]): events to analyze.
      plugin (AnalysisPlugin): plugin.
      knowledge_base_values (Optional[dict[str, str]]): knowledge base values.

    Returns:
      FakeStorageWriter: storage writer.
    """
    knowledge_base_object = self._SetUpKnowledgeBase(
        knowledge_base_values=knowledge_base_values)

    session = sessions.Session()
    storage_writer = fake_writer.FakeStorageWriter(session)
    storage_writer.Open()
    for event, event_data in test_events:
      storage_writer.AddEventData(event_data)

      event.SetEventDataIdentifier(event_data.GetIdentifier())
      storage_writer.AddEvent(event)

    mediator = analysis_mediator.AnalysisMediator(
        storage_writer, knowledge_base_object)

    for event, event_data in test_events:
      plugin.ExamineEvent(mediator, event, event_data)

    analysis_report = plugin.CompileReport(mediator)
    storage_writer.AddAnalysisReport(analysis_report)

    return storage_writer

  def _CreateTestEvent(self, event_values):
    """Create a test event and event data.

    Args:
      event_values (dict[str, str]): event values.

    Returns:
      tuple[EventObject, WindowsRegistryServiceEventData]: event and event
          data for testing.
    """
    copy_of_event_values = dict(event_values)

    timestamp = copy_of_event_values.get('timestamp', None)
    if 'timestamp' in copy_of_event_values:
      del copy_of_event_values['timestamp']

    timestamp_desc = copy_of_event_values.get('timestamp_desc', None)
    if 'timestamp_desc' in copy_of_event_values:
      del copy_of_event_values['timestamp_desc']

    event = events.EventObject()
    event.timestamp = timestamp
    event.timestamp_desc = timestamp_desc

    event_data = events.EventData()
    event_data.CopyFromDict(copy_of_event_values)

    return event, event_data

  def _ParseAndAnalyzeFile(
      self, path_segments, parser, plugin, knowledge_base_values=None):
    """Parses and analyzes a file using the parser and analysis plugin.

    Args:
      path_segments (list[str]): path segments inside the test data directory.
      parser (BaseParser): parser.
      plugin (AnalysisPlugin): plugin.
      knowledge_base_values (Optional[dict[str, str]]): knowledge base values.

    Returns:
      FakeStorageWriter: storage writer.
    """
    knowledge_base_object = self._SetUpKnowledgeBase(
        knowledge_base_values=knowledge_base_values)

    storage_writer = self._ParseFile(
        path_segments, parser, knowledge_base_object)

    mediator = analysis_mediator.AnalysisMediator(
        storage_writer, knowledge_base_object)

    for event in storage_writer.GetSortedEvents():
      event_data = None
      event_data_identifier = event.GetEventDataIdentifier()
      if event_data_identifier:
        event_data = storage_writer.GetEventDataByIdentifier(
            event_data_identifier)

      plugin.ExamineEvent(mediator, event, event_data)

    analysis_report = plugin.CompileReport(mediator)
    storage_writer.AddAnalysisReport(analysis_report)

    return storage_writer

  def _ParseFile(self, path_segments, parser, knowledge_base_object):
    """Parses a file using the parser.

    Args:
      path_segments (list[str]): path segments inside the test data directory.
      parser (BaseParser): parser.
      knowledge_base_object (KnowledgeBase): knowledge base.

    Returns:
      FakeStorageWriter: storage writer.
    """
    session = sessions.Session()
    storage_writer = fake_writer.FakeStorageWriter(session)
    storage_writer.Open()

    mediator = parsers_mediator.ParserMediator(
        storage_writer, knowledge_base_object)

    file_entry = self._GetTestFileEntry(path_segments)
    mediator.SetFileEntry(file_entry)

    if isinstance(parser, parsers_interface.FileEntryParser):
      parser.Parse(mediator)

    elif isinstance(parser, parsers_interface.FileObjectParser):
      file_object = file_entry.GetFileObject()
      try:
        parser.Parse(mediator, file_object)
      finally:
        file_object.close()

    else:
      self.fail('Got unexpected parser type: {0:s}'.format(type(parser)))

    return storage_writer

  def _SetUpKnowledgeBase(self, knowledge_base_values=None):
    """Sets up a knowledge base.

    Args:
      knowledge_base_values (Optional[dict[str, str]]): knowledge base values.

    Returns:
      KnowledgeBase: knowledge base.
    """
    knowledge_base_object = knowledge_base.KnowledgeBase()
    if knowledge_base_values:
      for identifier, value in iter(knowledge_base_values.items()):
        if identifier == 'users':
          self._SetUserAccounts(knowledge_base_object, value)
        else:
          knowledge_base_object.SetValue(identifier, value)

    return knowledge_base_object

  def _SetUserAccounts(self, knowledge_base_object, users):
    """Sets the user accounts in the knowledge base.

    Args:
      knowledge_base_object (KnowledgeBase): used to store information about
          users.
      users (list[dict[str, str])): users, for example [{'name': 'me',
        'sid': 'S-1', 'uid': '1'}]
    """
    for user in users:
      identifier = user.get('sid', user.get('uid', None))
      if not identifier:
        continue

      user_account_artifact = artifacts.UserAccountArtifact(
          identifier=identifier, user_directory=user.get('path', None),
          username=user.get('name', None))

      knowledge_base_object.AddUserAccount(user_account_artifact)
