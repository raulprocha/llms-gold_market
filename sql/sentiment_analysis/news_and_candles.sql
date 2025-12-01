
with news_processed as (
SELECT distinct 
headline
, target_symbol.symbol
, db_assets_with_impact.name
, date_parse(created_at, '%Y-%m-%dT%H:%i:%sZ' ) created_at
, db_selected_news.id new_id
, db_assets_with_impact.why_matter
, row_number() over (partition by 1 order by headline, target_symbol.symbol, db_assets_with_impact.name, content) id
FROM db_selected_news
CROSS JOIN UNNEST(CAST(json_parse(REPLACE(symbols, '''', '"')) AS array<varchar>)) AS target_symbol(symbol)
inner join db_assets_with_impact on 1=1 
    and db_assets_with_impact.symbol = target_symbol.symbol
order by 1, 2, 3, 4
)

, candles_xauusd as (
select 
date_parse(time, '%Y-%m-%d %H:%i:%s+00:00') time
, LEAD(date_parse(time, '%Y-%m-%d %H:%i:%s+00:00')) OVER (ORDER BY time) AS time_after
, cast(open as double) open
, cast(high as double) high
, cast(low as double) low
, cast(close as double) close
, cast(tick_volume as double) tick_volume
, cast(spread as double) spread
, cast(real_volume as double) real_volume
, dt
from db_candles_xauusd 
)

select 
news_processed.id
, created_at
, candles_xauusd.time
, news_processed.symbol
, news_processed.name symbol_name
, db_headline.headline 
, db_headline.generated_headline
, json_extract_scalar(replace(sentiment, '''', '"'), '$[0].label') label
, json_extract_scalar(replace(sentiment, '''', '"'), '$[0].score') score
, open
, high
, low
, close
, CASE 
  WHEN date_diff('minute', candles_xauusd.time, news_processed.created_at) <= 15 
       THEN open
  ELSE close
END AS reference_price
, LEAD(CASE    WHEN date_diff('minute', candles_xauusd.time, news_processed.created_at) <= 15         THEN open   ELSE close END, 12) OVER (ORDER BY candles_xauusd.time ASC) AS reference_price_6h_after
, LEAD(CASE    WHEN date_diff('minute', candles_xauusd.time, news_processed.created_at) <= 15         THEN open   ELSE close END, 24) OVER (ORDER BY candles_xauusd.time ASC) AS reference_price_12h_after
, LEAD(CASE    WHEN date_diff('minute', candles_xauusd.time, news_processed.created_at) <= 15         THEN open   ELSE close END, 48) OVER (ORDER BY candles_xauusd.time ASC) AS reference_price_24h_after
, LEAD(CASE    WHEN date_diff('minute', candles_xauusd.time, news_processed.created_at) <= 15         THEN open   ELSE close END, 96) OVER (ORDER BY candles_xauusd.time ASC) AS reference_price_48h_after

from news_processed
left join db_headline on 1=1 
    and cast(db_headline.id as integer) = cast(news_processed.id as integer)
left join db_sentiment on 1=1 
    and cast(news_processed.id as integer) = cast(db_sentiment.id as integer)
left join candles_xauusd on 1=1 
    and news_processed.created_at between candles_xauusd.time and candles_xauusd.time_after

