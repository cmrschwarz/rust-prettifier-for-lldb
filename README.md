# Rust Prettifier for LLDB

[![CI](https://github.com/cmrschwarz/rust-prettifier-for-lldb/actions/workflows/ci.yml/badge.svg)](https://github.com/cmrschwarz/rust-prettifier-for-lldb/actions/workflows/ci.yml)


Script to add Rust specific pretty-printing to the LLDB debugger.

With the recent [removal](https://github.com/vadimcn/codelldb/issues/1166) of Rust specific pretty printing from
[CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb), debugging Rust, especially
enums, has become quite painful.

This script is meant as a temporary fix until the situation of the
ecosystem improves, see [Compatability](#compatability).


### With Prettifier
![After](after.png)


### Without Prettifier
![Before](before.png)


## Standalone LLDB

To load the script into your lldb debugger instance, execute the following lldb command:

```
command script import /path/to/rust_prettifier_for_lldb.py
```

[`rust_prettifier_for_lldb.py`](https://raw.githubusercontent.com/cmrschwarz/rust-prettifier-for-lldb/refs/heads/main/rust_prettifier_for_lldb.py)
is the only file from this Repository that you actually need. You can download it separately from the
[Releases](https://github.com/cmrschwarz/rust-prettifier-for-lldb/releases) section.

## Usage with VSCode Debug Adapters
To use this script with VSCode debug adapters you have to instruct them
to execute the same lldb command as above before the actual debugging session.

**Either place `rust_prettifier_for_lldb.py` into your `.vscode` folder,
or replace `${workspaceFolder}/.vscode/rust_prettifier_for_lldb.py`
with the actual path you chose in the examples below**.

### VSCode + CodeLLDB
For the
[CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb)
extension, add the `preRunCommands` json tag from the example below
to your launch configuration(s) or alternatively to your user settings under
`lldb.launch.preRunCommands`.

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
                    "name": "NAME_OF_YOUR_BINARY_HERE",
                    "kind": "bin"
                }
            },
            "expressions": "simple",
            "preRunCommands": [
                // !! change this path if you placed the script somewhere else !!
                "command script import ${workspaceFolder}/.vscode/rust_prettifier_for_lldb.py"
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
            "program": "NAME_OF_YOUR_BINARY_HERE",
            "args": [],
            "cwd": "${workspaceFolder}",
            "initCommands": [
                // !! change this path if you placed the script somewhere else !!
                "command script import ${workspaceFolder}/.vscode/rust_prettifier_for_lldb.py"
            ],
        }
    ]
}
```



## Compatability
This script was developed for LLDB Version `19.0.0`, aswell as `19.1.0-codelldb` (version currently bundled by
[CodeLLDB](https://github.com/vadimcn/codelldb)).

At the time of writing, it is known to work well with the latest stable version Rust (`1.82.0`).

Initially this did not support Windows, although @jesnor was able to get it partially working.
Any improvements on that front would of course be welcomed.

If you are using older versions of Rust or LLDB this script might not work for you.

Due to the changing nature of the Rust Standard Library internals aswell
as the LLDB representation of them, this will never be more than a temporary hack
that's constantly in danger of becoming outdated.
The hope is that
[Rust's own  Pretty Printers](https://github.com/rust-lang/rust/blob/717f5df2c308dfb4b7b8e6c002c11fe8269c4011/src/etc/lldb_providers.py)
will eventually ship in a functional state, superseeding this temporary bandaid.


The plan for this script is to live at head, and hopefully get retired sooner rather than later.


I'm happy to accept pull requests to improve this script or even add support
for commonly used collection types of third party crates,
as long as you supply testcases to make sure your additions can be maintained.

Note (2025-01-18): There are
[known cases](https://github.com/cmrschwarz/rust-prettifier-for-lldb/blob/4e630a6576f033eba0565a554198dc2ef6fc0379/tests/test_enums.py#L95)
where it does not seem feasible to report the correct answer without fixing the upstream issues in Rust or LLVM.
You might in rare cases even get incorrect results.

## Thank You

Thank you to Vadim Chugunov (@vadimcn) for the wonderful CodeLLDB and the
[starting point](https://github.com/vadimcn/codelldb/blob/05502bf75e4e7878a99b0bf0a7a81bba2922cbe3/formatters/rust.py)
for this script.

## Support

If this script has helped you out a a Github Star :sparkles: would make me very happy,
and maybe help demonstrate to the Rust Project Maintainers that a solid solution
for debugging Rust is something that many people desire.
