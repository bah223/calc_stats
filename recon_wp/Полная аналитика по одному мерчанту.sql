-- ==================================================================
-- WP — 4. Полная аналитика по одному мерчанту (МСК)
-- ==================================================================
-- Всё в одном запросе: количество, конверсия, последняя операция.
-- Легко копировать и менять partner_id + дату.
SELECT
  3035 AS partner_id,
  'PAY365/DonatePay_SBP_API-RUB' AS merchant_name,
  COUNT(*) AS total_transactions,
  COUNT(*) FILTER (WHERE status IN ('PAY_OK', 'MANUAL_OK')) AS success_transactions,
  ROUND(
    COUNT(*) FILTER (WHERE status IN ('PAY_OK', 'MANUAL_OK')) * 100.0
    / NULLIF(COUNT(*), 0),
    2
  ) AS conversion_percent,
  MAX(created) AS last_operation_time
FROM public.db_wp_pay_operations
WHERE partner_id = 3035
  AND created >= '2025-12-27 21:00:00'
  AND created < '2025-12-28 21:00:00';