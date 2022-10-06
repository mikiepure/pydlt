""" Provide message class of the DLT protocol. """
from datetime import datetime, timezone
from typing import List, Optional, cast

from pydlt.header import (
    ExtendedHeader,
    MessageBusInfo,
    MessageControlInfo,
    MessageLogInfo,
    MessageTraceInfo,
    MessageType,
    MessageTypeInfo,
    StandardHeader,
    StorageHeader,
)
from pydlt.payload import Argument, NonVerbosePayload, Payload, VerbosePayload

###############################################################################
# DLT Message of the DLT protocol
# It can be checked at following sections:
# - 7.7.1 Dlt Message Format in General
# - 7.7.6 Additional Message Parts
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


_MESSAGE_TYPE_STR = {
    MessageType.DLT_TYPE_LOG: "log",
    MessageType.DLT_TYPE_APP_TRACE: "app_trace",
    MessageType.DLT_TYPE_NW_TRACE: "nw_trace",
    MessageType.DLT_TYPE_CONTROL: "control",
}

_MESSAGE_LOG_INFO_STR = {
    MessageLogInfo.DLT_LOG_FATAL: "fatal",
    MessageLogInfo.DLT_LOG_ERROR: "error",
    MessageLogInfo.DLT_LOG_WARN: "warn",
    MessageLogInfo.DLT_LOG_INFO: "info",
    MessageLogInfo.DLT_LOG_DEBUG: "debug",
    MessageLogInfo.DLT_LOG_VERBOSE: "verbose",
}

_MESSAGE_TRACE_INFO_STR = {
    MessageTraceInfo.DLT_TRACE_VARIABLE: "variable",
    MessageTraceInfo.DLT_TRACE_FUNCTON_IN: "func_in",
    MessageTraceInfo.DLT_TRACE_FUNCTON_OUT: "func_out",
    MessageTraceInfo.DLT_TRACE_STATE: "state",
    MessageTraceInfo.DLT_TRACE_VFB: "vfb",
}

_MESSAGE_BUS_INFO_STR = {
    MessageBusInfo.DLT_NW_TRACE_IPC: "ipc",
    MessageBusInfo.DLT_NW_TRACE_CAN: "can",
    MessageBusInfo.DLT_NW_TRACE_FLEXRAY: "flexray",
    MessageBusInfo.DLT_NW_TRACE_MOST: "most",
}

_MESSAGE_CONTROL_INFO_STR = {
    MessageControlInfo.DLT_CONTROL_REQUEST: "request",
    MessageControlInfo.DLT_CONTROL_RESPONSE: "response",
    MessageControlInfo.DLT_CONTROL_TIME: "time",
}


