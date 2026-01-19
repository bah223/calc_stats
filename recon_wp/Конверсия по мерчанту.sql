-- ==================================================================
-- WP — 2. Конверсия по мерчанту (МСК)
-- ==================================================================
-- Конверсия = (успешные / всего) * 100%
-- Успешные статусы: 'PAY_OK', 'MANUAL_OK'
-- Если операций нет — конверсия = NULL (без деления на ноль)
SELECT
  COUNT(*) AS total_transactions,
  COUNT(*) FILTER (WHERE status IN ('PAY_OK', 'MANUAL_OK')) AS success_transactions,
  ROUND(
    COUNT(*) FILTER (WHERE status IN ('PAY_OK', 'MANUAL_OK')) * 100.0
    / NULLIF(COUNT(*), 0),
    2
  ) AS conversion_percent
FROM public.db_wp_pay_operations
WHERE partner_id = 3035
  AND created >= '2025-12-27 21:00:00'
  AND created < '2025-12-28 21:00:00';