"""Provide definition of Service ID of DLT control message.

It can be checked at the section "5.3 Services / Commands"
in AUTOSAR Log and Trace Protocol Specification R22-11.

For others, including deprecated, are listed at the section "7.7.7.1 Control messages"
in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3.
"""

from enum import IntEnum


class ServiceId(IntEnum):
    """A definition of Service ID of DLT control messages."""

    SET_LOG_LEVEL = 0x01
    SET_TRACE_STATUS = 0x02
    GET_LOG_INFO = 0x03
    GET_DEFAULT_LOG_LEVEL = 0x04
    STORE_CONFIG = 0x05
    RESET_TO_FACTORY_DEFAULT = 0x06
    SET_COM_INTERFACE_STATUS = 0x07
    SET_COM_INTERFACE_MAX_BANDWIDTH = 0x08
    SET_VERBOSE_MODE = 0x09
    SET_MESSAGE_FILTERING = 0x0A
    SET_TIMING_PACKETS = 0x0B
    GET_LOCAL_TIME = 0x0C
    SET_USE_ECU_ID = 0x0D
    SET_USE_SESSION_ID = 0x0E
    SET_USE_TIMESTAMP = 0x0F  # original service name: UseTimestamp
    SET_USE_EXTENDED_HEADER = 0x10  # original service name: UseExtendedHeader
    SET_DEFAULT_LOG_LEVEL = 0x11
    SET_DEFAULT_TRACE_STATUS = 0x12
    GET_SOFTWARE_VERSION = 0x13
    MESSAGE_BUFFER_OVERFLOW = 0x14
    GET_DEFAULT_TRACE_STATUS = 0x15
    GET_COM_INTERFACE_STATUS = 0x16
    GET_COM_INTERFACE_NAMES = 0x17
    GET_COM_INTERFACE_MAX_BANDWIDTH = 0x18
    GET_VERBOSE_MODE_STATUS = 0x19
    GET_MESSAGE_FILTERING_STATUS = 0x1A
    GET_USE_ECU_ID = 0x1B
    GET_USE_SESSION_ID = 0x0C
    GET_USE_TIMESTAMP = 0x1D
    GET_USE_EXTENDED_HEADER = 0x1E  # original service name: UseExtendedHeader
    GET_TRACE_STATUS = 0x1F
    SET_LOG_CHANNEL_ASSIGNMENT = 0x20
    SET_LOG_CHANNEL_THRESHOLD = 0x21
    GET_LOG_CHANNEL_THRESHOLD = 0x22
    GET_BUFFER_OVERFLOW_NOTIFICATION = 0x23  # original name: BufferOverflowNotification
    SET_LOG_LEVEL_LONG = 0x25
    SET_TRACE_STATUS_LONG = 0x26
    GET_LOG_INFO_LONG = 0x27
    GET_TRACE_STATUS_LONG = 0x28
    SET_LOG_CHANNEL_ASSIGNMENT_LONG = 0x29
    CALL_SW_C_INJECTION_BEGIN = 0xFFF
    # service name: CallSW-CInjection has a range: 0xFFF ... 0xFFFFFFFF
    CALL_SW_C_INJECTION_END = 0xFFFFFFFF
