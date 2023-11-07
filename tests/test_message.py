import struct
import sys
from pathlib import Path
from typing import List, cast

import pytest
from pydlt import (
    Argument,
    ArgumentBool,
    ArgumentFloat32,
    ArgumentFloat64,
    ArgumentRaw,
    ArgumentSInt8,
    ArgumentSInt16,
    ArgumentSInt32,
    ArgumentSInt64,
    ArgumentString,
    ArgumentUInt8,
    ArgumentUInt16,
    ArgumentUInt32,
    ArgumentUInt64,
    DltMessage,
    MessageBusInfo,
    MessageLogInfo,
    MessageType,
    StorageHeader,
)

CURRENT_DIR_PATH = Path(__file__).parent.absolute()
TEST_RESULTS_DIR_PATH = CURRENT_DIR_PATH / "results"
TEST_RESULTS_DIR_PATH.mkdir(exist_ok=True)


def test_string_representation():
    msg = DltMessage.create_verbose_message(
        [ArgumentString("ABCabc129!")],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "Apid",
        "Ctid",
        timestamp=93678,  # 9.3678 sec
        session_id=12345,
        ecu_id="Ecu",
        message_counter=119,
        str_header=StorageHeader(3600, 899, "ECU"),  # 3600 sec = 1 h
    )
    assert (
        str(msg) == "1970/01/01 01:00:00.000899 "
        "9.3678 119 Ecu Apid Ctid 12345 log info verbose 1 ABCabc129!"
    )


def test_latin1_encoding():
    msg = DltMessage.create_verbose_message(
        [ArgumentString("120°C äöü", is_utf8=False, encoding="latin-1")],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "Apid",
        "Ctid",
        timestamp=93678,  # 9.3678 sec
        session_id=12345,
        ecu_id="Ecu",
        message_counter=119,
    )
    copy = msg.create_from_bytes(msg.to_bytes(), False, "latin-1")
    assert str(copy) == "9.3678 119 Ecu Apid Ctid 12345 log info verbose 1 120°C äöü"


def test_message_std_header():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        timestamp=11111,  # 1.1111 sec
        session_id=12345,
        ecu_id="Ecu",
        message_counter=111,
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp == 11111
    assert dlt_message2.std_header.session_id == 12345
    assert dlt_message2.std_header.ecu_id == "Ecu"
    assert dlt_message2.std_header.message_counter == 111


def test_message_std_header_no_option():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp is None
    assert dlt_message2.std_header.session_id is None
    assert dlt_message2.std_header.ecu_id is None
    assert dlt_message2.std_header.message_counter == 0


def test_message_std_header_timestamp():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        timestamp=11111,  # 1.1111 sec
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp == 11111
    assert dlt_message2.std_header.session_id is None
    assert dlt_message2.std_header.ecu_id is None
    assert dlt_message2.std_header.message_counter == 0


def test_message_std_header_session_id():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        session_id=12345,
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp is None
    assert dlt_message2.std_header.session_id == 12345
    assert dlt_message2.std_header.ecu_id is None
    assert dlt_message2.std_header.message_counter == 0


def test_message_std_header_ecu_id():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        ecu_id="Ecu",
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp is None
    assert dlt_message2.std_header.session_id is None
    assert dlt_message2.std_header.ecu_id == "Ecu"
    assert dlt_message2.std_header.message_counter == 0


def test_message_std_header_min():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        timestamp=0,
        session_id=0,
        ecu_id="",
        message_counter=0,
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp == 0
    assert dlt_message2.std_header.session_id == 0
    assert dlt_message2.std_header.ecu_id == ""
    assert dlt_message2.std_header.message_counter == 0