class DltMessage:
    """A class to handle DLT Message."""

    def __init__(
        self,
        str_header: Optional[StorageHeader],
        std_header: StandardHeader,
        ext_header: Optional[ExtendedHeader],
        payload: Optional[Payload],
    ) -> None:
        """Create DltMessage object.

        In most cases, the constructor do not have to be called directly.
        The following factory methods can be used instead of it:
        - create_non_verbose_message
        - create_verbose_message
        - create_from_bytes

        Args:
            str_header (Optional[StorageHeader]): Storage Header of the message
            std_header (StandardHeader): Standard Header of the message
            ext_header (Optional[ExtendedHeader]): Extended Header of the message
            payload (Optional[Payload]): Payload of the message
        """
        self.str_header = str_header
        self.std_header = std_header
        self.ext_header = ext_header
        self.payload = payload

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.str_header == other.str_header
                and self.std_header == other.std_header
                and self.ext_header == other.ext_header
                and self.payload == other.payload
            )
        return False

    def __str__(self) -> str:
        """Get overview of the message.

        Overview is string of the following format:
        [<Time> ][<Timestamp> ]<Count>[ <Ecuid>][ <Apid>][ <Ctid>][ <SessionId>]
        [ <Type>][ <Subtype>][ <Mode>][ <#Args>][ <Payload>]

        Returns:
            str: Overview of the message
        """
        ret = []
        if self.str_header is not None:
            ret.append(
                datetime.fromtimestamp(self.str_header.seconds, timezone.utc).strftime(
                    "%Y/%m/%d %H:%M:%S"
                )
                + "."
                + str(self.str_header.microseconds).zfill(6)
            )
        if self.std_header.timestamp is not None:
            ret.append(
                str(int(self.std_header.timestamp / 10000))
                + "."
                + str(int(self.std_header.timestamp % 10000)).zfill(4)
            )
        ret.append(str(self.std_header.message_counter))
        if self.std_header.ecu_id is not None:
            ret.append(self.std_header.ecu_id)
        elif self.str_header is not None:
            ret.append(self.str_header.ecu_id)
        if self.ext_header is not None:
            ret.append(self.ext_header.application_id)
            ret.append(self.ext_header.context_id)
        if self.std_header.session_id is not None:
            ret.append(str(self.std_header.session_id))
        if self.ext_header is not None:
            ret.append(_MESSAGE_TYPE_STR.get(self.ext_header.message_type, "unknown"))
            if self.ext_header.message_type == MessageType.DLT_TYPE_LOG:
                ret.append(
                    _MESSAGE_LOG_INFO_STR.get(
                        self.ext_header.message_log_info, "unknown"
                    )
                )
            if self.ext_header.message_type == MessageType.DLT_TYPE_APP_TRACE:
                ret.append(
                    _MESSAGE_TRACE_INFO_STR.get(
                        self.ext_header.message_trace_info, "unknown"
                    )
                )
            if self.ext_header.message_type == MessageType.DLT_TYPE_NW_TRACE:
                ret.append(
                    _MESSAGE_BUS_INFO_STR.get(
                        self.ext_header.message_bus_info, "unknown"
                    )
                )
            if self.ext_header.message_type == MessageType.DLT_TYPE_CONTROL:
                ret.append(
                    _MESSAGE_CONTROL_INFO_STR.get(
                        self.ext_header.message_control_info, "unknown"
                    )
                )
        if self.ext_header is not None and self.ext_header.verbose:
            ret.append("verbose")
        else:
            ret.append("non-verbose")
        if self.ext_header is not None:
            ret.append(str(self.ext_header.number_of_arguments))
        if self.payload is not None:
            ret.append(str(self.payload))
        return " ".join(ret)

    @classmethod
    def create_non_verbose_message(
        cls,
        message_id: int,
        non_static_data: bytes,
        ext_header: Optional[ExtendedHeader] = None,
        timestamp: Optional[int] = None,
        session_id: Optional[int] = None,
        ecu_id: Optional[str] = None,
        message_counter: int = 0,
        version_number: int = 1,
        msb_first: bool = False,
        str_header: StorageHeader = None,
    ) -> "DltMessage":
        """Create DltMessage object as Non-Verbose mode.

        Returns:
            DltMessage: DltMessage object as Non-Verbose mode
        """
        payload = NonVerbosePayload(message_id, non_static_data, msb_first)
        std_header = cls._create_standard_header(
            payload.bytes_length,
            ext_header,
            timestamp,
            session_id,
            ecu_id,
            message_counter,
            version_number,
            msb_first,
        )
        return cls(str_header, std_header, ext_header, payload)

    @classmethod
    def create_verbose_message(
        cls,
        arguments: List[Argument],
        message_type: MessageType,
        message_type_info: MessageTypeInfo,
        application_id: str,
        context_id: str,
        timestamp: Optional[int] = None,
        session_id: Optional[int] = None,
        ecu_id: Optional[str] = None,
        message_counter: int = 0,
        version_number: int = 1,
        msb_first: bool = False,
        str_header: StorageHeader = None,
    ) -> "DltMessage":
        """Create DltMessage object as Verbose mode.

        Returns:
            DltMessage: DltMessage object as Verbose mode
        """
        payload = VerbosePayload(arguments)
        ext_header = ExtendedHeader(
            True,
            message_type,
            message_type_info,
            len(arguments),
            application_id,
            context_id,
        )
        std_header = cls._create_standard_header(
            payload.bytes_length,
            ext_header,
            timestamp,
            session_id,
            ecu_id,
            message_counter,
            version_number,
            msb_first,
        )
        return cls(str_header, std_header, ext_header, payload)

    @staticmethod
    def _create_standard_header(
        payload_length: int,
        ext_header: Optional[ExtendedHeader],
        timestamp: Optional[int],
        session_id: Optional[int],
        ecu_id: Optional[str],
        message_counter: int,
        version_number: int,
        msb_first: bool,
    ) -> StandardHeader:
        if ext_header is None:
            use_extended_header = False
            ext_header_length = 0
        else:
            use_extended_header = True
            ext_header_length = ext_header.bytes_length
        std_header = StandardHeader(
            use_extended_header,
            msb_first,
            version_number,
            message_counter,
            0,  # temporary length; it will be set on the next statement
            ecu_id,
            session_id,
            timestamp,
        )
        std_header.length = payload_length + ext_header_length + std_header.bytes_length
        return std_header

    @classmethod
    def create_from_bytes(
        cls, data: bytes, with_storage_header: bool, encoding: Optional[str] = None
    ) -> "DltMessage":
        """Create DltMessage object from data bytes.

        Args:
            data (bytes): Data bytes
            with_storage_header (bool): The data has storage header or not

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            DltMessage: New DltMessage object
        """
        seek_pos = 0
        str_header = None
        str_header_length = 0
        if with_storage_header:
            str_header = StorageHeader.create_from_bytes(data)
            seek_pos += str_header.bytes_length
            str_header_length = str_header.bytes_length
        std_header = StandardHeader.create_from_bytes(data[seek_pos:])
        seek_pos += std_header.bytes_length
        ext_header = None
        ext_header_length = 0
        if std_header.use_extended_header:
            ext_header = ExtendedHeader.create_from_bytes(data[seek_pos:])
            ext_header_length = ext_header.bytes_length
            seek_pos += ext_header.bytes_length
        payload = None
        if std_header.length > std_header.bytes_length + ext_header_length:
            is_verbose = ext_header is not None and ext_header.verbose is True
            if is_verbose:
                payload = VerbosePayload.create_from_bytes(
                    data[seek_pos : std_header.length + str_header_length],
                    std_header.msb_first,
                    ext_header.number_of_arguments,
                    encoding,
                )
            else:
                payload = NonVerbosePayload.create_from_bytes(
                    data[seek_pos : std_header.length + str_header_length],
                    std_header.msb_first,
                )
        return cls(str_header, std_header, ext_header, payload)

    def to_bytes(self) -> bytes:
        """Convert to data bytes.

        Returns:
            bytes: Converted data bytes
        """
        data = b""
        if self.str_header is not None:
            data += self.str_header.to_bytes()
        data += self.std_header.to_bytes()
        if self.ext_header is not None:
            data += self.ext_header.to_bytes()
        if self.payload is not None:
            data += self.payload.to_bytes(self.std_header.msb_first)
        return data

    @property
    def verbose(self) -> bool:
        """Check the message is verbose mode or non-verbose mode.

        Returns:
            bool:
                - False: Non-Verbose mode
                -  True: Verbose mode
        """
        return False if self.ext_header is None else self.ext_header.verbose

    @property
    def non_verbose_payload(self) -> NonVerbosePayload:
        """Get payload as non-verbose mode.

        Unexpected behaviors can be caused if the DltMessage is verbose mode.

        Returns:
            NonVerbosePayload: Payload as non-verbose mode
        """
        return cast(NonVerbosePayload, self.payload)

    @property
    def verbose_payload(self) -> VerbosePayload:
        """Get payload as verbose mode.

        Unexpected behaviors can be caused if the DltMessage is non-verbose mode.

        Returns:
            NonVerbosePayload: Payload as verbose mode
        """
        return cast(VerbosePayload, self.payload)
