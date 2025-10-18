select 
id
, created_at
, time
, symbol
, symbol_name
, headline
, generated_headline
, label
, score
, CASE
  WHEN label = 'Positive' AND CAST(score AS DOUBLE) < 0.7 THEN 'positive - weakly correlated'
  WHEN label = 'Positive' AND CAST(score AS DOUBLE) < 0.9 THEN 'positive - moderately correlated'
  WHEN label = 'Positive' AND CAST(score AS DOUBLE) <= 1.0 THEN 'positive - strongly correlated'

  WHEN label = 'Neutral' AND CAST(score AS DOUBLE) < 0.8 THEN 'neutral - weakly correlated'
  WHEN label = 'Neutral' AND CAST(score AS DOUBLE) < 0.95 THEN 'neutral - moderately correlated'
  WHEN label = 'Neutral' AND CAST(score AS DOUBLE) <= 1.0 THEN 'neutral - strongly correlated'

  WHEN label = 'Negative' AND CAST(score AS DOUBLE) < 0.7 THEN 'negative - weakly correlated'
  WHEN label = 'Negative' AND CAST(score AS DOUBLE) < 0.9 THEN 'negative - moderately correlated'
  WHEN label = 'Negative' AND CAST(score AS DOUBLE) <= 1.0 THEN 'negative - strongly correlated'

  ELSE 'unknown'
END AS sentiment_strength
, open
, high
, low
, close
, reference_price
, reference_price_6h_after
, CASE 
  WHEN reference_price_6h_after > reference_price THEN 'Up'
  WHEN reference_price_6h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_6h
, LEAST(
      FLOOR( ABS(
        (reference_price_6h_after - reference_price)
        / reference_price * 100.0
      ) / 0.75 ),
      5
    ) AS magnitude_6h
, reference_price_12h_after
, CASE 
  WHEN reference_price_12h_after > reference_price THEN 'Up'
  WHEN reference_price_12h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_12h
, LEAST(
      FLOOR( ABS(
        (reference_price_12h_after - reference_price)
        / reference_price * 100.0
      ) / 1.0 ),
      5
    ) AS magnitude_12h
, reference_price_24h_after
, CASE 
  WHEN reference_price_24h_after > reference_price THEN 'Up'
  WHEN reference_price_24h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_24h
, LEAST(
      FLOOR( ABS(
        (reference_price_24h_after - reference_price)
        / reference_price * 100.0
      ) / 1.5 ),
      5
    ) AS magnitude_24h
, reference_price_48h_after
, CASE 
  WHEN reference_price_48h_after > reference_price THEN 'Up'
  WHEN reference_price_48h_after < reference_price THEN 'Down'
  ELSE 'Neutral'
END AS direction_48h
, LEAST(
      FLOOR( ABS(
        (reference_price_48h_after - reference_price)
        / reference_price * 100.0
      ) / 2.0 ),
      5
    ) AS magnitude_48h
from dwh_int_news_and_candles
