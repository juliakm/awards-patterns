# Experiments

One question per page: the guess, one chart, the answer, and a short "how I counted."

## Published

- Does the most-nominated film win Best Picture?

## Next

Early numbers below cover ceremonies through 2023 and come from a quick exploratory run. Recheck them through 2026 when writing the page.

- **Are Best Picture and Best Director splitting more often?** 4 of 19 from 1991 to 2009, then 6 of 14 from 2010 to 2023.
- **Is "overdue" real?** Acting nominees with 3+ losses and no win won 29% of the time (27 of 93). Nominees who already have an Oscar won 14.5% (52 of 359). The average is about 20%.
- **Which other Oscar goes with Best Picture?** Since 1981, 31 of 43 Best Picture winners also won Director, and more were nominated for Editing (40) than Director (39).
- **Who has had the worst luck?** *The Turning Point* and *The Color Purple* went 0 for 11. Glenn Close and Peter O'Toole went 0 for 8. Henry Fonda waited 41 ceremonies for a first win.
- **Can a simple cheat sheet win your Oscar pool?** Write the rules down before the March 14, 2027 ceremony (recheck the date), then score them live.

## Before relying on numbers

- Spot-check against the Academy's database. `data/curated/spot_check_kaggle_v13.csv` (private) lists cases to check.
- The loader drops rows the file marks as unofficial, unless they won or are from ceremony 2, which never announced nominees. Recount the early numbers above with it.
- The Academy's terms for its data haven't been reviewed. Publish summaries and small tables only, and keep raw files private.

## Shelved

The forecast model, its policy and the precursor, pundit and box-office source audits are preserved at the `forecast-era` git tag. Model code is on the local `draft-features` branch.
