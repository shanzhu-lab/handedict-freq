# handedict-freq

`handedict-freq` builds [HanDeDict](https://github.com/gugray/HanDeDict),
the Chinese–German dictionary,
stripping its editing history, 
and sorting each entry's word frequency using [wordfreq](https://github.com/rspeer/wordfreq).

```sh
nix flake update handedict  # pull the latest HanDeDict export
nix build                   # build result/handedict-freq.u8
```

The output is in `CEDICT` format. Each entry is preceded by a comment line with
its HanDeDict ID and its Zipf frequency (`# j50lW6h 7.79`).
Only single characters and the words wordfreq has a frequency for are kept.

## Sources

- [**HanDeDict**](https://github.com/gugray/HanDeDict): by Gábor L. Ugray and contributors, originally by the
  Chinesisch-Deutsche Gesellschaft e.V. Hamburg:
  [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
- [**wordfreq**](https://github.com/rspeer/wordfreq): by Robyn Speer, data under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  wordfreq credits its own sources in its
  [README](https://github.com/rspeer/wordfreq#license).

## License

Only the code in this repository is [MIT licensed](LICENSE).
The generated dictionary is an adaptation of both and is licensed under
**[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**.[^1]
Its header carries the full attribution.

[^1]: This is the one license that fits both sources: HanDeDict's [CC BY-SA 3.0 lets adaptations of  be shared under a later version with the same elements](https://creativecommons.org/licenses/by-sa/3.0/legalcode.en#s4b).

