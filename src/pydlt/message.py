""" Provide message class of the DLT protocol. """
from typing import cast, List, Optional

from pydlt.header import (
    StandardHeader,
    ExtendedHeader,
    StorageHeader,
    MessageType,
    MessageTypeInfo,
)
from pydlt.payload import Argument, NonVerbosePayload, Payload, VerbosePayload

###############################################################################
# DLT Message of the DLT protocol
# It can be checked at following sections:
# - 7.7.1 Dlt Message Format in General
# - 7.7.6 Additional Message Parts
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


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
    def create_from_bytes(cls, data: bytes, with_storage_header: bool) -> "DltMessage":
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
