# Power BI-tema

Temaet ligger som kode i `src/`, og `dist/theme.json` bygges ud fra det.

```
src/theme.json              farver, tekstklasser m.m. (alt undtagen visualStyles)
src/visualStyles/*.json     én fil pr. visualtype ("*" ligger i _default.json)
scripts/build.py            samler src/ til dist/theme.json og validerer
scripts/split.py            deler en samlet temafil op i src/ (fx en ny Microsoft-version)
```

## Daglig brug

```
python scripts/build.py          # bygger dist/theme.json
python scripts/build.py --check  # validerer uden at skrive fil
```

Importér `dist/theme.json` i Power BI Desktop (View > Themes > Browse for themes), eller
kopiér den ind i PBIP-rapporterne.

## Ny samlet temafil (fx ny Microsoft-version)

```
python scripts/split.py sti/til/ny-fil.json
git diff
```

`split.py` overskriver kun de visualtyper, der findes i filen. Egne filer som `DAPSPC.json` bliver
liggende, og `git diff` viser præcis, hvad der har ændret sig.

## Udgivelse

Push til `main` bygger og validerer. Et tag som `v1.0.0` udgiver desuden `theme.json` som release.
