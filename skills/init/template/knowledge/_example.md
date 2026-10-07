# Standard deviation (example page)

## Try it
```python
xs = [2, 4, 4, 4, 5, 5, 7, 9]
mean = sum(xs) / len(xs)
sd = (sum((x - mean) ** 2 for x in xs) / len(xs)) ** 0.5
print(mean, sd)  # 5.0 2.0
```
Change one value to 30 and predict the new SD before running it.

## Why it works
SD is the typical distance of a value from the mean. Squaring keeps negatives from cancelling
out; the square root brings the unit back.

## Connections
- Variance is SD squared (it would get its own page)
- Used in [[learning/_example/map]] for the A/B test

## Recall
- [b0 · due 2026-10-08] Why divide by n-1 instead of n for a sample?
- [b2 · due 2026-10-14] What does a larger SD tell you about the data?

## Log
- 2026-10-07 quiz: 3/4, missed: why divide by n-1

Sources: `raw/notes/stats-lecture-3.md` · Updated: 2026-10-07
