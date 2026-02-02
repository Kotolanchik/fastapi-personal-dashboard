with finance as (
    select * from read_parquet('{{ var("parquet_path") }}/finance/*.parquet')
)

select
    user_id,
    date_trunc('month', recorded_at) as month,
    sum(income) as total_income,
    sum(expense_food + expense_transport + expense_health + expense_other) as total_expense
from finance
group by user_id, month
