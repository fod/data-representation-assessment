SELECT
    a.date,
    b.name,
    a.quantity,
    round((b.calories * (a.quantity / 100)), 0) calories,
    round((b.protein * (a.quantity / 100)), 0) protein,
    round((b.carbs * (a.quantity / 100)), 0) carbs,
    round((b.fat * (a.quantity / 100)), 0) fat
FROM
    food_log a
    JOIN food_items b ON a.food_id = b.id
WHERE
    a.user_id = 1
ORDER BY
    a.date DESC;