"""Provide header class of the DLT protocol. """
import struct
from enum import IntEnum
from typing import Optional, cast

###############################################################################
# Standard Header of the DLT protocol
# It can be checked at following sections:
# - 7.7.2 Header Definition of the Dlt Protocol
# - 7.7.3 Standard Header
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


class StandardHeader:
    """The Standard Header of a DLT Message."""

    # length of the bytes data
    DATA_MIN_LENGTH = 4

    # bit masks to get/set values in Header Type
    USE_EXTENDED_HEADER_MASK = 0b00000001
    MSB_FIRST_MASK = 0b00000010
    WITH_ECU_ID_MASK = 0b00000100
    WITH_SESSION_ID_MASK = 0b00001000
    WITH_TIMESTAMP_MASK = 0b00010000
    VERSION_NUMBER_MASK = 0b11100000

    _VERSION_NUMBER_SHIFT = 5

    # struct format for pack/unpack
    STRUCT_MIN_FORMAT = ">BBH"

    def __init__(
        self,
        use_extended_header: bool,
        msb_first: bool,
        version_number: int,
        message_counter: int,
        length: int,
        ecu_id: Optional[str] = None,
        session_id: Optional[int] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        """Create StandardHeader object.

        Args:
            use_extended_header (bool): If set, the Extended Header is transmitted.
            msb_first (bool): If set, the payload data is in big endian format,
                              else in little endian format.
            version_number (int): Version number of Dlt Data protocol
            message_counter (int): Continuous number of message
            length (int): Length of the complete message in bytes
            ecu_id (Optional[str]): Unique address of sender
            session_id (Optional[int]): Session number
            timestamp (Optional[int]): Continuous time / ticks from the ECU
                                       at the moment the message is sent to Dlt
        """
        self.use_extended_header = use_extended_header
        self.msb_first = msb_first
        self.version_number = version_number
        self.message_counter = message_counter
        self.length = length
        self.ecu_id = ecu_id
        self.session_id = session_id
        self.timestamp = timestamp

    def __repr__(self):
        val = (
            f"StandardHeader(use_extended_header={self.use_extended_header}, "
            f"msb_first={self.msb_first}, version_number={self.version_number}, "
            f"message_counter={self.message_counter}, length={self.length}"
        )
        if self.ecu_id is not None:
            val += f', ecu_id="{self.ecu_id}"'
        if self.session_id is not None:
            val += f", session_id={self.session_id}"
        if self.timestamp is not None:
            val += f", timestamp={self.timestamp}"
        val += ")"
        return val

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.use_extended_header == other.use_extended_header
                and self.msb_first == other.msb_first
                and self.version_number == other.version_number
                and self.message_counter == other.message_counter
                and self.length == other.length
                and self.ecu_id == other.ecu_id
                and self.session_id == other.session_id
                and self.timestamp == other.timestamp
            )
        return False

    @classmethod
    def create_from_bytes(cls, data: bytes) -> "StandardHeader":
        """Create StandardHeader object from data bytes.

        Args:
            data (bytes): Data bytes

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            StandardHeader: New StandardHeader object
        """
        # validate arguments
        data_length = len(data)
        if data_length < cls.DATA_MIN_LENGTH:
            raise ValueError(
                f"Unexpected length of the data: {data_length} / "
                f"Standard Header must be {cls.DATA_MIN_LENGTH} or more"
            )

        # get header type
        ueh = bool(data[0] & cls.USE_EXTENDED_HEADER_MASK)
        msbf = bool(data[0] & cls.MSB_FIRST_MASK)
        weid = bool(data[0] & cls.WITH_ECU_ID_MASK)
        wsid = bool(data[0] & cls.WITH_SESSION_ID_MASK)
        wtms = bool(data[0] & cls.WITH_TIMESTAMP_MASK)
        vers = int((data[0] & cls.VERSION_NUMBER_MASK) >> cls._VERSION_NUMBER_SHIFT)

        # validate data
        unpack_format = cls.STRUCT_MIN_FORMAT
        expected_data_length = cls.DATA_MIN_LENGTH
        if weid:
            expected_data_length += 4
            unpack_format += "4s"
        if wsid:
            expected_data_length += 4
            unpack_format += "I"
        if wtms:
            expected_data_length += 4
            unpack_format += "I"
        if data_length < expected_data_length:
            raise ValueError(
                f"Unexpected length of the data: {data_length} / "
                f"Standard Header with Header Type: "
                f"WEID={weid} WSID={wsid} WTMS={wtms} "
                f"must be {expected_data_length} or more"
            )

        # parse bytes
        entries = struct.unpack_from(unpack_format, data)
        mcnt = entries[1]
        length = entries[2]
        entry_index = 3
        ecu = None
        if weid:
            ecu = _ascii_decode(entries[entry_index])
            entry_index += 1
        seid = None
        if wsid:
            seid = entries[entry_index]
            entry_index += 1
        tmsp = None
        if wtms:
            tmsp = entries[entry_index]

        return cls(ueh, msbf, vers, mcnt, length, ecu, seid, tmsp)

    def to_bytes(self) -> bytes:
        """Convert to data bytes.

        Returns:
            bytes: Converted data bytes
        """
        data = struct.pack(
            self.STRUCT_MIN_FORMAT, self.header_type, self.message_counter, self.length
        )
        # with_ecu_id is not used to avoid False Positive error of PyRights
        if self.ecu_id is not None:
            data += struct.pack(">4s", _ascii_encode(self.ecu_id))
        if self.with_session_id:
            data += struct.pack(">I", self.session_id)
        if self.with_timestamp:
            data += struct.pack(">I", self.timestamp)
        return data

    @property
    def bytes_length(self) -> int:
        """Get length of the data bytes.

        Returns:
            int: Length of the data bytes
        """
        length = self.DATA_MIN_LENGTH
        if self.with_ecu_id:
            length += 4
        if self.with_session_id:
            length += 4
        if self.with_timestamp:
            length += 4
        return length

    @property
    def header_type(self) -> int:
        """Get Header Type.

        Returns:
            int: Header Type
        """
        htyp = self.version_number << self._VERSION_NUMBER_SHIFT
        if self.use_extended_header:
            htyp |= self.USE_EXTENDED_HEADER_MASK
        if self.msb_first:
            htyp |= self.MSB_FIRST_MASK
        if self.with_ecu_id:
            htyp |= self.WITH_ECU_ID_MASK
        if self.with_session_id:
            htyp |= self.WITH_SESSION_ID_MASK
        if self.with_timestamp:
            htyp |= self.WITH_TIMESTAMP_MASK
        return htyp

    @property
    def with_ecu_id(self) -> bool:
        """Check WEID (With ECU ID) bit is set in the Header Type.

        Returns:
            bool:
                - True: The Standard Header has ECU ID.
                - False: The Standard Header does not have ECU ID.
        """
        return self.ecu_id is not None

    @property
    def with_session_id(self) -> bool:
        """Check WSID (With Session ID) bit is set in the Header Type.

        Returns:
            bool:
                - True: The Standard Header has Session ID.
                - False: The Standard Header does not have Session ID.
        """
        return self.session_id is not None

    @property
    def with_timestamp(self) -> bool:
        """Check WTMS (With Timestamp) bit is set in the Header Type.

        Returns:
            bool:
                - True: The Standard Header has Timestamp.
                - False: The Standard Header does not have Timestamp.
        """
        return self.timestamp is not None


