SELECT distinct 
headline
, target_symbol.symbol
, assets_with_impact.name
, date_parse(created_at, '%Y-%m-%dT%H:%i:%sZ' ) created_at
, selected_news.id
, headline
, assets_with_impact.why_matter
, row_number() over (partition by 1 order by headline, target_symbol.symbol, assets_with_impact.name, content) id
FROM selected_news
CROSS JOIN UNNEST(CAST(json_parse(REPLACE(symbols, '''', '"')) AS array<varchar>)) AS target_symbol(symbol)
inner join assets_with_impact on 1=1 
    and assets_with_impact.symbol = target_symbol.symbol
order by 1, 2, 3, 4