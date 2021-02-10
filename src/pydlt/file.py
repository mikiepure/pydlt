""" Provide class to handle DLT file. """
import struct
from io import SEEK_CUR
from pathlib import Path
from typing import Iterator, List, Optional, Union

from pydlt.header import StandardHeader, StorageHeader
from pydlt.message import DltMessage


class DltFileReader:
    """A class to read DLT message from DLT file.

    Examples::
        # create reader as context manager
        with DltFileReader("filepath") as reader:
            # read 1 message from file
            message = reader.read_message()

            # read all messages from file
            messages = reader.read_messages()

        # create reader as iterator
        for message in DltFileReader("filepath"):  # read all messages
            # handle each message
    """

    def __init__(self, path: Union[str, Path]) -> None:
        """Create DltFileReader object.

        Open a file of the path in the constructor.
        The file should be closed by calling close() method
        when the file is no longer used by the class.

        The class supports context manager and with block.
        close() method does not have to be called if using it.

        Args:
            path (Union[str, Path]): A path to file.
        """
        self._file = open(str(path), "rb")

    def __enter__(self) -> "DltFileReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        self.close()

    def close(self) -> None:
        """Close a file opened by the class."""
        self._file.close()

    @property
    def closed(self) -> bool:
        """Check a file opened by the class is closed.

        Returns:
            bool: A file is closed if True.
        """
        return self._file.closed

    def __iter__(self) -> Iterator[DltMessage]:
        return self

    def __next__(self) -> DltMessage:
        message = self.read_message()
        if message is None:
            raise StopIteration()
        return message

    def read_message(self) -> Optional[DltMessage]:
        """Read 1 DLT message from file.

        Returns:
            Optional[DltMessage]: DLT message or None if not enough data to read
        """
        min_length = StorageHeader.DATA_LENGTH + StandardHeader.DATA_MIN_LENGTH
        min_data = self._file.peek(min_length)
        if len(min_data) < min_length:
            return None
        length = struct.unpack_from(
            StandardHeader.STRUCT_MIN_FORMAT, min_data, StorageHeader.DATA_LENGTH
        )[2]
        msg_length = StorageHeader.DATA_LENGTH + length
        msg_data = self._file.peek(msg_length)
        if len(msg_data) < msg_length:
            return None
        self._file.seek(msg_length, SEEK_CUR)
        return DltMessage.create_from_bytes(msg_data, True)

    def read_messages(self) -> List[DltMessage]:
        """Read all DLT messages from file.

        Returns:
            List[DltMessage]: All DLT messages in the file
        """
        return [message for message in self.__iter__()]


class DltFileWriter:
    """A class to write DLT message to DLT file.

    Examples::
        # create writer as context manager
        with DltFileWriter("filepath") as writer:
            # write 1 message to file
            writer.write_message(message)

            # write messages to file
            writer.write_messages(messages)
    """

    def __init__(self, path: Union[str, Path], append: bool = False) -> None:
        """Create DltFileWriter object.

        Open a file of the path in the constructor.
        The file should be closed by calling close() method
        when the file is no longer used by the class.

        The class supports context manager and with block.
        close() method does not have to be called if using it.

        Args:
            path (Union[str, Path]): A path to file.
            append (bool, optional): Set True if append mode. Defaults to False.
        """
        mode = "ab" if append else "wb"
        self._file = open(path, mode)

    def __enter__(self) -> "DltFileWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        self.close()

    def close(self) -> None:
        """Close a file opened by the class."""
        self._file.close()

    @property
    def closed(self) -> bool:
        """Check a file opened by the class is closed.

        Returns:
            bool: A file is closed if True.
        """
        return self._file.closed

    def write_message(self, message: DltMessage) -> None:
        """Write 1 DLT message to file.

        Args:
            message (DltMessage): DLT message
        """
        self._file.write(message.to_bytes())

    def write_messages(self, messages: List[DltMessage]) -> None:
        """Write DLT messages to file.

        Args:
            messages (List[DltMessage]): DLT messages
        """
        [self.write_message(message) for message in messages]
