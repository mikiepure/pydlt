from typing import cast

import pydlt.payload as payload
import pytest
from pydlt import Argument, ArgumentBool


def test_bool_payload_without_type_length():
    b1 = ArgumentBool(True)
    dlt_bytes = bytearray(b1.to_bytes(False))
    # clear the TypeInfo.TYPE_LENGTH_8BIT flag
    dlt_bytes[0] = 0x10
    assert (
        cast(ArgumentBool, Argument.create_from_bytes(bytes(dlt_bytes), False)).data
        is True
    )


def test_bool_endian():
    # Endian is not defined
    b1 = ArgumentBool(True)

    # - msb_first_default is False (default)
    assert b1.to_bytes() == b1.to_bytes(False)

    # - msb_first_default is True
    payload.msb_first_default = True
    assert b1.to_bytes() == b1.to_bytes(True)

    # - msb_first_default is None
    payload.msb_first_default = None
    with pytest.raises(ValueError):
        assert b1.to_bytes()

    # Endian is defined (LSB First)
    b2 = ArgumentBool(True, msb_first=False)
    assert b2.to_bytes() == b2.to_bytes(False)

    # Endian is defined (MSB First)
    b3 = ArgumentBool(True, msb_first=True)
    assert b3.to_bytes() == b3.to_bytes(True)
