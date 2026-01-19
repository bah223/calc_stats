-- ==================================================================
-- WP — 5. Полная аналитика по нескольким мерчантам (МСК)
-- ==================================================================
-- Как добавить мерчанта:
--   1. Узнай его partner_id:
--      SELECT id, name FROM public.db_wp_partners WHERE name ILIKE '%...%';
--   2. Добавь строку в VALUES: (ID, 'Название')
--   3. Готово!
WITH merchants AS (
  SELECT * FROM (VALUES
    (3035, 'PAY365/DonatePay_SBP_API-RUB'),
    (3239, 'PAY365/Mosparking(МТС)-RUB'),
    (3233, 'PAY365/ТК_Центр_Stoloto(МТС)-RUB')
    -- ↑ ДОБАВЛЯЙ СЮДА
  ) AS t(partner_id, merchant_name)
)
SELECT
  m.merchant_name AS "Мерчант",
  m.partner_id AS "ID",
  COUNT(*) AS "Всего",
  COUNT(*) FILTER (WHERE x.status IN ('PAY_OK', 'MANUAL_OK')) AS "Успешных",
  ROUND(
    COUNT(*) FILTER (WHERE x.status IN ('PAY_OK', 'MANUAL_OK')) * 100.0
    / NULLIF(COUNT(*), 0),
    2
  ) AS "Конверсия, %",
  MAX(x.created) AS "Последняя операция"
FROM merchants m
LEFT JOIN public.db_wp_pay_operations x
  ON x.partner_id = m.partner_id
  AND x.created >= '2025-12-27 21:00:00'
  AND x.created < '2025-12-28 21:00:00'
GROUP BY m.partner_id, m.merchant_name
ORDER BY "Всего" DESC;