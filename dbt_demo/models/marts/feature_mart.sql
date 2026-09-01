-- ВИТРИНА ПРИЗНАКОВ — та самая точка, где dbt отдаёт работу ML-части.
-- Ниже по графу от неё начинается training_dataset.
select
    order_id,
    freight_ratio,
    distance_km,
    n_items,
    seller_delay_d,
    -- целевая переменная: доставка «долгая», если задержка продавца и расстояние выше нормы
    case when seller_delay_d + distance_km / 200.0 > 2.6 then 1 else 0 end as target,
    case when abs(hash(order_id)) % 10 < 8 then 'train' else 'test' end    as split
from {{ ref('int_order_features') }}
where freight_ratio is not null
