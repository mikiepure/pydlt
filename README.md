# PyDLT

A pyre-python library to handle AUTOSAR DLT protocol, which is based on
AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3, Section 7.7 Protocol Specification.

## Quick Start

### Write messages to DLT file

```py
from pydlt import (
    ArgumentString,
    DltFileWriter,
    DltMessage,
    MessageLogInfo,
    MessageType,
    StorageHeader,
)

# Create DLT message
msg1 = DltMessage.create_verbose_message(
    [ArgumentString("hello, pydlt!")],
    MessageType.DLT_TYPE_LOG,
    MessageLogInfo.DLT_LOG_INFO,
    "App",
    "Ctx",
    message_counter=0,
    str_header=StorageHeader(0, 0, "Ecu"),
)
print(msg1)
# > 1970/01/01 00:00:00.000000 0 Ecu App Ctx log info verbose 1 hello, pydlt!
msg2 = DltMessage.create_non_verbose_message(
    0,
    b"\x01\x02\x03",
    message_counter=1,
    str_header=StorageHeader(0, 0, "Ecu"),
)
print(msg2)
# > 1970/01/01 00:00:00.000000 1 Ecu non-verbose [0] 010203

# Write DLT messages to file
with DltFileWriter("<path to DLT file>") as writer:
    writer.write_messages([msg1, msg2])
```

### Read messages from DLT file

```py
from pydlt import DltFileReader

# Read DLT messages from file
for msg in DltFileReader("<path to DLT file>"):
    # Print overview of each DLT message
    print(msg)
```

## Limitation

The following format of Type Info in a Payload has not been supported.

- TYPE_LENGTH_128BIT
- TYPE_ARRAY
- VARIABLE_INFO
- FIXED_POINT
- TRACE_INFO
- TYPE_STRUCT
