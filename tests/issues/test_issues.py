from pathlib import Path
from typing import cast

import pytest
from pydlt.file import DltFileReader
from pydlt.payload import ArgumentString, ArgumentUInt32

CURRENT_DIR_PATH = Path(__file__).parent.absolute()


def test_issue24():
    """Ignore missing bytes and reduce numeric type if there are not enough bytes of
    numeric type at the end of the payload like as DLTViewer (qdlt/qdltargument.cpp).
    """
    path = CURRENT_DIR_PATH / "issue24.dlt"
    with DltFileReader(path) as reader:
        with pytest.warns():
            # show warnings: the data of 64 bit unsigned integer is not enough,
            # handle it as 32 bit unsigned integer.
            msg = reader.read_message()
        assert msg is not None
        assert msg.verbose is True
        args = msg.verbose_payload.arguments
        assert len(args) == 2
        assert cast(ArgumentString, args[0]).data == "HIST: SCU_RSTSTAT:"
        assert cast(ArgumentUInt32, args[1]).data == 65536
