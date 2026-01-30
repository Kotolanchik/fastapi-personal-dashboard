with health as (
    select * from read_parquet('{{ var("parquet_path") }}/health/*.parquet')
)

select
    user_id,
    date_trunc('month', recorded_at) as month,
    avg(sleep_hours) as avg_sleep_hours,
    avg(energy_level) as avg_energy_level,
    avg(wellbeing) as avg_wellbeing
from health
group by user_id, month
