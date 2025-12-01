
select 
dwh_int_news.id
, dwh_int_news.id_new
, created_at
, dwh_int_candles.time
, dwh_int_news.symbol
, dwh_int_news.name symbol_name
, db_headline.headline 
, db_headline.generated_headline
, json_extract_scalar(replace(sentiment, '''', '"'), '$[0].label') label
, json_extract_scalar(replace(sentiment, '''', '"'), '$[0].score') score
, explanation
, open
, high
, low
, close
, market_closed_verifier
, market_closed_verifier_6h
, market_closed_verifier_12h
, market_closed_verifier_24h
, market_closed_verifier_48h
, CASE WHEN date_diff('minute', dwh_int_candles.time, dwh_int_news.created_at) <= 15 THEN open_for_reference_price ELSE close_for_reference_price END AS reference_price
, CASE WHEN date_diff('minute', dwh_int_candles.time, dwh_int_news.created_at) <= 15 THEN open_6h_after ELSE close_6h_after END AS reference_price_6h_after
, CASE WHEN date_diff('minute', dwh_int_candles.time, dwh_int_news.created_at) <= 15 THEN open_12h_after ELSE close_12h_after END AS reference_price_12h_after
, CASE WHEN date_diff('minute', dwh_int_candles.time, dwh_int_news.created_at) <= 15 THEN open_24h_after ELSE close_24h_after END AS reference_price_24h_after
, CASE WHEN date_diff('minute', dwh_int_candles.time, dwh_int_news.created_at) <= 15 THEN open_48h_after ELSE close_48h_after END AS reference_price_48h_after
, resistance_status
, support_status
, correlation_description
, impact_timing_description

from dwh_int_news
left join db_headline on 1=1 
    and cast(db_headline.id as integer) = cast(dwh_int_news.id as integer)
left join db_sentiment on 1=1 
    and cast(dwh_int_news.id as integer) = cast(db_sentiment.id as integer)
left join dwh_int_candles on 1=1 
    and dwh_int_news.created_at between dwh_int_candles.time and dwh_int_candles.time_after
