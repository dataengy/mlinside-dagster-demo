-- Позиции заказа, свёрнутые до уровня заказа.
select
    order_id,
    count(*)                        as n_items,
    sum(cast(product_weight_g as double)) as total_weight_g
from {{ source('raw', 'raw_items') }}
group by order_id