def test_message_std_header_max():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_non_verbose_message(
        0,
        b"\x00",
        timestamp=0xFFFFFFFF,
        session_id=0xFFFFFFFF,
        ecu_id="EcuX",
        message_counter=0xFF,
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.std_header.timestamp == 0xFFFFFFFF
    assert dlt_message2.std_header.session_id == 0xFFFFFFFF
    assert dlt_message2.std_header.ecu_id == "EcuX"
    assert dlt_message2.std_header.message_counter == 0xFF


def test_message_std_header_msbf_non_verbose_false():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _dlt_std_header_msbf_non_verbose_make_messsage(False)
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    _dlt_std_header_msbf_non_verbose_validation(dlt_message2)


def test_message_std_header_msbf_non_verbose_true():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _dlt_std_header_msbf_non_verbose_make_messsage(True)
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    _dlt_std_header_msbf_non_verbose_validation(dlt_message2)


def _dlt_std_header_msbf_non_verbose_make_messsage(msbf: bool) -> DltMessage:
    return DltMessage.create_non_verbose_message(
        0xDEADBEAF,  # 3735928495
        b"\x01\x02\x03",
        msb_first=msbf,
        str_header=StorageHeader(0, 0, "ECU"),
    )


def _dlt_std_header_msbf_non_verbose_validation(msg: DltMessage):
    assert msg.non_verbose_payload.message_id == 0xDEADBEAF
    assert msg.non_verbose_payload.non_static_data == b"\x01\x02\x03"


def test_message_std_header_msbf_verbose_false():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _dlt_std_header_msbf_verbose_make_messsage(False)
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    _dlt_std_header_msbf_verbose_validation(dlt_message2)


def test_message_std_header_msbf_verbose_true():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _dlt_std_header_msbf_verbose_make_messsage(True)
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    _dlt_std_header_msbf_verbose_validation(dlt_message2)


def _dlt_std_header_msbf_verbose_make_messsage(msbf: bool) -> DltMessage:
    return _make_verbose_payload_message(
        [
            ArgumentBool(False),
            ArgumentBool(True),
            ArgumentUInt8(111),
            ArgumentUInt16(11111),
            ArgumentUInt32(1111111111),
            ArgumentUInt64(1111111111111111111),
            ArgumentSInt8(-111),
            ArgumentSInt16(-11111),
            ArgumentSInt32(-1111111111),
            ArgumentSInt64(-1111111111111111111),
            ArgumentFloat32(1.11),
            ArgumentFloat64(1.11),
            ArgumentString("abc123XYZ!", False),
            ArgumentString("あいうえお", True),
            ArgumentRaw(b"\x01\x02\x03"),
        ],
        msbf,
    )


def _dlt_std_header_msbf_verbose_validation(msg: DltMessage):
    assert cast(ArgumentBool, msg.verbose_payload.arguments[0]).data is False
    assert cast(ArgumentBool, msg.verbose_payload.arguments[1]).data is True
    assert cast(ArgumentUInt8, msg.verbose_payload.arguments[2]).data == 111
    assert cast(ArgumentUInt16, msg.verbose_payload.arguments[3]).data == 11111
    assert cast(ArgumentUInt32, msg.verbose_payload.arguments[4]).data == 1111111111
    assert (
        cast(ArgumentUInt64, msg.verbose_payload.arguments[5]).data
        == 1111111111111111111
    )
    assert cast(ArgumentSInt8, msg.verbose_payload.arguments[6]).data == -111
    assert cast(ArgumentSInt16, msg.verbose_payload.arguments[7]).data == -11111
    assert cast(ArgumentSInt32, msg.verbose_payload.arguments[8]).data == -1111111111
    assert (
        cast(ArgumentSInt64, msg.verbose_payload.arguments[9]).data
        == -1111111111111111111
    )
    assert (
        cast(ArgumentFloat32, msg.verbose_payload.arguments[10]).data
        == struct.unpack(">f", struct.pack(">f", 1.11))[0]
    )
    assert (
        cast(ArgumentFloat64, msg.verbose_payload.arguments[11]).data
        == struct.unpack(">d", struct.pack(">d", 1.11))[0]
    )
    assert cast(ArgumentString, msg.verbose_payload.arguments[12]).data == "abc123XYZ!"
    assert cast(ArgumentString, msg.verbose_payload.arguments[13]).data == "あいうえお"
    assert cast(ArgumentRaw, msg.verbose_payload.arguments[14]).data == b"\x01\x02\x03"


def test_message_ext_header():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_verbose_message(
        [],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "App",
        "Ctx",
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.ext_header.message_type == MessageType.DLT_TYPE_LOG
    assert dlt_message2.ext_header.message_log_info == MessageLogInfo.DLT_LOG_INFO
    assert dlt_message2.ext_header.application_id == "App"
    assert dlt_message2.ext_header.context_id == "Ctx"


def test_message_ext_header_min():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_verbose_message(
        [],
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_FATAL,
        "",
        "",
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.ext_header.message_type == MessageType.DLT_TYPE_LOG
    assert dlt_message2.ext_header.message_log_info == MessageLogInfo.DLT_LOG_FATAL
    assert dlt_message2.ext_header.application_id == ""
    assert dlt_message2.ext_header.context_id == ""


def test_message_ext_header_max():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = DltMessage.create_verbose_message(
        [],
        MessageType.DLT_TYPE_NW_TRACE,
        MessageBusInfo.DLT_NW_TRACE_MOST,
        "AppX",
        "CtxX",
        str_header=StorageHeader(0, 0, "ECU"),
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert dlt_message2.ext_header.message_type == MessageType.DLT_TYPE_NW_TRACE
    assert dlt_message2.ext_header.message_log_info == MessageBusInfo.DLT_NW_TRACE_MOST
    assert dlt_message2.ext_header.application_id == "AppX"
    assert dlt_message2.ext_header.context_id == "CtxX"


def test_message_verbose_payload_bool():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _make_verbose_payload_message(
        [ArgumentBool(False), ArgumentBool(True)]
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert cast(ArgumentBool, dlt_message2.verbose_payload.arguments[0]).data is False
    assert cast(ArgumentBool, dlt_message2.verbose_payload.arguments[1]).data is True


def test_message_verbose_payload_uint():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _make_verbose_payload_message(
        [
            ArgumentUInt8(111),
            ArgumentUInt16(11111),
            ArgumentUInt32(1111111111),
            ArgumentUInt64(1111111111111111111),
        ]
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert cast(ArgumentUInt8, dlt_message2.verbose_payload.arguments[0]).data == 111
    assert cast(ArgumentUInt16, dlt_message2.verbose_payload.arguments[1]).data == 11111
    assert (
        cast(ArgumentUInt32, dlt_message2.verbose_payload.arguments[2]).data
        == 1111111111
    )
    assert (
        cast(ArgumentUInt64, dlt_message2.verbose_payload.arguments[3]).data
        == 1111111111111111111
    )


def test_message_verbose_payload_sint():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _make_verbose_payload_message(
        [
            ArgumentSInt8(-111),
            ArgumentSInt16(-11111),
            ArgumentSInt32(-1111111111),
            ArgumentSInt64(-1111111111111111111),
        ]
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert cast(ArgumentSInt8, dlt_message2.verbose_payload.arguments[0]).data == -111
    assert (
        cast(ArgumentSInt16, dlt_message2.verbose_payload.arguments[1]).data == -11111
    )
    assert (
        cast(ArgumentSInt32, dlt_message2.verbose_payload.arguments[2]).data
        == -1111111111
    )
    assert (
        cast(ArgumentSInt64, dlt_message2.verbose_payload.arguments[3]).data
        == -1111111111111111111
    )


def test_message_verbose_payload_float():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _make_verbose_payload_message(
        [ArgumentFloat32(1.11), ArgumentFloat64(1.11)]
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert (
        cast(ArgumentFloat32, dlt_message2.verbose_payload.arguments[0]).data
        == struct.unpack(">f", struct.pack(">f", 1.11))[0]
    )
    assert (
        cast(ArgumentFloat64, dlt_message2.verbose_payload.arguments[1]).data
        == struct.unpack(">d", struct.pack(">d", 1.11))[0]
    )


def test_message_verbose_payload_string():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _make_verbose_payload_message(
        [ArgumentString("abc123XYZ!", False), ArgumentString("あいうえお", True)]
    )
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert (
        cast(ArgumentString, dlt_message2.verbose_payload.arguments[0]).data
        == "abc123XYZ!"
    )
    assert (
        cast(ArgumentString, dlt_message2.verbose_payload.arguments[1]).data
        == "あいうえお"
    )


def test_message_verbose_payload_raw():
    path = TEST_RESULTS_DIR_PATH / Path(f"{sys._getframe().f_code.co_name}.dlt")

    dlt_message1 = _make_verbose_payload_message([ArgumentRaw(b"\x01\x02\x03")])
    dlt_bytes = dlt_message1.to_bytes()
    path.write_bytes(dlt_bytes)

    dlt_message2 = DltMessage.create_from_bytes(dlt_bytes, True)
    assert (
        cast(ArgumentRaw, dlt_message2.verbose_payload.arguments[0]).data
        == b"\x01\x02\x03"
    )


def _make_verbose_payload_message(
    args: List[Argument], msbf: bool = False
) -> DltMessage:
    return DltMessage.create_verbose_message(
        args,
        MessageType.DLT_TYPE_LOG,
        MessageLogInfo.DLT_LOG_INFO,
        "App",
        "Ctx",
        msb_first=msbf,
        str_header=StorageHeader(0, 0, "ECU"),
    )


if __name__ == "__main__":
    pytest.main(sys.argv)
