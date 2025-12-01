with percentil_calculator as (
  SELECT 
  id_new
  , NTILE(4) OVER (ORDER BY magnitude_pips_6h) magnitude_percentil_6h
  , magnitude_pips_6h
  , NTILE(4) OVER (ORDER BY magnitude_pips_12h) magnitude_percentil_12h
  , magnitude_pips_12h
  , NTILE(4) OVER (ORDER BY magnitude_pips_24h) magnitude_percentil_24h
  , magnitude_pips_24h
  , NTILE(4) OVER (ORDER BY magnitude_pips_48h) magnitude_percentil_48h
  , magnitude_pips_48h
  FROM( 
    SELECT DISTINCT 
    id_new
    , ABS(reference_price_6h_after - reference_price ) /0.01 AS magnitude_pips_6h
    , ABS(reference_price_12h_after - reference_price ) /0.01 AS magnitude_pips_12h
    , ABS(reference_price_24h_after - reference_price ) /0.01 AS magnitude_pips_24h
    , ABS(reference_price_48h_after - reference_price ) /0.01 AS magnitude_pips_48h
    FROM dwh_int_news_and_candles
    )
)


select 
id
, dwh_int_news_and_candles.id_new
, created_at
, time
, symbol
, symbol_name
, headline
, generated_headline
, label
, score
, CASE
  WHEN label = 'Positive' AND CAST(score AS DOUBLE) < 0.7 THEN 'weakly positive'
  WHEN label = 'Positive' AND CAST(score AS DOUBLE) < 0.9 THEN 'moderately positive'
  WHEN label = 'Positive' AND CAST(score AS DOUBLE) <= 1.0 THEN 'strongly positive'
  WHEN label = 'Neutral' AND CAST(score AS DOUBLE) < 0.8 THEN 'weakly neutral'
  WHEN label = 'Neutral' AND CAST(score AS DOUBLE) < 0.95 THEN 'moderately neutral'
  WHEN label = 'Neutral' AND CAST(score AS DOUBLE) <= 1.0 THEN 'strongly neutral'
  WHEN label = 'Negative' AND CAST(score AS DOUBLE) < 0.7 THEN 'weakly negative'
  WHEN label = 'Negative' AND CAST(score AS DOUBLE) < 0.9 THEN 'moderately negative'
  WHEN label = 'Negative' AND CAST(score AS DOUBLE) <= 1.0 THEN 'strongly negative'
  ELSE 'unknown'
END AS sentiment_strength
, open
, high
, low
, close
, reference_price
, market_closed_verifier
, market_closed_verifier_6h
, market_closed_verifier_12h
, market_closed_verifier_24h
, market_closed_verifier_48h
, reference_price_6h_after
, CASE 
  WHEN reference_price_6h_after > reference_price THEN 'Up'
  WHEN reference_price_6h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_6h
, magnitude_pips_6h
, CASE magnitude_percentil_6h
  WHEN 1 THEN 'low impact'
  WHEN 2 THEN 'medium-low impact'
  WHEN 3 THEN 'medium-high impact'
  WHEN 4 THEN 'high impact'
END AS magnitude_6h
, reference_price_12h_after
, CASE 
  WHEN reference_price_12h_after > reference_price THEN 'Up'
  WHEN reference_price_12h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_12h
, magnitude_pips_12h
, CASE magnitude_percentil_12h
  WHEN 1 THEN 'low impact'
  WHEN 2 THEN 'medium-low impact'
  WHEN 3 THEN 'medium-high impact'
  WHEN 4 THEN 'high impact'
END AS magnitude_12h
, reference_price_24h_after
, CASE 
  WHEN reference_price_24h_after > reference_price THEN 'Up'
  WHEN reference_price_24h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_24h
, magnitude_pips_24h
, CASE magnitude_percentil_24h
  WHEN 1 THEN 'low impact'
  WHEN 2 THEN 'medium-low impact'
  WHEN 3 THEN 'medium-high impact'
  WHEN 4 THEN 'high impact'
END AS magnitude_24h
, reference_price_48h_after
, CASE 
  WHEN reference_price_48h_after > reference_price THEN 'Up'
  WHEN reference_price_48h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_48h
, magnitude_pips_48h
, CASE magnitude_percentil_48h
  WHEN 1 THEN 'low impact'
  WHEN 2 THEN 'medium-low impact'
  WHEN 3 THEN 'medium-high impact'
  WHEN 4 THEN 'high impact'
END AS magnitude_48h
--, resistance_status
--, support_status
, correlation_description
, impact_timing_description
, explanation
from dwh_int_news_and_candles
LEFT JOIN  percentil_calculator ON 1=1 
  AND percentil_calculator.id_new = dwh_int_news_and_candles.id_new
 -- =MIN(FLOOR(ABS(Q2 - P2) / 0,5); 5) sheets calculation for magnitude
WHERE 
  generated_headline IS NOT NULL AND
  explanation IS NOT NULL AND
  correlation_description IS NOT NULL AND
  impact_timing_description IS NOT NULL AND
  symbol IS NOT NULL AND
  symbol_name IS NOT NULL AND
  sentiment_strength IS NOT NULL AND
  label IS NOT NULL AND
  market_closed_verifier IS NOT NULL AND
  market_closed_verifier_6h IS NOT NULL AND
  market_closed_verifier_12h IS NOT NULL AND
  market_closed_verifier_24h IS NOT NULL AND
  market_closed_verifier_48h IS NOT NULL AND
  direction_6h IS NOT NULL AND magnitude_6h IS NOT NULL AND
  direction_12h IS NOT NULL AND magnitude_12h IS NOT NULL AND
  direction_24h IS NOT NULL AND magnitude_24h IS NOT NULL AND
  direction_48h IS NOT NULL AND magnitude_48h IS NOT NULL