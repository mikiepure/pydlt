# PyDLT

A pyre-python library to handle AUTOSAR DLT protocol, which is based on
AUTOSAR Specification of Diagnostic Log and Trace V1.2.0 R4.0 Rev3, Section 7.7 Protocol Specification.

## Limitation

The following format of Type Info in a Payload has not been supported.

- TYPE_LENGTH_128BIT
- TYPE_ARRAY
- VARIABLE_INFO
- FIXED_POINT
- TRACE_INFO
- TYPE_STRUCT
