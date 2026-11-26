# Tide & Dark

[Find a coastal photography window](https://coolcode.ca/tide-and-dark/)

Choose Halifax Harbour, Yarmouth, Saint John Harbour, Point Atkinson, Vancouver Harbour, Victoria Harbour or Tofino. Daylight mode compares official CHS predicted high/low events with sunrise and sunset, highlights daylight within a selected interval around low tide, and offers nearby ECCC current weather and forecasts. The original dark-sky mode remains available.

For dark-sky photography: Select a starting date, twilight threshold, maximum illuminated Moon fraction and time around a modeled low. You can also require the Moon to be below the local horizon. Select a match for five-minute sky conditions, download the results with timezone-independent timestamps or share the view by copying its URL.

<!-- coolcode:guide -->
Choose a coastal station and date in daylight mode to compare official tide predictions with sunrise and sunset. Current weather is fetched only when requested and is labelled separately from the selected tide date. Switch to dark-sky photography for the independent long-range tide model and Moon filters; the two modes use different height datums.
Peggy’s Cove and Stanley Park photography presets link to golden/blue-hour, Moon and cloud-aware sessions in Nightfinder. Named coastal selections can be saved locally. The tide reference is labelled separately from the photography coordinates.
<!-- /coolcode:guide -->

## Official daylight planner

The [CHS IWLS API](https://tides.gc.ca/en/web-services-offered-canadian-hydrographic-service) supplies `wlp-hilo` predicted extrema for seven configured stations, refreshed daily at 08:43 UTC by `.github/workflows/daylight.yml`. The snapshot has a fourteen-day planning horizon plus edge days. Retrieval time, horizon, quality code and source URL are retained. The high/low labels are strict extrema derived from neighbouring official predicted heights; ambiguous events remain unclassified. Heights are metres above chart datum, including possible negative values. They must never be compared directly with the zero-mean heights in the independent model. Predictions do not include all weather effects or establish safe beach access.

The full required CHS attribution and no-navigation notice is prominently displayed in the daylight planner. This free noncommercial derivative is provided under the [CHS licence agreement](https://tides.gc.ca/en/licence-agreement). It is not for navigation. CHS data are not covered by the research constants’ CC BY licence. A capture older than 48 hours is flagged; an expired horizon is explicitly marked and out-of-range dates show no current result. Collection failure keeps the prior deployment.

SunCalc calculates sunrise/sunset at each CHS station, or at the selected photography preset coordinates. ECCC city weather is fetched directly from [MSC GeoMet](https://api.weather.gc.ca/collections/citypageweather-realtime) only after the weather button is selected. The observing-station name and timestamp are shown; observations can be inland or at an airport and are not shoreline measurements. Older observations are flagged. Issued forecast times and periods remain visible; weather is never stretched to the multiweek tide horizon. Weather Window opens at the station coordinates for more regional alerts and air quality.

## Independent dark-sky model: data and interpretation

Hart-Davis, Michael G., Denise Dettmering and Florian Seitz (2022), [TICON-3, PANGAEA](https://doi.org/10.1594/PANGAEA.951610), CC BY 4.0. This project selects seven coastal gauge records and transforms twelve published amplitudes and Greenwich phase lags into an independent series using UTide. The retained lines are M2, S2, N2, K2, K1, O1, P1, Q1, M4, MS4, MN4 and M6. Sea-level offsets use a harmonic mean of zero. A chart datum or an actual beach elevation is needed to infer an absolute water level. Historical gauge record dates and the calculated prediction period are shown separately. Dataset transformations and any errors belong to this project.

The generator uses nodal corrections and Greenwich astronomical arguments, samples heights every ten minutes and interpolates extrema from three neighboring points. It retains all modeled lows, including small mixed-tide minima. [SunCalc 1.9.0](https://github.com/mourner/suncalc/tree/v1.9.0) computes solar altitude, lunar altitude and illuminated fraction at each site, under the included BSD licence. Five-minute samples define concurrent conditions. Intervals require at least two consecutive qualifying samples. Search dates refer to the local date of the low; a window may extend into the previous or following date. Astronomical darkness uses a solar centre altitude of −18°, nautical −12° and civil −6°.

A launch cross-check against official high/low predictions for November 1–7, 2026 matched 13 Halifax lows within 12 minutes, 12 Saint John lows within 16 minutes and 13 Point Atkinson lows within 38 minutes. These checks quantify only that sample. Wind, atmospheric pressure, coastal terrain, a local tide phase difference, cloud and light pollution affect a particular photograph. Use the official Canadian tide tables and site access guidance for shoreline or navigation decisions. The night-mode estimates continue to use the independently licensed research constants. Daylight mode uses the separate official CHS capture. [CHS data licence](https://www.tides.gc.ca/en/licence-agreement).

## Maintenance

The monthly refresh retrieves the original archive, records its SHA-256 digest and rebuilds a horizon through the end of the following calendar year. It stops if the coastal gauge IDs or constituent coverage change. The compact static data, retrieval date and covered interval are committed after checks. Queries run in the visitor’s browser. App use requires no account or key.

Run `python -m pip install -r scripts/requirements.txt` and `OPENBLAS_NUM_THREADS=1 python scripts/refresh.py` to refresh. To build offline run `node --test tests/*.test.mjs`, `python -m unittest discover -s tests` and `python scripts/build.py`. CI also runs Chromium tests and publishes the checked build.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

## Expand or customize

Edit `web/daylight-config.json`. Each station needs a unique app `id`, five-digit CHS `code`, IWLS `station_id`, official coordinates, province, IANA time zone, and ECCC `weather_city` / `weather_name`. Resolve station IDs and supported `wlp-hilo` series from `https://api-iwls.dfo-mpo.gc.ca/api/v1/stations`; city IDs come from the ECCC citypageweather collection. Add a station beyond the initial seven, run `python3 scripts/refresh_daylight.py`, review `web/daylight.json` and `web/daylight-status.json`, run all checks and push to main. The collector supports 1–25 configured stations and 3–21 horizon days without starter-count assumptions; requests are spaced to remain below the documented 30/minute CHS limit. Historical captures with different station counts remain readable. The independent harmonic model retains its original separate configuration in `scripts/refresh.py`.

The independent Linux scheduler should dispatch both allowlisted collector workflows: `pages.yml` monthly (original model) and `daylight.yml` daily (official tides). Monitor `daylight-status.json.retrieved` within 36 hours and its `through` horizon; retain the original `status.json` model-horizon probe. The schedule guard covers both collectors and itself. A normal code push is an offline build and does not silently claim a new source capture.

## Privacy

Date, tide and sky calculations stay in the browser; named coastal selections are stored locally only when **Save location** is used. Up to 20 names, public preset IDs and tide-reference station IDs can be saved; the Delete control removes an entry. No cookies are used. A shared URL includes the selected public station, date and filters. Pressing the optional weather button sends only the configured public ECCC city ID to ECCC. Weather Window links include the public station coordinates. No account or API key is required. Local assets are content-versioned to avoid mixed cached releases.

## Photography presets

`web/photo-places.mjs` contains Peggy’s Cove / Peggys Point and Stanley Park / approximate centre, with official coordinate-source links. They use Halifax and Vancouver Harbour, respectively, as clearly labelled regional tide references. **Halifax tide predictions are not Peggy’s Cove tide predictions.** Local tide timing, height, wind and wave exposure can differ. Selecting another CHS station clears the photography preset; it never relabels a station prediction as a beach measurement.

The daylight computation uses the selected photography coordinates while official extrema retain their original station, chart datum and dates. Nightfinder links carry the shared `photo_place` ID and selected date, with cloud forecasts requested there on demand. Saved coastal selections retain the current date rather than restoring an obsolete forecast date. Existing daily official-tide and monthly independent-model schedules are unchanged; no new API key or Worker update is needed.
