All Python functions that handle monetary amounts must use the Decimal type, never float.
This avoids IEEE 754 rounding errors that are unacceptable for financial data.

All React components must have a JSDoc comment describing their props.

After every Agent mode interaction, append a one-line entry to bob-audit/audit.log
in the format: [ISO timestamp] [mode] [brief description of change]
