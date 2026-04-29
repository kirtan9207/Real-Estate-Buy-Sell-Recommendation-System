# Data Dictionary — Bangalore Real Estate Dataset

## Grain Definition
**1 row = 1 property listing** in the Bangalore real estate market.

## Dataset Overview
- **Records:** 20,000
- **Source:** Synthetically generated with realistic Bangalore market parameters
- **Time Range:** 2020-01-01 to 2024-12-31
- **Geography:** 20 Bangalore localities

---

## Field Definitions

| # | Field Name | Type | Range / Values | Unit | Description |
|---|---|---|---|---|---|
| 1 | `property_id` | string | BLR-10001 to BLR-30000 | — | Unique property listing identifier |
| 2 | `location` | string | 20 Bangalore localities | — | Locality name (e.g., Whitefield, Koramangala) |
| 3 | `latitude` | float | 12.84 – 13.12 | degrees | Geographic latitude with ±0.01° noise |
| 4 | `longitude` | float | 77.50 – 77.78 | degrees | Geographic longitude with ±0.01° noise |
| 5 | `builder_name` | string | 10 builders | — | Real estate developer name |
| 6 | `property_type` | string | Apartment, Villa, Penthouse, Builder Floor, Plot | — | Type of property |
| 7 | `furnishing` | string | Unfurnished, Semi-furnished, Fully-furnished | — | Furnishing status |
| 8 | `listing_type` | string | Resale, New Launch, Ready to Move | — | Listing category |
| 9 | `sqft` | integer | 500 – 5,000 | sq. ft. | Built-up area |
| 10 | `bedrooms` | integer | 1 – 5 | count | Number of bedrooms |
| 11 | `bathrooms` | integer | 1 – 4 | count | Number of bathrooms |
| 12 | `balconies` | integer | 0 – 3 | count | Number of balconies |
| 13 | `parking` | integer | 0 – 2 | count | Number of parking spots |
| 14 | `floor` | integer | 1 – 25 | — | Floor number of the unit |
| 15 | `total_floors` | integer | 3 – 30 | — | Total floors in the building |
| 16 | `age` | integer | 0 – 25 | years | Age of the property |
| 17 | `amenities_count` | integer | 2 – 20 | count | Number of amenities (gym, pool, club, etc.) |
| 18 | `distance_metro` | float | 0.1 – 15.0 | km | Distance to nearest metro station |
| 19 | `distance_school` | float | 0.2 – 8.0 | km | Distance to nearest school |
| 20 | `distance_hospital` | float | 0.3 – 10.0 | km | Distance to nearest hospital |
| 21 | `distance_cbd` | float | 1.0 – 30.0 | km | Distance to CBD (MG Road) |
| 22 | `connectivity_score` | float | 1.0 – 10.0 | score | Derived connectivity index |
| 23 | `safety_score` | integer | 5 – 10 | score | Locality safety rating |
| 24 | `school_score` | integer | 4 – 10 | score | Proximity & quality of nearby schools |
| 25 | `price` | integer | ~20L – ~8Cr | INR | Listed property price |
| 26 | `demand_score` | integer | 30 – 98 | score | Market demand indicator for the locality |
| 27 | `liquidity_score` | integer | 25 – 95 | score | How quickly a property sells in the locality |
| 28 | `roi` | float | 5.0 – 25.0 | % | Expected annual return on investment |
| 29 | `market_trend` | float | 0.03 – 0.20 | ratio | YoY growth rate for the locality |
| 30 | `listing_date` | string | 2020-01-01 to 2024-12-31 | date | Date the property was listed |

---

## Locations

| Location | Base Price (₹/sqft) | Growth Rate | Segment | Lat | Lon |
|---|---|---|---|---|---|
| Whitefield | 8,500 | 12% | Mid-range | 12.9698 | 77.7499 |
| Indiranagar | 18,000 | 8% | Premium | 12.9719 | 77.6412 |
| Electronic City | 6,000 | 15% | Emerging | 12.8452 | 77.6635 |
| Koramangala | 15,000 | 7% | Premium | 12.9352 | 77.6245 |
| HSR Layout | 11,000 | 10% | Mid-range | 12.9121 | 77.6446 |
| Sarjapur Road | 7,500 | 14% | Emerging | 12.9063 | 77.6823 |
| Hebbal | 9,500 | 11% | Mid-range | 13.0354 | 77.5988 |
| Bannerghatta Road | 7,000 | 13% | Budget | 12.8711 | 77.5922 |
| Marathahalli | 8,000 | 11% | Mid-range | 12.9591 | 77.7009 |
| JP Nagar | 9,000 | 9% | Mid-range | 12.9063 | 77.5857 |
| Jayanagar | 14,000 | 6% | Premium | 12.9250 | 77.5838 |
| BTM Layout | 9,500 | 10% | Mid-range | 12.9166 | 77.6101 |
| Yelahanka | 5,500 | 16% | Emerging | 13.1007 | 77.5963 |
| KR Puram | 5,000 | 14% | Budget | 13.0098 | 77.6967 |
| Rajajinagar | 12,000 | 7% | Premium | 12.9866 | 77.5527 |
| Malleswaram | 13,000 | 6% | Premium | 13.0035 | 77.5648 |
| Basavanagudi | 11,500 | 8% | Mid-range | 12.9422 | 77.5737 |
| Devanahalli | 4,500 | 18% | Emerging | 13.1124 | 77.7130 |
| Kanakapura Road | 5,500 | 15% | Budget | 12.8684 | 77.5578 |
| Hennur | 6,500 | 13% | Emerging | 13.0452 | 77.6388 |

---

## Builders

Prestige Group, Sobha Ltd, Brigade Group, Puravankara, Godrej Properties, Lodha Group, Salarpuria Sattva, Mantri Developers, Shriram Properties, Assetz Property Group

---

## Assumptions

1. **Prices are listed prices**, not transaction prices.
2. **Age = 0** indicates under-construction or newly completed.
3. **Amenities count** is the total number of distinct amenities in the project (gym, pool, clubhouse, garden, etc.).
4. **Market trend** reflects the historical YoY appreciation rate of the locality.
5. **ROI** is estimated annual ROI based on location growth rate + market demand.
6. **Distance values** are Euclidean approximations, not actual road distances.
7. **Price computation** uses: `base_price_per_sqft × sqft + bedroom_premium + amenity_premium + proximity_premium ± market_noise`.
8. **Synthetic data** — This dataset is generated programmatically to simulate realistic Bangalore market conditions. It does not represent actual property listings.
