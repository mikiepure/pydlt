"""Provide payload class of the DLT protocol. """
import struct
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import List, Optional, Union

###############################################################################
# Payload of the DLT protocol
# It can be checked at following sections:
# - 7.7.5 Payload
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


class Payload(ABC):
    """The Payload of a DLT Message."""

    def __str__(self) -> str:
        return self._to_str()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_bytes(False) == other.to_bytes(False)
        return False

    @abstractmethod
    def to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        """Convert to data bytes.

        Args:
            msb_first (Optional[bool]): If set, the payload data is in big endian,
                                        else in little endian.

        Returns:
            bytes: Converted data bytes
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def bytes_length(self) -> int:
        """Get length of the data bytes.

        Returns:
            int: Length of the data bytes
        """
        raise NotImplementedError

    @abstractmethod
    def _to_str(self) -> str:
        """Convert payload to human readable string.

        Returns:
            str: Human readable string.
        """
        raise NotImplementedError


###############################################################################
# Payload: Non-Verbose Mode of the DLT protocol
# It can be checked at following sections:
# - 7.7.5.1 Non-Verbose Mode
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


class NonVerbosePayload(Payload):
    """The Payload of Non-Verbose Mode of a DLT Message."""

    # minimum length of the bytes data
    _MESSAGE_ID_LENGTH = 4

    def __init__(
        self, message_id: int, non_static_data: bytes, msb_first: Optional[bool] = None
    ) -> None:
        """Create NonVerbosePayload object.

        Args:
            message_id (int): Unique ID for a specific Dlt message
            non_static_data (bytes): All non-static information of a Dlt message.
            msb_first (Optional[bool]): If set, the payload data is in big endian,
                                        else in little endian.
        """
        self.message_id = message_id
        self.non_static_data = non_static_data
        self.msb_first = msb_first

    @classmethod
    def create_from_bytes(cls, data: bytes, msb_fitst: bool) -> "NonVerbosePayload":
        """Create NonVerbosePayload object from data bytes.

        Args:
            data (bytes): Data bytes
            msb_first (bool): If set, the payload data is in big endian format,
                              else in little endian format.

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            NonVerbosePayload: New NonVerbosePayload object
        """
        # validate arguments
        data_length = len(data)
        if data_length < cls._MESSAGE_ID_LENGTH:
            raise ValueError(
                f"Unexpected length of the data: {data_length} / "
                f"Payload of Non-Verbose Mode must not be < {cls._MESSAGE_ID_LENGTH}"
            )

        # parse bytes
        endian = ">" if msb_fitst else "<"
        entries = struct.unpack(f"{endian}I", data[:4])
        message_id = entries[0]

        return cls(message_id, data[4:], msb_fitst)

    def to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        """Convert to data bytes.

        Args:
            msb_first (Optional[bool]): If set, the payload data is in big endian,
                                        else in little endian.

        Returns:
            bytes: Converted data bytes
        """
        if msb_first is not None:
            endian = ">" if msb_first else "<"
        elif self.msb_first is not None:
            endian = ">" if self.msb_first else "<"
        else:
            raise ValueError("Endian is not known")
        return struct.pack(f"{endian}I", self.message_id) + self.non_static_data

    @property
    def bytes_length(self) -> int:
        """Get length of the data bytes.

        Returns:
            int: Length of the data bytes
        """
        return self._MESSAGE_ID_LENGTH + len(self.non_static_data)

    def _to_str(self) -> str:
        """Convert payload to human readable string.

        Returns:
            str: Human readable string.
        """
        return f"[{self.message_id}] {self.non_static_data.hex()}"


###############################################################################
# Payload: Verbose Mode of the DLT protocol
# It can be checked at following sections:
# - 7.7.5.2 Verbose Mode
# in AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3
###############################################################################


# Base type:
# - Type Bool (BOOL)
# - Type Signed (SINT)
# - Type Unsigned (UINT)
# - Type Float (FLOA)
# - Type Array (ARAY)    *not supported*
# - Type String (STRG)
# - Type Raw (RAWD)
# - Trace Info (TRAI)    *not supported*
# - Type Struct (STRU)   *not supported*
# Option type:
# - Type Length (TYLE)   *supported with limitation*
# - Variable Info (VARI) *not supported*
# - Fixed Point (FIXP)   *not supported*
# - String Coding (SCOD)
# fmt: off
MASK_BASE_TYPE     = 0b00000000000000000110011111110000  # noqa: E221
MASK_TYPE_LENGTH   = 0b00000000000000000000000000001111  # noqa: E221
MASK_VARIABLE_INFO = 0b00000000000000000000100000000000  # noqa: E221
MASK_FIXED_POINT   = 0b00000000000000000001000000000000  # noqa: E221
MASK_STRING_CODING = 0b00000000000000111000000000000000  # noqa: E221
# fmt: on


class TypeInfo(IntEnum):
    """A definition of Type Info of the Argument of Verbose Mode Paylaod.

    Note: The following format has not been supported:
    - TYPE_LENGTH_128BIT
    - TYPE_ARRAY
    - VARIABLE_INFO
    - FIXED_POINT
    - TRACE_INFO
    - TYPE_STRUCT
    """

    # fmt: off
    # Type Length
    TYPE_LENGTH_8BIT    = 0b00000000000000000000000000000001    # noqa: E221
    TYPE_LENGTH_16BIT   = 0b00000000000000000000000000000010    # noqa: E221
    TYPE_LENGTH_32BIT   = 0b00000000000000000000000000000011    # noqa: E221
    TYPE_LENGTH_64BIT   = 0b00000000000000000000000000000100    # noqa: E221
    TYPE_LENGTH_128BIT  = 0b00000000000000000000000000000101    # noqa: E221
    # Type Bool
    TYPE_BOOL           = 0b00000000000000000000000000010000    # noqa: E221
    # Type Signed
    TYPE_SIGNED         = 0b00000000000000000000000000100000    # noqa: E221
    # Type Unsigned
    TYPE_UNSIGNED       = 0b00000000000000000000000001000000    # noqa: E221
    # Type Float
    TYPE_FLOAT          = 0b00000000000000000000000010000000    # noqa: E221
    # Type Array
    TYPE_ARRAY          = 0b00000000000000000000000100000000    # noqa: E221
    # Type String
    TYPE_STRING         = 0b00000000000000000000001000000000    # noqa: E221
    # Type Raw
    TYPE_RAW            = 0b00000000000000000000010000000000    # noqa: E221
    # Variable Info
    VARIABLE_INFO       = 0b00000000000000000000100000000000    # noqa: E221
    # Fixed Point
    FIXED_POINT         = 0b00000000000000000001000000000000    # noqa: E221
    # Trace Info
    TRACE_INFO          = 0b00000000000000000010000000000000    # noqa: E221
    # Type Struct
    TYPE_STRUCT         = 0b00000000000000000100000000000000    # noqa: E221
    # String Coding
    STRING_CODING_ASCII = 0b00000000000000000000000000000000    # noqa: E221
    STRING_CODING_UTF8  = 0b00000000000000001000000000000000    # noqa: E221
    # fmt: on


class Argument(ABC):

    _TYPE_INFO_LENGTH = 4

    def __init__(self, msb_first: Optional[bool]):
        self.msb_first = msb_first

    def __str__(self) -> str:
        return self._to_str()

    @property
    @abstractmethod
    def _type_info(self) -> int:
        raise NotImplementedError

    @classmethod
    def create_from_bytes(
        cls, data: bytes, msb_first: bool, encoding: Optional[str] = None
    ) -> "Argument":
        """Create Argument object from data bytes.

        Raises:
            ValueError: Unsupported TypeInfo is in the data.

        Returns:
            Argument: Argument object
        """
        endian = ">" if msb_first else "<"
        type_info = struct.unpack(f"{endian}I", data[: cls._TYPE_INFO_LENGTH])[0]
        type_info_base = type_info & MASK_BASE_TYPE
        if type_info_base == TypeInfo.TYPE_BOOL:
            return ArgumentBool.from_data_payload(
                data[cls._TYPE_INFO_LENGTH :], msb_first
            )
        elif type_info_base == TypeInfo.TYPE_SIGNED:
            type_info_length = type_info & MASK_TYPE_LENGTH
            if type_info_length == TypeInfo.TYPE_LENGTH_8BIT:
                return ArgumentSInt8.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_16BIT:
                return ArgumentSInt16.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_32BIT:
                return ArgumentSInt32.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_64BIT:
                return ArgumentSInt64.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
        elif type_info_base == TypeInfo.TYPE_UNSIGNED:
            type_info_length = type_info & MASK_TYPE_LENGTH
            if type_info_length == TypeInfo.TYPE_LENGTH_8BIT:
                return ArgumentUInt8.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_16BIT:
                return ArgumentUInt16.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_32BIT:
                return ArgumentUInt32.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_64BIT:
                return ArgumentUInt64.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
        elif type_info_base == TypeInfo.TYPE_FLOAT:
            type_info_length = type_info & MASK_TYPE_LENGTH
            if type_info_length == TypeInfo.TYPE_LENGTH_32BIT:
                return ArgumentFloat32.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
            elif type_info_length == TypeInfo.TYPE_LENGTH_64BIT:
                return ArgumentFloat64.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], msb_first
                )
        elif type_info_base == TypeInfo.TYPE_STRING:
            type_info_string_coding = type_info & MASK_STRING_CODING
            if type_info_string_coding == TypeInfo.STRING_CODING_ASCII:
                return ArgumentString.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], False, msb_first, encoding
                )
            elif type_info_string_coding == TypeInfo.STRING_CODING_UTF8:
                return ArgumentString.from_data_payload(
                    data[cls._TYPE_INFO_LENGTH :], True, msb_first
                )
        elif type_info_base == TypeInfo.TYPE_RAW:
            return ArgumentRaw.from_data_payload(
                data[cls._TYPE_INFO_LENGTH :], msb_first
            )

        raise ValueError(f"Unsupported TypeInfo: {bin(type_info)}")

    @classmethod
    @abstractmethod
    def from_data_payload(cls, data_payload: bytes, msb_first: bool) -> "Argument":
        """Create Argument object from data payload bytes.

        Args:
            data_payload (bytes): Data payload bytes (without type info)
            msb_first (bool): If set, the payload data is in big endian format,
                              else in little endian format.

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            Argument: New Argument object
        """
        raise NotImplementedError

    def to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        """Convert to data bytes.

        Args:
            msb_first (Optional[bool]): If set, the payload data is in big endian,
                                        else in little endian.

        Returns:
            bytes: Converted data bytes
        """
        if msb_first is not None:
            endian = ">" if msb_first else "<"
        elif self.msb_first is not None:
            endian = ">" if self.msb_first else "<"
        else:
            raise ValueError("Endian is not known")
        return struct.pack(f"{endian}I", self._type_info) + self.data_payload_to_bytes(
            msb_first
        )

    @property
    def bytes_length(self) -> int:
        """Get length of the data bytes (including type info).

        Returns:
            int: Length of the data bytes
        """
        return self._TYPE_INFO_LENGTH + self.data_payload_length

    @abstractmethod
    def _to_str(self) -> str:
        """Convert payload to human readable string.

        Returns:
            str: Human readable string.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def data_payload_length(self) -> int:
        """Get length of the data payload.

        Returns:
            int: Length of the data payload
        """
        raise NotImplementedError

    @abstractmethod
    def data_payload_to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        """Convert data payload to bytes.

        Returns:
            bytes: Convert data payload
        """
        raise NotImplementedError


