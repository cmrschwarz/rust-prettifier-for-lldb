# Rust Prettifier for LLDB

[![CI](https://github.com/cmrschwarz/rust-prettifier-for-lldb/actions/workflows/ci.yml/badge.svg)](https://github.com/cmrschwarz/rust-prettifier-for-lldb/actions/workflows/ci.yml)


Script to add Rust specific pretty-printing to the LLDB debugger.

With the recent removal of Rust specific pretty printing from [CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb), debugging Rust, especially
enums, has become quite painful.

This script is meant as a temporary fix until the situation of the
ecosystem improves, see [Compatability](#compatability).



## Standalone LLDB

To load the script into your lldb debugger instance, execute the following lldb command:

```
command script import <path to rust_prettifier_for_lldb.py>
```

## Usage with VSCode Debug Adapters
To use this script with VSCode debug adapters you have to instruct them
to execute the same lldb command as above before the actual debugging session.

**Don't forget to replace `<path to rust_prettifier_for_lldb.py>` 
with the actual path on your local machine in the examples below**.

If you dislike linking to an absolute path on your machine I recommend
placing (or symlinking) `rust_prettifier_for_lldb.py` into the
`.vscode` folder of your repository, so you can use
`"${workspaceFolder}/.vscode/rust_prettifier_for_lldb.py"` as the path.

### VSCode + CodeLLDB
For the [CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb) extension, add the `preRunCommands` json tag to your launch configuration(s).
It is also recommended to set `"expressions": "simple"` to fix an issue with
the array subscript operator (`[..]`) in the Debug Watch Window. 
Here's an example configuration for your `.vscode/launch.json`:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "lldb",
            "request": "launch",
            "name": "Debug",
            "cargo": {
                "args": [
                    "build",
                ],
                "filter": {
                    "name": "<your binary name here>",
                    "kind": "bin"
                }
            },
            "expressions": "simple",
            "preRunCommands": [
                "command script import <path to rust_prettifier_for_lldb.py>"
            ],
            "args": [],
         
           
        },
    ]
}
```

### VSCode + lldb-dap

For the [lldb-dap](https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.lldb-dap) extension, add the `initCommands` JSON tag to your `.vscode/launch.json` configuration(s), as shown in the example below:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "lldb-dap",
            "request": "launch",
            "name": "Debug",
            "program": "<binary name here>",
            "args": [],
            "cwd": "${workspaceFolder}",
            "initCommands": [
                "command script import <path to rust_prettifier_for_lldb.py>"
            ],
        }
    ]
}
```



## Compatability
This Script was developed for LLDB Version `19.0.0`, aswell as `19.1.0-codelldb` (Version currently bundled by [CodeLLDB](https://github.com/vadimcn/codelldb)).

At the time of writing, it is known to work well with the latest stable Version Rust (`1.82.0`). 

If you are using older versions of Rust or LLDB this script might not work for you.

Due to the changing nature of the Rust Standard Library internals aswell
as the LLDB represenation of them, this will never be more than a temporary hack
that's constantly in danger of becoming outdated.
The hope is that [Rust's own  Pretty Printers](https://github.com/rust-lang/rust/blob/717f5df2c308dfb4b7b8e6c002c11fe8269c4011/src/etc/lldb_providers.py) will eventually ship in a functional state, superseeding this temporary bandaid.


The plan for this script is to live at head, and hopefully get retired sooner rather than later.


I'm happy to accept pull requests to improve this script or even add support
for commonly used collection types of third party crates, 
as long as you supply testcases to make sure your additions can be maintained. 

## Thank You

Thank you to Vadim Chugunov (@vadimcn) for the wonderful CodeLLDB
and the [starting point](https://github.com/vadimcn/codelldb/blob/05502bf75e4e7878a99b0bf0a7a81bba2922cbe3/formatters/rust.py) for this script.

## Support

If this script has helped you out a a small [Github Sponsors Donation](https://github.com/sponsors/cmrschwarz) or a Github Star would make me very happy, and show the Rust Project Maintainers that a solid solution for debugging Rust is worth their time.   
