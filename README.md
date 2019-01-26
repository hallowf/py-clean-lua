
### Parameters

- -ugl/--ugliffy
  * Replaces new line characters "\n" with spaces
- -clW/--clearWhites
  * Removes excess whitespace
- -remG/--removeGlobals
  * Removes globals defined
  * Pass in a file name trough the command-line or config
  * the file must be in the root folder as the program
- -uC/--useConfig
  * Use configuration file see [Default Config file](#-default-config-file)

### Parser
[ 'func',
    'x',
    [ 'a', 'b', 'c' ],
    [ [ 'ass', 'l', 'p' ], [ 'ass', 'x', 'z' ]
  ]
]


### Default Config file

```
[DEFAULT]
clearWhites = True
removeGlobals = .lua_globals
ugglify = False
toRem = Debugging
        SomeOtherGlobal
        SomeOtherLocal

```
