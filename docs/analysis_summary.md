# Analysis Summary

## Dataset overview

The project uses synthetic e-commerce data generated for portfolio practice.

Current dataset:

- users: 500
- sessions: 2,225
- paid orders: 425
- events: 6,752
- revenue: 221,082.40
- average order value: 520.19
- session-to-order conversion: 19.10%

## Monthly dynamics

December 2025 is the strongest month in the dataset:

- revenue: 23,873.00
- paid orders: 48
- session-to-order conversion: 24.49%

July 2025 also shows strong activity:

- active users: 110
- sessions: 205
- paid orders: 46

March 2026 should be interpreted carefully because it is an incomplete month in the generated dataset.

## Funnel analysis

Funnel steps:

1. `view_item`
2. `add_to_cart`
3. `purchase`

Results:

- viewed users: 500
- cart users: 385
- purchase users: 290
- view-to-cart conversion: 77.00%
- cart-to-purchase conversion: 75.32%
- view-to-purchase conversion: 58.00%

Main interpretation:

The largest user loss happens between product view and cart addition.
This may indicate issues with product cards, pricing clarity, product description, reviews, or call-to-action visibility.

## Traffic source analysis

Best traffic source by view-to-purchase conversion:

- telegram: 32.16%

Lowest traffic source by view-to-purchase conversion:

- google: 23.36%

Interpretation:

Telegram shows the highest purchase conversion and may bring warmer traffic.
However, traffic source decisions should also include traffic volume, acquisition cost, margin, and retention.

## Acquisition channel analysis

Top channels by revenue:

- referral: 51,970.96
- social: 51,335.17
- email: 45,207.53

Best channel by user-to-buyer conversion:

- email: 62.37%

Interpretation:

Referral and social bring the highest revenue, while email has the best user-to-buyer conversion.
Email users may be more loyal or better warmed up before purchase.

## Device analysis

Best device type by revenue:

- desktop: 97,783.89

Best device type by session-to-order conversion:

- desktop: 21.12%

Lowest device type by conversion:

- mobile: 15.22%

Interpretation:

Desktop users convert better than mobile users.
The mobile funnel should be investigated further: checkout UX, page speed, payment flow, and product card layout may affect conversion.

## Category analysis

Top categories by revenue:

- Electronics: 80,141.63
- Home: 67,450.40
- Sports: 48,133.28
- Beauty: 32,551.16

Interpretation:

Electronics and Home are the main revenue drivers.
Beauty has the lowest revenue despite a similar number of sold items, which may be explained by lower average item price.

## Product analysis

Top products by revenue:

- Orion Headphones
- Atlas Laptop
- Pulse Chair
- Aero Storage Box
- Aero Phone

Interpretation:

The top products are concentrated mostly in Electronics and Home categories.
These categories should be prioritized in dashboard monitoring and business analysis.

## Next analytical steps

- Add customer acquisition cost data.
- Calculate CAC, LTV, and payback period.
- Add repeat purchase metrics.
- Build a Power BI dashboard.
- Create a Jupyter notebook with EDA and visualizations.
- Add a simple predictive model for purchase probability or churn risk.
