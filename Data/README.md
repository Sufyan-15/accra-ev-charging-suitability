# Data sources and expected folder structure

The source datasets are not redistributed in this repository. Download or extract them from the official providers, and organise them as follows:

```text
Data/
└── Raw/
    ├── Fuel_Stations/
    │   └── Fuel_Stations_Accra.geojson
    ├── Activity_Centres/
    │   ├── Accra_Universities.geojson
    │   ├── Accra_Markets.geojson
    │   ├── Accra_Malls.geojson
    │   └── Accra_Transport_Terminal.geojson
    ├── Substations/
    │   └── Accra_Substations.geojson
    └── Population/
        └── gha_pop_2026_CN_100m_R2025A_v1.tif
```

The scripts create `Data/Processed/` and `Data/Final/` outputs during execution.

## OpenStreetMap-derived vector data

Fuel stations, universities, markets, shopping malls, transport terminals and electrical substations were extracted from [OpenStreetMap](https://www.openstreetmap.org) through [Overpass Turbo](https://overpass-turbo.eu).

- Fuel-station extraction date: 5 June 2026
- Activity-centre extraction date: 16 June 2026
- Electrical-substation extraction date: 28 June 2026
- Search area used in the queries: `Accra`

Principal tags:

| Dataset | OpenStreetMap tag |
|---|---|
| Fuel stations | `amenity=fuel` |
| Universities | `amenity=university` |
| Markets | `amenity=marketplace` |
| Shopping malls | `shop=mall` |
| Transport terminals | `amenity=bus_station` |
| Electrical substations | `power=substation` |

OpenStreetMap data are available under the Open Data Commons Open Database License. Users should retain the required attribution to OpenStreetMap contributors.

## WorldPop population raster

The population input is the constrained WorldPop R2025A version 1 estimate for Ghana at approximately 100 m resolution. The raster represents estimated residents per grid cell in WGS84.

- Dataset page: [WorldPop Ghana population counts](https://hub.worldpop.org/geodata/summary?id=73551)
- Persistent identifier: [https://doi.org/10.5258/SOTON/WP00839](https://doi.org/10.5258/SOTON/WP00839)
- Expected filename: `gha_pop_2026_CN_100m_R2025A_v1.tif`

Recommended dataset citation:

> Bondarenko, M., et al. (2025). *Constrained estimates of 2015–2030 total number of people per grid square at a resolution of 3 arc (approximately 100 m at the equator), R2025A version 1*. WorldPop, School of Geography and Environmental Science, University of Southampton. https://doi.org/10.5258/SOTON/WP00839

WorldPop datasets are made available under the licence stated on the official dataset page. Users should verify and comply with the current terms when downloading the data.
