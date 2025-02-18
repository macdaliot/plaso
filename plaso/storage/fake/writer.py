# -*- coding: utf-8 -*-
"""Fake (in-memory only) storage writer for testing."""

from plaso.lib import definitions
from plaso.storage import writer
from plaso.storage.fake import fake_store


class FakeStorageWriter(writer.StorageWriter):
  """Fake (in-memory only) storage writer object.

  Attributes:
    session_completion (SessionCompletion): session completion attribute
        container.
    session_configuration (SessionConfiguration): session configuration
        attribute container.
    session_start (SessionStart): session start attribute container.
    task_completion (TaskCompletion): task completion attribute container.
    task_start (TaskStart): task start attribute container.
  """

  def __init__(self, storage_type=definitions.STORAGE_TYPE_SESSION):
    """Initializes a storage writer object.

    Args:
      storage_type (Optional[str]): storage type.
    """
    super(FakeStorageWriter, self).__init__(storage_type=storage_type)
    self.session_completion = None
    self.session_configuration = None
    self.session_start = None
    self.task_completion = None
    self.task_start = None

  def GetFirstWrittenEventSource(self):
    """Retrieves the first event source that was written after open.

    Using GetFirstWrittenEventSource and GetNextWrittenEventSource newly
    added event sources can be retrieved in order of addition.

    Returns:
      EventSource: event source or None if there are no newly written ones.

    Raises:
      IOError: when the storage writer is closed.
      OSError: when the storage writer is closed.
    """
    if not self._store:
      raise IOError('Unable to read from closed storage writer.')

    event_source = self._store.GetAttributeContainerByIndex(
        self._CONTAINER_TYPE_EVENT_SOURCE,
        self._first_written_event_source_index)
    self._written_event_source_index = (
        self._first_written_event_source_index + 1)
    return event_source

  def GetNextWrittenEventSource(self):
    """Retrieves the next event source that was written after open.

    Returns:
      EventSource: event source or None if there are no newly written ones.

    Raises:
      IOError: when the storage writer is closed.
      OSError: when the storage writer is closed.
    """
    if not self._store:
      raise IOError('Unable to read from closed storage writer.')

    event_source = self._store.GetAttributeContainerByIndex(
        self._CONTAINER_TYPE_EVENT_SOURCE, self._written_event_source_index)
    self._written_event_source_index += 1
    return event_source

  def Open(self, **unused_kwargs):
    """Opens the storage writer.

    Raises:
      IOError: if the storage writer is already opened.
      OSError: if the storage writer is already opened.
    """
    if self._store:
      raise IOError('Storage writer already opened.')

    self._store = fake_store.FakeStore()
    self._store.Open()

    self._first_written_event_source_index = 0
    self._written_event_source_index = 0

  def WriteSessionCompletion(self, session):
    """Writes session completion information.


    Args:
      session (Session): session the storage changes are part of.

    Raises:
      IOError: if the storage type does not support writing a session
          completion or when the storage writer is closed.
      OSError: if the storage type does not support writing a session
          completion or when the storage writer is closed.
    """
    self._RaiseIfNotWritable()

    if self._storage_type != definitions.STORAGE_TYPE_SESSION:
      raise IOError('Session start not supported by storage type.')

    self.session_completion = session.CreateSessionCompletion()

  def WriteSessionConfiguration(self, session):
    """Writes session configuration information.

    Args:
      session (Session): session the storage changes are part of.

    Raises:
      IOError: if the storage type does not support writing session
          configuration information or when the storage writer is closed.
      OSError: if the storage type does not support writing session
          configuration information or when the storage writer is closed.
    """
    self._RaiseIfNotWritable()

    if self._storage_type != definitions.STORAGE_TYPE_SESSION:
      raise IOError('Session configuration not supported by storage type.')

    self.session_configuration = session.CreateSessionConfiguration()

  def WriteSessionStart(self, session):
    """Writes session start information.

    Args:
      session (Session): session the storage changes are part of.

    Raises:
      IOError: if the storage type does not support writing a session
          start or when the storage writer is closed.
      OSError: if the storage type does not support writing a session
          start or when the storage writer is closed.
    """
    self._RaiseIfNotWritable()

    if self._storage_type != definitions.STORAGE_TYPE_SESSION:
      raise IOError('Session start not supported by storage type.')

    self.session_start = session.CreateSessionStart()

  # TODO: refactor into base writer.
  def WriteTaskCompletion(self, task):
    """Writes task completion information.

    Args:
      task (Task): task.

    Raises:
      IOError: if the storage type does not support writing a task
          completion or when the storage writer is closed.
      OSError: if the storage type does not support writing a task
          completion or when the storage writer is closed.
    """
    self._RaiseIfNotWritable()

    if self._storage_type != definitions.STORAGE_TYPE_TASK:
      raise IOError('Task completion not supported by storage type.')

    self.task_completion = task.CreateTaskCompletion()

  # TODO: refactor into base writer.
  def WriteTaskStart(self, task):
    """Writes task start information.

    Args:
      task (Task): task.

    Raises:
      IOError: if the storage type does not support writing a task
          start or when the storage writer is closed.
      OSError: if the storage type does not support writing a task
          start or when the storage writer is closed.
    """
    self._RaiseIfNotWritable()

    if self._storage_type != definitions.STORAGE_TYPE_TASK:
      raise IOError('Task start not supported by storage type.')

    self.task_start = task.CreateTaskStart()
