import sys
from pathlib import Path

import pytest

from pydlt import (
    ArgumentString,
    DltFileReader,
    DltFileWriter,
    DltMessage,
    MessageLogInfo,
    MessageType,
    StorageHeader,
)

CURRENT_DIR_PATH = Path(__file__).parent.absolute()
TEST_RESULTS_DIR_PATH = CURRENT_DIR_PATH / "results"
TEST_RESULTS_DIR_PATH.mkdir(exist_ok=True)


def test_file():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    writer = DltFileWriter(path)
    assert writer.closed is False
    writer.write_message(_make_dlt_message())
    writer.write_message(_make_dlt_message())
    writer.close()
    assert writer.closed is True

    reader = DltFileReader(path)
    assert reader.closed is False
    assert reader.read_message() is not None
    assert reader.read_message() is not None
    assert reader.read_message() is None
    reader.close()
    assert reader.closed is True


def test_file_context_manager():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    with DltFileWriter(path) as writer:
        assert writer.closed is False
        writer.write_message(_make_dlt_message())
        writer.write_message(_make_dlt_message())
    assert writer.closed is True

    with DltFileReader(path) as reader:
        assert reader.closed is False
        assert reader.read_message() is not None
        assert reader.read_message() is not None
        assert reader.read_message() is None
    assert reader.closed is True


def test_file_read_large_message():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    msg1 = DltMessage.create_verbose_message(
        [ArgumentString("0123456789" * 6000)],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "App",
        "Ctx",
        message_counter=0,
        str_header=StorageHeader(0, 0, "Ecu"),
    )

    with DltFileWriter(path) as writer:
        writer.write_messages([msg1])

    with DltFileReader(path) as reader:
        msg = reader.read_message()
        assert msg is not None
        assert msg1 == msg


def test_file_list_iterator():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    with DltFileWriter(path) as writer:
        assert writer.closed is False
        messages = [_make_dlt_message(), _make_dlt_message()]
        writer.write_messages(messages)
    assert writer.closed is True

    with DltFileReader(path) as reader:
        assert reader.closed is False
        messages = reader.read_messages()
        assert len(messages) == 2
    assert reader.closed is True

    message_len = 0
    for _ in DltFileReader(path):
        message_len += 1
    assert message_len == 2


def test_quick_start():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    # Create DLT message
    msg1 = DltMessage.create_verbose_message(
        [ArgumentString("hello, pydlt!")],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "App",
        "Ctx",
        message_counter=0,
        str_header=StorageHeader(0, 0, "Ecu"),
    )
    msg2 = DltMessage.create_non_verbose_message(
        0,
        b"\x01\x02\x03",
        message_counter=1,
        str_header=StorageHeader(0, 0, "Ecu"),
    )
    # Write DLT messages to file
    with DltFileWriter(path) as writer:
        writer.write_messages([msg1, msg2])

    print()

    # Read each DLT message from file
    for msg in DltFileReader(path):
        # Print overview of each DLT message
        print(msg)


def test_file_encoding():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")
    msg1 = DltMessage.create_verbose_message(
        [ArgumentString("100°C äöü", encoding="latin-1")],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "App",
        "Ctx",
        str_header=StorageHeader(0, 0, "Ecu"),
    )
    with DltFileWriter(path) as writer:
        writer.write_messages([msg1])

    with DltFileReader(path, encoding="latin-1") as reader:
        msg = reader.read_message()
        assert msg is not None
        assert str(msg.payload) == "100°C äöü"


def _make_dlt_message():
    std_header = DltMessage._create_standard_header(
        0, None, None, None, None, 0, 1, False
    )
    return DltMessage(StorageHeader(0, 0, "ECU"), std_header, None, None)


if __name__ == "__main__":
    pytest.main(sys.argv.extend(["--capture", "no"]))
