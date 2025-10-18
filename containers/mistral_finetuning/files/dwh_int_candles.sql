WITH 
-- Creating time grid to help to regularize the database - Important to consider timezones
time_grid AS (
  SELECT ts AS grid_time FROM UNNEST(
    sequence(
      timestamp '2020-01-01 00:00:00',
      timestamp '2020-12-31 23:30:00',
      interval '30' minute
    )
  ) AS t(ts)

  UNION ALL

  SELECT ts AS grid_time FROM UNNEST(
    sequence(
      timestamp '2021-01-01 00:00:00',
      timestamp '2021-12-31 23:30:00',
      interval '30' minute
    )
  ) AS t(ts)

  UNION ALL

  SELECT ts AS grid_time FROM UNNEST(
    sequence(
      timestamp '2022-01-01 00:00:00',
      timestamp '2022-12-31 23:30:00',
      interval '30' minute
    )
  ) AS t(ts)

  UNION ALL

  SELECT ts AS grid_time FROM UNNEST(
    sequence(
      timestamp '2023-01-01 00:00:00',
      timestamp '2023-12-31 23:30:00',
      interval '30' minute
    )
  ) AS t(ts)

  UNION ALL

  SELECT ts AS grid_time FROM UNNEST(
    sequence(
      timestamp '2024-01-01 00:00:00',
      timestamp '2024-12-31 23:30:00',
      interval '30' minute
    )
  ) AS t(ts)

  UNION ALL

  SELECT ts AS grid_time FROM UNNEST(
    sequence(
      timestamp '2025-01-01 00:00:00',
      timestamp '2025-06-26 23:30:00',
      interval '30' minute
    )
  ) AS t(ts)
)

, candles_xauusd as (
  select
  CASE -- Fixing for daylight saving time
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2020-01-01' AND DATE '2020-03-28' THEN date_add('hour', 4, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2020-03-29' AND DATE '2020-10-24' THEN date_add('hour', 3, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2020-10-25' AND DATE '2021-03-27' THEN date_add('hour', 4, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2021-03-28' AND DATE '2021-10-30' THEN date_add('hour', 3, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2021-10-31' AND DATE '2022-03-26' THEN date_add('hour', 4, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2022-03-27' AND DATE '2022-10-30' THEN date_add('hour', 3, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2022-10-31' AND DATE '2023-03-26' THEN date_add('hour', 4, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2023-03-27' AND DATE '2023-10-29' THEN date_add('hour', 3, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2023-10-30' AND DATE '2024-03-30' THEN date_add('hour', 4, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2024-03-31' AND DATE '2024-10-26' THEN date_add('hour', 3, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2024-10-27' AND DATE '2025-03-29' THEN date_add('hour', 4, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
    WHEN date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') BETWEEN DATE '2025-03-30' AND DATE '2025-06-26' THEN date_add('hour', 3, date_parse(time, '%Y-%m-%d %H:%i:%s+00:00'))
  end market_time
  , *
  from db_candles_xauusd
)
, time_to_utc as (
    select 
    time_grid.grid_time as time
    , case 
      when market_time is not null then 'open'
      else 'closed'
    end AS market_closed_verifier
    -- We always want the last value corresponding even when the market is closed

    , first_value(cast(open as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) open
    , last_value(cast(open as double))  IGNORE NULLS OVER (ORDER BY grid_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) open_for_reference_price
    , first_value(cast(high as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) high
    , first_value(cast(low as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) low
    , first_value(cast(close as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) close
    , last_value(cast(close as double))  IGNORE NULLS OVER (ORDER BY grid_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) close_for_reference_price
    , first_value(cast(tick_volume as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) tick_volume
    , first_value(cast(spread as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) spread
    , first_value(cast(real_volume as double))  IGNORE NULLS OVER (ORDER BY grid_time ASC ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) real_volume
    , date(time_grid.grid_time) dt
    from time_grid
    left join candles_xauusd on 1=1 
        and candles_xauusd.market_time = time_grid.grid_time
)

select 
time
, LEAD(time) OVER (ORDER BY time ASC) time_after
, market_closed_verifier
, open
, open_for_reference_price
, LEAD(open, 12) OVER (ORDER BY time ASC) AS open_6h_after
, LEAD(market_closed_verifier, 12) OVER (ORDER BY time ASC) AS market_closed_verifier_6h
, LEAD(open, 24) OVER (ORDER BY time ASC) AS open_12h_after
, LEAD(market_closed_verifier, 24) OVER (ORDER BY time ASC) AS market_closed_verifier_12h
, LEAD(open, 48) OVER (ORDER BY time ASC) AS open_24h_after
, LEAD(market_closed_verifier, 48) OVER (ORDER BY time ASC) AS market_closed_verifier_24h
, LEAD(open, 96) OVER (ORDER BY time ASC) AS open_48h_after
, LEAD(market_closed_verifier, 96) OVER (ORDER BY time ASC) AS market_closed_verifier_48h
, close_for_reference_price
, LEAD(close, 12) OVER (ORDER BY time ASC) AS close_6h_after
, LEAD(close, 24) OVER (ORDER BY time ASC) AS close_12h_after
, LEAD(close, 48) OVER (ORDER BY time ASC) AS close_24h_after
, LEAD(close, 96) OVER (ORDER BY time ASC) AS close_48h_after

, high
, low
, close
, tick_volume
, spread
, real_volume
, dt
-- 30-day highest high (used to detect resistance zones)
, MAX(high) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW) AS highest_high_30d

-- 30-day lowest low (used to detect support zones)
, MIN(low) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW) AS lowest_low_30d

-- Distance from current price to 30-day high, used to describe resistance proximity
, CASE 
  WHEN (MAX(high) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW) - close) / close <= 0.005 THEN 'touching resistance'
  WHEN (MAX(high) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW) - close) / close <= 0.015 THEN 'near resistance'
  WHEN (MAX(high) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW) - close) / close <= 0.03 THEN 'approaching resistance'
  ELSE 'far from resistance'
END AS resistance_status

-- Distance from current price to 30-day low, used to describe support proximity
, CASE 
  WHEN (close - MIN(low) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW)) / close <= 0.005 THEN 'touching support'
  WHEN (close - MIN(low) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW)) / close <= 0.015 THEN 'near support'
  WHEN (close - MIN(low) OVER (ORDER BY time ROWS BETWEEN 1440 PRECEDING AND CURRENT ROW)) / close <= 0.03 THEN 'approaching support'
  ELSE 'far from support'
END AS support_status
from time_to_utc