class ArgumentNumBase(Argument):
    """It is a class for number base argument.

    It has a data field for value.
    A length of the data field is changed by type info.

    """

    def __init__(
        self,
        data: Union[bool, int, float],
        msb_first: Optional[bool] = None,
    ):
        super().__init__(msb_first)
        self.data = data

    @staticmethod
    @abstractmethod
    def _struct_format() -> str:
        """Get format string for struct.pack() / struct.unpack().

        Returns:
            str: Format string for struct.pack() / struct.unpack().

        """
        raise NotImplementedError

    def _to_str(self) -> str:
        return str(self.data)

    @staticmethod
    @abstractmethod
    def _data_payload_length() -> int:
        raise NotImplementedError

    @classmethod
    def from_data_payload(cls, data_payload: bytes, msb_first: bool) -> "Argument":
        endian = ">" if msb_first else "<"
        return cls(
            struct.unpack(
                f"{endian}{cls._struct_format()}",
                data_payload[: cls._data_payload_length()],
            )[0],
            msb_first,
        )

    def data_payload_to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        if msb_first is not None:
            endian = ">" if msb_first else "<"
        elif self.msb_first is not None:
            endian = ">" if self.msb_first else "<"
        else:
            raise ValueError("Endian is not known")
        return struct.pack(f"{endian}{self._struct_format()}", self.data)