###############################################################################
# Extended Header of the DLT protocol
# It can be checked at following sections:
# - 7.7.2 Header Definition of the Dlt Protocol
# - 7.7.4 Dlt Extended Header
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


class MessageType(IntEnum):
    """A definition of Message Type in DLT Extended Header."""

    DLT_TYPE_LOG = 0x0
    DLT_TYPE_APP_TRACE = 0x1
    DLT_TYPE_NW_TRACE = 0x2
    DLT_TYPE_CONTROL = 0x3


class MessageTypeInfo(IntEnum):
    """A definition of Message Type Info in DLT Extended Header."""


class MessageLogInfo(MessageTypeInfo):
    """A definition of Message Log Info in DLT Extended Header."""

    DLT_LOG_FATAL = 0x1
    DLT_LOG_ERROR = 0x2
    DLT_LOG_WARN = 0x3
    DLT_LOG_INFO = 0x4
    DLT_LOG_DEBUG = 0x5
    DLT_LOG_VERBOSE = 0x6


class MessageTraceInfo(MessageTypeInfo):
    """A definition of Message Trace Info in DLT Extended Header."""

    DLT_TRACE_VARIABLE = 0x1
    DLT_TRACE_FUNCTON_IN = 0x2
    DLT_TRACE_FUNCTON_OUT = 0x3
    DLT_TRACE_STATE = 0x4
    DLT_TRACE_VFB = 0x5


