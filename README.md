# fips-utils

Grab-bag of useful fips utilities which are generally useful but don't
quite fit into the core fips project.

## Usage

Just add the ```fips-utils``` import to the ```fips.yml``` file
of your project:

```yaml
---
imports:
    fips-utils:
        git: https://github.com/fips-libs/fips-utils
```

Now run ```fips fetch```.

New fips verbs (aka commands) can be listed via ```fips help```, new
build configs via ```fips list configs```.

For help on generators (aka custom build jobs) read on:

## Generators (aka Custom Build Jobs)

Those are usually available through cmake macros:

- [fipsutil_copy()](fips-files/generators/copy.py): copy files from project directory to deployment directory
- [fipsutil_embed()](fips-files/generators/embed.py): embed binary files into C headers

For usage examples, see the [sokol-samples](https://github.com/floooh/sokol-samples/)
and [chips-test](https://github.com/floooh/chips-test/) repositories.

## Verbs

- **markdeep**: build and view source-embedded Markdeep documentation
- **valgrind**: run an app target through valgrind
- **gdb**: debug an app target in gdb


