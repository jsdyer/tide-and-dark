# Tide & Dark

[Find a coastal photography window](https://coolcode.ca/tide-and-dark/)

Choose Halifax Harbour, Yarmouth, Saint John Harbour, Point Atkinson, Vancouver Harbour, Victoria Harbour or Tofino. Select a starting date, twilight threshold, maximum illuminated Moon fraction and time around a modeled low. You can also require the Moon to be below the local horizon. Select a match for five-minute sky conditions, download the results with timezone-independent timestamps or share the view by copying its URL.

<!-- coolcode:guide -->
Try Halifax starting December 1, 2026 with astronomical darkness, at most 25% lunar illumination and one hour on either side of low tide. The December 3 local evening window surrounds a modeled 10:08 p.m. low with a roughly 22% illuminated Moon.
<!-- /coolcode:guide -->

## Data and interpretation

Hart-Davis, Michael G., Denise Dettmering and Florian Seitz (2022), [TICON-3, PANGAEA](https://doi.org/10.1594/PANGAEA.951610), CC BY 4.0. This project selects seven coastal gauge records and transforms twelve published amplitudes and Greenwich phase lags into an independent series using UTide. The retained lines are M2, S2, N2, K2, K1, O1, P1, Q1, M4, MS4, MN4 and M6. Sea-level offsets use a harmonic mean of zero. A chart datum or an actual beach elevation is needed to infer an absolute water level. Historical gauge record dates and the calculated prediction period are shown separately. Dataset transformations and any errors belong to this project.

The generator uses nodal corrections and Greenwich astronomical arguments, samples heights every ten minutes and interpolates extrema from three neighboring points. It retains all modeled lows, including small mixed-tide minima. [SunCalc 1.9.0](https://github.com/mourner/suncalc/tree/v1.9.0) computes solar altitude, lunar altitude and illuminated fraction at each site, under the included BSD licence. Five-minute samples define concurrent conditions. Intervals require at least two consecutive qualifying samples. Search dates refer to the local date of the low; a window may extend into the previous or following date. Astronomical darkness uses a solar centre altitude of −18°, nautical −12° and civil −6°.

A launch cross-check against official high/low predictions for November 1–7, 2026 matched 13 Halifax lows within 12 minutes, 12 Saint John lows within 16 minutes and 13 Point Atkinson lows within 38 minutes. These checks quantify only that sample. Wind, atmospheric pressure, coastal terrain, a local tide phase difference, cloud and light pollution affect a particular photograph. Use the official Canadian tide tables and site access guidance for shoreline or navigation decisions. The public site links to the [CHS station directory](https://tides.gc.ca/en/stations) and uses the independently licensed research constants for its own estimates. [CHS data licence](https://www.tides.gc.ca/en/licence-agreement).

## Maintenance

The monthly refresh retrieves the original archive, records its SHA-256 digest and rebuilds a horizon through the end of the following calendar year. It stops if the coastal gauge IDs or constituent coverage change. The compact static data, retrieval date and covered interval are committed after checks. Queries run in the visitor’s browser. App use requires no account or key.

Run `python -m pip install -r scripts/requirements.txt` and `OPENBLAS_NUM_THREADS=1 python scripts/refresh.py` to refresh. To build offline run `node --test tests/*.test.mjs`, `python -m unittest discover -s tests` and `python scripts/build.py`. CI also runs Chromium tests and publishes the checked build.