class MessageBusInfo(MessageTypeInfo):
    """A definition of Message Trace Info in DLT Extended Header."""

    DLT_NW_TRACE_IPC = 0x1
    DLT_NW_TRACE_CAN = 0x2
    DLT_NW_TRACE_FLEXRAY = 0x3
    DLT_NW_TRACE_MOST = 0x4


class MessageControlInfo(MessageTypeInfo):
    """A definition of Message Control Info in DLT Extended Header."""

    DLT_CONTROL_REQUEST = 0x1
    DLT_CONTROL_RESPONSE = 0x2
    DLT_CONTROL_TIME = 0x3


class ExtendedHeader:
    """The Extended Header of a DLT Message."""

    # length of the bytes data
    DATA_LENGTH = 10

    # bit masks to get/set values in Message Info
    VERBOSE_MASK = 0b00000001
    MESSAGE_TYPE_MASK = 0b00001110
    MESSAGE_TYPE_INFO_MASK = 0b11110000

    _MESSAGE_TYPE_SHIFT = 1
    _MESSAGE_TYPE_INFO_SHIFT = 4

    # struct format for pack/unpack
    STRUCT_FORMAT = ">BB4s4s"

    def __init__(
        self,
        verbose: bool,
        message_type: MessageType,
        message_type_info: MessageTypeInfo,
        number_of_arguments: int,
        application_id: str,
        context_id: str,
    ) -> None:
        """Create ExtendedHeader object.

        Args:
            verbose (bool): If set, a description of the transmitted data is provided
                            within the payload.
                            If not set, this information will be given within a file.
            message_type (MessageType): A field describes the transmitted Dlt message
            message_type_info (MessageTypeInfo): A field depends on the Message Type
            number_of_arguments (int): Number of arguments in the message payload
            application_id (str): Number / ID of application
            context_id (str): Unique ID of logging / tracing context
        """
        self.verbose = verbose
        self.message_type = message_type
        self.message_type_info = message_type_info
        self.number_of_arguments = number_of_arguments
        self.application_id = application_id
        self.context_id = context_id

    def __repr__(self):
        return (
            f"ExtendedHeader(verbose={self.verbose}, "
            f"message_type={self.message_type}, "
            f"message_type_info={self.message_type_info}, "
            f"number_of_arguments={self.number_of_arguments}, "
            f'application_id="{self.application_id}", '
            f'context_id="{self.context_id}")'
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.verbose == other.verbose
                and self.message_type == other.message_type
                and self.message_type_info == other.message_type_info
                and self.number_of_arguments == other.number_of_arguments
                and self.application_id == other.application_id
                and self.context_id == other.context_id
            )
        return False

    @classmethod
    def create_from_bytes(cls, data: bytes) -> "ExtendedHeader":
        """Create ExtendedHeader object from data bytes.

        Args:
            data (bytes): Data bytes

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            ExtendedHeader: New ExtendedHeader object
        """
        # validate arguments
        data_length = len(data)
        if data_length < cls.DATA_LENGTH:
            raise ValueError(
                f"Unexpected length of the data: {data_length} / "
                f"Extended Header must be {cls.DATA_LENGTH} or more"
            )

        # parse bytes
        entries = struct.unpack_from(cls.STRUCT_FORMAT, data)
        msin = entries[0]
        verb = bool(msin & cls.VERBOSE_MASK)
        mstp = (msin & cls.MESSAGE_TYPE_MASK) >> cls._MESSAGE_TYPE_SHIFT
        mtin = (msin & cls.MESSAGE_TYPE_INFO_MASK) >> cls._MESSAGE_TYPE_INFO_SHIFT
        noar = entries[1]
        apid = _ascii_decode(entries[2])
        ctid = _ascii_decode(entries[3])

        return cls(verb, mstp, mtin, noar, apid, ctid)

    def to_bytes(self) -> bytes:
        """Convert to data bytes.

        Returns:
            bytes: Converted data bytes
        """
        msin = 0
        if self.verbose:
            msin |= self.VERBOSE_MASK
        msin |= (self.message_type << self._MESSAGE_TYPE_SHIFT) & self.MESSAGE_TYPE_MASK
        msin |= (
            self.message_type_info << self._MESSAGE_TYPE_INFO_SHIFT
        ) & self.MESSAGE_TYPE_INFO_MASK
        return struct.pack(
            self.STRUCT_FORMAT,
            msin,
            self.number_of_arguments,
            _ascii_encode(self.application_id),
            _ascii_encode(self.context_id),
        )

    @property
    def bytes_length(self) -> int:
        """Get length of the data bytes.

        Returns:
            int: Length of the data bytes
        """
        return self.DATA_LENGTH

    @property
    def message_log_info(self) -> MessageLogInfo:
        """Get Message Log Info.

        message_type_info is converted to MessageLogInfo.

        Returns:
            MessageLogInfo: Message Log Info
        """
        return cast(MessageLogInfo, self.message_type_info)

    @property
    def message_trace_info(self) -> MessageTraceInfo:
        """Get Message Trace Info.

        message_type_info is converted to MessageTraceInfo.

        Returns:
            MessageTraceInfo: Message Trace Info
        """
        return cast(MessageTraceInfo, self.message_type_info)

    @property
    def message_bus_info(self) -> MessageBusInfo:
        """Get Message Bus Info.

        message_type_info is converted to MessageBusInfo.

        Returns:
            MessageBusInfo: Message Bus Info
        """
        return cast(MessageBusInfo, self.message_type_info)

    @property
    def message_control_info(self) -> MessageControlInfo:
        """Get Message Control Info.

        message_type_info is converted to MessageControlInfo.

        Returns:
            MessageControlInfo: Message Control Info
        """
        return cast(MessageControlInfo, self.message_type_info)


