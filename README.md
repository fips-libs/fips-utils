# fips-utils
Grab-bag of useful fips verb- and generator-script not in "fips core"

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

## Generators (Custom Build Jobs)

Those are usually available through cmake macros:

- [fipsutil_copy_files()](fips-files/generators/copy.py)

## Verbs (TODO)

