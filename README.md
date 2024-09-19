# LLDB-RUST

Script to add Rust specific pretty-printing to the lldb debugger.


## Usage Standalone LLDB
To load the script into your lldb instance, execute the following lldb command:

```
command script import <path_to_rust.py>
``` 


## VSCode
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
            "program": "${workspaceFolder}/target/debug/<your_binary_name>",
            "args": [],
            "cwd": "${workspaceFolder}",
            "initCommands": [
                "command script import <path_to_rust.py>"
            ],
        }
    ]
}
```



