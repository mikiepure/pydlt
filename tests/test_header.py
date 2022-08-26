import sys
import pytest

from pydlt import (
    StorageHeader,
    StandardHeader,
    ExtendedHeader,
    MessageType,
    MessageLogInfo,
)


def test_storage_header():
    header = StorageHeader(3600, 899, "ECU")
    assert header == StorageHeader(3600, 899, "ECU")
    assert header != StorageHeader(0, 899, "ECU")
    assert header != StorageHeader(3600, 0, "ECU")
    assert header != StorageHeader(3600, 899, "EC")
    assert header == eval(repr(header))
    assert header == StorageHeader.create_from_bytes(header.to_bytes())
    assert 16 == len(header.to_bytes())


def test_storage_header_min():
    header = StorageHeader(0, 0, '')
    assert header == StorageHeader.create_from_bytes(header.to_bytes())
    assert 16 == len(header.to_bytes())


def test_std_header():
    header = StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header == StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=True,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=True,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=2,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=88,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=200,
        ecu_id="ECU",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECUI",
        session_id=42,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=43,
        timestamp=1200,
    )
    assert header != StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
        timestamp=12010,
    )
    assert header == eval(repr(header))
    assert header == StandardHeader.create_from_bytes(header.to_bytes())
    assert 16 == len(header.to_bytes())


def test_standard_header_no_timestamp():
    header = StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        session_id=42,
    )
    assert header == eval(repr(header))
    assert header == StandardHeader.create_from_bytes(header.to_bytes())
    assert 12 == len(header.to_bytes())


def test_standard_header_no_session():
    header = StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
        timestamp=1142,
    )
    assert header == eval(repr(header))
    assert header == StandardHeader.create_from_bytes(header.to_bytes())
    assert 12 == len(header.to_bytes())


def test_standard_header_no_session_no_timestamp():
    header = StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
        ecu_id="ECU",
    )
    assert header == eval(repr(header))
    assert header == StandardHeader.create_from_bytes(header.to_bytes())
    assert 8 == len(header.to_bytes())


def test_standard_header_minimal():
    header = StandardHeader(
        use_extended_header=False,
        msb_first=False,
        version_number=1,
        message_counter=87,
        length=199,
    )
    assert header == eval(repr(header))
    assert header == StandardHeader.create_from_bytes(header.to_bytes())
    assert 4 == len(header.to_bytes())


def test_extended_header():
    header = ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=1,
        application_id="APID",
        context_id="CTX",
    )
    assert header == ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=1,
        application_id="APID",
        context_id="CTX",
    )
    assert header != ExtendedHeader(
        verbose=False,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=1,
        application_id="APID",
        context_id="CTX",
    )
    assert header != ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_CONTROL,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=1,
        application_id="APID",
        context_id="CTX",
    )
    assert header != ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_WARN,
        number_of_arguments=1,
        application_id="APID",
        context_id="CTX",
    )
    assert header != ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=2,
        application_id="APID",
        context_id="CTX",
    )
    assert header != ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=1,
        application_id="API",
        context_id="CTX",
    )
    assert header != ExtendedHeader(
        verbose=True,
        message_type=MessageType.DLT_TYPE_LOG,
        message_type_info=MessageLogInfo.DLT_LOG_INFO,
        number_of_arguments=1,
        application_id="APID",
        context_id="CTIX",
    )
    assert header == eval(repr(header))
    assert header == ExtendedHeader.create_from_bytes(header.to_bytes())
    assert 10 == len(header.to_bytes())


if __name__ == "__main__":
    pytest.main(sys.argv)
