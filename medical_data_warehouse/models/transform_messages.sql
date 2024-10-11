{{ config(materialized='table') }}

with raw as (
    select *
    from {{ source('public', 'medical_data') }}
)

select
  message_id,
  sender_id,
  lower(message_text) as message_text,  -- Convert message text to lowercase
  channel,
  date
from raw