###############################################################################
# Storage Header of the DLT protocol
# It can be checked at following sections:
# - 7.7.6 Additional Message Parts
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


class StorageHeader:
    """The Storage Header of a DLT Message."""

    # length of the bytes data
    DATA_LENGTH = 16

    # "DLT"+0x01
    DLT_PATTERN = b"\x44\x4C\x54\x01"

    # struct format for pack/unpack
    STRUCT_FORMAT = "<Ii4s"

    def __init__(self, seconds: int, microseconds: int, ecu_id: str) -> None:
        """Create StorageHeader object.

        Args:
            seconds (int): A seconds since 01.01.1970 (unix time)
            microseconds (int): A microseconds of the second (between 0 – 1.000.000)
            ecu_id (str): The ECU ID
        """
        self.seconds = seconds
        self.microseconds = microseconds
        self.ecu_id = ecu_id

    def __repr__(self):
        return (
            f"StorageHeader(seconds={self.seconds}, "
            f'microseconds={self.microseconds}, ecu_id="{self.ecu_id}")'
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.seconds == other.seconds
                and self.microseconds == other.microseconds
                and self.ecu_id == other.ecu_id
            )
        return False

    @classmethod
    def create_from_bytes(cls, data: bytes) -> "StorageHeader":
        """Create StorageHeader object from data bytes.

        Args:
            data (bytes): Data bytes

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            StorageHeader: New StorageHeader object
        """
        # validate arguments
        data_length = len(data)
        if data_length < cls.DATA_LENGTH:
            raise ValueError(
                f"Unexpected length of the data: {data_length} / "
                f"Storage Header must be {cls.DATA_LENGTH} or more"
            )

        # parse bytes
        dlt_pattern = data[:4]
        if dlt_pattern != cls.DLT_PATTERN:
            raise ValueError(
                f"DLT-Pattern is not found in the data: {dlt_pattern} / "
                f"Beginning of Storage Header must be {cls.DLT_PATTERN}"
            )
        entries = struct.unpack_from(cls.STRUCT_FORMAT, data, 4)
        seconds = entries[0]
        microseconds = entries[1]
        ecu_id = _ascii_decode(entries[2])

        return cls(seconds, microseconds, ecu_id)

    def to_bytes(self) -> bytes:
        """Convert to data bytes.

        Returns:
            bytes: Converted data bytes
        """
        return self.DLT_PATTERN + struct.pack(
            self.STRUCT_FORMAT,
            self.seconds,
            self.microseconds,
            _ascii_encode(self.ecu_id),
        )

    @property
    def bytes_length(self) -> int:
        """Get length of the data bytes.

        Returns:
            int: Length of the data bytes
        """
        return self.DATA_LENGTH


def _ascii_decode(ascii: bytes) -> str:
    """Decode bytes of ASCII charactors to string.

    Args:
        ascii (bytes): ASCII charactors

    Returns:
        str: Converted string
    """
    return ascii.decode("ascii", "replace").replace("\x00", "")


def _ascii_encode(ascii: str) -> bytes:
    """Encode string of ASCII charactors to bytes.

    Args:
        ascii (str): ASCII charactors

    Returns:
        str: Converted bytes
    """
    return ascii.encode("ascii", "replace")
