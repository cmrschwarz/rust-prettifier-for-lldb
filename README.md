# Rust Prettifier for LLDB

Script to add Rust specific pretty-printing to the LLDB debugger.

## Usage Standalone LLDB

To load the script into your lldb debugger instance, execute the following lldb command:

```
command script import /path/to/rust_prettifier_for_lldb.py

```


## Usage VSCode + code-lldb
To use this script in VSCode with the [code-lldb](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb) extension,
add the `preRunCommands` json tag to your launch configuration(s)
as shown in the example configuration below:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "lldb",
            "request": "launch",
            "name": "scr",
            "cargo": {
                "args": [
                    "build",
                ],
                "filter": {
                    "kind": "bin"
                }
            },
            "preRunCommands": [
                "command script import /path/to/your/checkout/of/rust_prettifier_for_lldb.py"
            ],
            "args": [],
         
           
        },
    ]
}
```

## Usage VSCode + lldb-dap

To use this script in VSCode with the [lldb-dap](https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.lldb-dap) extension, add the `initCommands` json tag to your launch configuration(s), as shown in the example configuration below:

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
                "command script import /path/to/your/checkout/of/rust_prettifier_for_lldb.py"
            ],
        }
    ]
}
```
