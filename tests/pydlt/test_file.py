import sys
from pathlib import Path

import pytest

from pydlt.file import DltFileReader, DltFileWriter
from pydlt.header import StorageHeader
from pydlt.message import DltMessage

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


# the test can be executed after running all unit tests
@pytest.mark.skip(reason="file not stored")
def test_quick_start():
    path = TEST_RESULTS_DIR_PATH / Path("test_message_std_header_msbf_verbose_true.dlt")
    print()
    for msg in DltFileReader(path):
        print(msg)


def _make_dlt_message():
    std_header = DltMessage._create_standard_header(
        0, None, None, None, None, 0, 1, False
    )
    return DltMessage(StorageHeader(0, 0, "ECU"), std_header, None, None)


if __name__ == "__main__":
    pytest.main(["--capture", "no"])
