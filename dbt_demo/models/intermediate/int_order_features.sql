-- Заказ + его позиции: здесь появляются производные признаки.
select
    o.order_id,
    o.customer_state,
    o.distance_km,
    o.seller_delay_d,
    o.order_value,
    i.n_items,
    i.total_weight_g,
    o.freight_value / nullif(o.order_value, 0) as freight_ratio
from {{ ref('stg_orders') }} as o
join {{ ref('stg_items') }}  as i using (order_id)