class ArgumentBool(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_BOOL | TypeInfo.TYPE_LENGTH_8BIT

    @staticmethod
    def _struct_format() -> str:
        return "?"

    @staticmethod
    def _data_payload_length() -> int:
        return 1

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentUInt8(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_UNSIGNED | TypeInfo.TYPE_LENGTH_8BIT

    @staticmethod
    def _struct_format() -> str:
        return "B"

    @staticmethod
    def _data_payload_length() -> int:
        return 1

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentUInt16(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_UNSIGNED | TypeInfo.TYPE_LENGTH_16BIT

    @staticmethod
    def _struct_format() -> str:
        return "H"

    @staticmethod
    def _data_payload_length() -> int:
        return 2

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentUInt32(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_UNSIGNED | TypeInfo.TYPE_LENGTH_32BIT

    @staticmethod
    def _struct_format() -> str:
        return "I"

    @staticmethod
    def _data_payload_length() -> int:
        return 4

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentUInt64(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_UNSIGNED | TypeInfo.TYPE_LENGTH_64BIT

    @staticmethod
    def _struct_format() -> str:
        return "Q"

    @staticmethod
    def _data_payload_length() -> int:
        return 8

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentSInt8(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_SIGNED | TypeInfo.TYPE_LENGTH_8BIT

    @staticmethod
    def _struct_format() -> str:
        return "b"

    @staticmethod
    def _data_payload_length() -> int:
        return 1

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentSInt16(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_SIGNED | TypeInfo.TYPE_LENGTH_16BIT

    @staticmethod
    def _struct_format() -> str:
        return "h"

    @staticmethod
    def _data_payload_length() -> int:
        return 2

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentSInt32(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_SIGNED | TypeInfo.TYPE_LENGTH_32BIT

    @staticmethod
    def _struct_format() -> str:
        return "i"

    @staticmethod
    def _data_payload_length() -> int:
        return 4

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentSInt64(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_SIGNED | TypeInfo.TYPE_LENGTH_64BIT

    @staticmethod
    def _struct_format() -> str:
        return "q"

    @staticmethod
    def _data_payload_length() -> int:
        return 8

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentFloat32(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_FLOAT | TypeInfo.TYPE_LENGTH_32BIT

    @staticmethod
    def _struct_format() -> str:
        return "f"

    @staticmethod
    def _data_payload_length() -> int:
        return 4

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentFloat64(ArgumentNumBase):
    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_FLOAT | TypeInfo.TYPE_LENGTH_64BIT

    @staticmethod
    def _struct_format() -> str:
        return "d"

    @staticmethod
    def _data_payload_length() -> int:
        return 8

    @property
    def data_payload_length(self) -> int:
        return self._data_payload_length()


class ArgumentByteBase(Argument):
    """It is a class for byte-base argument.

    It has a length field as 4 byte and data field for value.
    """

    LENGTH_SIZE = 2

    @property
    def data_payload_length(self) -> int:
        return self.LENGTH_SIZE + self.data_length

    @property
    @abstractmethod
    def data_length(self) -> int:
        raise NotImplementedError

    def data_payload_to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        if msb_first is not None:
            endian = ">" if msb_first else "<"
        elif self.msb_first is not None:
            endian = ">" if self.msb_first else "<"
        else:
            raise ValueError("Endian is not known")
        return struct.pack(f"{endian}H", self.data_length) + self.data_to_bytes()

    @abstractmethod
    def data_to_bytes(self) -> bytes:
        raise NotImplementedError


class ArgumentString(ArgumentByteBase):
    def __init__(
        self,
        data: str,
        is_utf8: bool = False,
        msb_first: Optional[bool] = None,
        encoding: Optional[str] = None,
    ):
        """Create argument of Type String.

        Args:
            data (str): A data payload of string.
            is_utf8 (bool, optional): Encoding of the string is UTF-8 if True, or ASCII.
                                      Defaults to True (UTF-8).
            msb_first (Optional[bool], optional): [description]. Defaults to None.
            encoding: custom 8-bit encoding that will be used for serialization
                      Has no effect if is_utf8 is set to True
        """
        super().__init__(msb_first)
        self.data = data
        self.is_utf8 = is_utf8
        self._encoding = self._encoding_format(is_utf8, encoding)

    def _to_str(self) -> str:
        return self.data

    @property
    def _type_info(self) -> int:
        type_info = TypeInfo.TYPE_STRING
        if self.is_utf8:
            type_info |= TypeInfo.STRING_CODING_UTF8
        return type_info

    @classmethod
    def from_data_payload(
        cls,
        data_payload: bytes,
        is_utf8: bool,
        msb_first: bool,
        encoding: Optional[str] = None,
    ) -> "Argument":
        endian = ">" if msb_first else "<"
        length = struct.unpack(f"{endian}H", data_payload[: cls.LENGTH_SIZE])[0]
        return cls(
            data_payload[cls.LENGTH_SIZE : cls.LENGTH_SIZE + length - 1].decode(
                cls._encoding_format(is_utf8, encoding), "replace"
            ),
            is_utf8,
            msb_first,
        )

    @property
    def data_length(self) -> int:
        return len(self.data.encode(self._encoding, "replace")) + 1

    def data_to_bytes(self) -> bytes:
        return self.data.encode(self._encoding, "replace") + b"\x00"

    @staticmethod
    def _encoding_format(is_utf8: bool, encoding: str) -> str:
        if encoding is None:
            encoding = "ascii"
        return "utf-8" if is_utf8 else encoding


class ArgumentRaw(ArgumentByteBase):
    def __init__(
        self,
        data: bytes,
        msb_first: Optional[bool] = None,
    ):
        super().__init__(msb_first)
        self.data = data

    def _to_str(self) -> str:
        return self.data.hex()

    @property
    def _type_info(self) -> int:
        return TypeInfo.TYPE_RAW

    @classmethod
    def from_data_payload(cls, data_payload: bytes, msb_first: bool) -> "Argument":
        endian = ">" if msb_first else "<"
        length = struct.unpack(f"{endian}H", data_payload[: cls.LENGTH_SIZE])[0]
        return cls(data_payload[cls.LENGTH_SIZE : cls.LENGTH_SIZE + length], msb_first)

    @property
    def data_length(self) -> int:
        return len(self.data)

    def data_to_bytes(self) -> bytes:
        return self.data


class VerbosePayload(Payload):
    """The Payload of Verbose Mode of a DLT Message."""

    def __init__(self, arguments: List[Argument]) -> None:
        """Create VerbosePayload object.

        Args:
            arguments (List[Argument]): A list of argument
        """
        self.arguments = arguments

    @classmethod
    def create_from_bytes(
        cls,
        data: bytes,
        msb_first: bool,
        number_of_arguments: int,
        encoding: Optional[str] = None,
    ) -> "VerbosePayload":
        """Create VerbosePayload object from data bytes.

        Args:
            data (bytes): Data bytes
            msb_first (bool): If set, the payload data is in big endian format,
                              else in little endian format.
            number_of_arguments: number of arguments within this payload data
            encoding: optional non-standard 8-bit string encoding

        Raises:
            ValueError: It can be caused by invalid data format.

        Returns:
            VerbosePayload: New VerbosePayload object
        """
        arguments = []
        offset = 0
        for _ in range(number_of_arguments):
            arg = Argument.create_from_bytes(data[offset:], msb_first, encoding)
            arguments.append(arg)
            offset += arg.bytes_length
        return cls(arguments)

    def to_bytes(self, msb_first: Optional[bool] = None) -> bytes:
        """Convert to data bytes.

        Args:
            msb_first (Optional[bool]): If set, the payload data is in big endian,
                                        else in little endian.

        Returns:
            bytes: Converted data bytes
        """
        data = b""
        for arg in self.arguments:
            data += arg.to_bytes(msb_first)
        return data

    @property
    def bytes_length(self) -> int:
        """Get length of the data bytes.

        Returns:
            int: Length of the data bytes
        """
        length = 0
        for arg in self.arguments:
            length += arg.bytes_length
        return length

    def _to_str(self) -> str:
        """Convert payload to human readable string.

        Returns:
            str: Human readable string.
        """
        return " ".join([str(arg) for arg in self.arguments])
