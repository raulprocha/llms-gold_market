
with asset_impact as (
    SELECT 
    asset
    , symbol
    , impact_trend
    , correlation_beta
    , timeframe
    , key_drivers
    , source_link
    , CASE
        WHEN cast(correlation_beta AS double) <= -0.75 THEN 'strong negative correlation with gold'
        WHEN cast(correlation_beta AS double) > -0.75 AND cast(correlation_beta AS double) <= -0.4 THEN 'moderate negative correlation with gold'
        WHEN cast(correlation_beta AS double) > -0.4 AND cast(correlation_beta AS double) < 0.4 THEN 'neutral or no clear correlation with gold'
        WHEN cast(correlation_beta AS double) >= 0.4 AND cast(correlation_beta AS double) < 0.75 THEN 'moderate positive correlation with gold'
        WHEN cast(correlation_beta AS double) >= 0.75 THEN 'strong positive correlation with gold'
    END AS correlation_description
    , CASE
        WHEN timeframe IN ('1-4h', '1-6h', '2-6h') THEN 'Impact typically occurs within 1–6 hours (very early)'
        WHEN timeframe IN ('3-12h', '4-12h') THEN 'Impact typically occurs within 6–12 hours (early)'
        WHEN timeframe IN ('6-24h', '8-24h') THEN 'Impact typically occurs within 12–24 hours (mid-term)'
        WHEN timeframe IN ('12-36h', '12-48h') THEN 'Impact typically occurs within 24–48 hours (late)'
        WHEN timeframe = '24-72h' THEN 'Impact typically occurs within 48–72 hours (extended)'
        ELSE 'Impact timing unclear'
    END AS impact_timing_description

    FROM db_asset_impact
    WHERE asset IS NOT NULL
)

, news as (
    SELECT distinct 
    headline
    , target_symbol.symbol
    , db_assets_with_impact.name
    , date_parse(created_at, '%Y-%m-%dT%H:%i:%sZ' ) created_at
    , db_selected_news.id id_new
    , db_assets_with_impact.why_matter
    , row_number() over (partition by 1 order by headline, target_symbol.symbol, db_assets_with_impact.name, content) id
    FROM db_selected_news
    CROSS JOIN UNNEST(CAST(json_parse(REPLACE(symbols, '''', '"')) AS array<varchar>)) AS target_symbol(symbol)
    inner join db_assets_with_impact on 1=1 
        and db_assets_with_impact.symbol = target_symbol.symbol
    order by 1, 2, 3, 4
)

select 
news.headline
, news.symbol
, news.name
, news.created_at
, news.id_new
, news.id
, news.why_matter
, db_asset_explanation.explanation
, asset_impact.correlation_description
, asset_impact.impact_timing_description
from news
left join asset_impact on 1=1 
    and asset_impact.symbol = news.symbol
left join db_asset_explanation on 1=1 
    and news.symbol = db_asset_explanation.symbol
