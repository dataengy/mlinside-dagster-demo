-- Приведение сырых заказов к рабочим типам и именам.
select
    order_id,
    customer_state,
    cast(distance_km as double)    as distance_km,
    cast(seller_delay_d as integer) as seller_delay_d,
    cast(freight_value as double)  as freight_value,
    cast(order_value as double)    as order_value
from {{ source('raw', 'raw_orders') }}
