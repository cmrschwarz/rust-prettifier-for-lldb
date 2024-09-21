# Rust Prettifier for LLDB

Script to add Rust specific pretty-printing to the LLDB debugger.

## Usage Standalone LLDB

To load the script into your lldb instance, execute the following lldb command:

```
command script import /path/to/rust_prettifier_for_lldb.py
```

## Usage VSCode + lldb-dap

To use this script in VSCode,

1. Install the [lldb-dap](https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.lldb-dap) extension.
2. Use something akin to the following `.vscode/launch.json`:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "lldb-dap",
            "request": "launch",
            "name": "Debug",
            "program": "${workspaceFolder}/program/to/debug",
            "args": [],
            "cwd": "${workspaceFolder}",
            "initCommands": [
                "command script import /path/to/rust_prettifier_for_lldb.py"
            ],
        }
    ]
}
```
