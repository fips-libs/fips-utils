# fips-utils

Grab-bag of useful fips utilities which are generally useful but don't
quite fit into the core fips project.

## Usage

Just add the ```fips-utils``` import to the ```fips.yml``` file
of your project and run ```fips fetch```.

```yaml
---
imports:
    fips-utils:
        git: https://github.com/fips-libs/fips-utils
```

Now run ```fips help```, this should list additional verbs (subcommands),
```fips list configs```, and check out the additional generators
under ```fips-files/generators``` and cmake helper macros in
```fips-files/include.cmake```.

## Generators (aka Custom Build Jobs)

Those are usually available through cmake macros:

- [fipsutil_copy()](fips-files/generators/copy.py): copy files from project directory to deployment directory
- [fipsutil_embed()](fips-files/generators/embed.py): embed binary files into C headers

For usage examples, see the [sokol-samples](https://github.com/floooh/sokol-samples/)
and [chips-test](https://github.com/floooh/chips-test/) repositories.

## Verbs (TODO)

