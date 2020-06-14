SELECT
    chart.subject_id,
    chart.charttime,
    chart.value AS height,
    chart.valueuom
FROM
    mimiciii.chartevents as chart
INNER JOIN
    (
    SELECT
        ditems.itemid,
        ditems.label,
        ditems.category,
        ditems.unitname
    FROM
        mimiciii.d_items as ditems
    WHERE
        (lower(ditems.label) LIKE '%admit ht') OR
        (lower(ditems.label) LIKE '%height%')
    EXCEPT
    SELECT
        ditems.itemid,
        ditems.label,
        ditems.category,
        ditems.unitname
    FROM
        mimiciii.d_items as ditems
    WHERE
        (lower(ditems.label) LIKE '%bed%') OR
        (lower(ditems.label) LIKE '%apache%')
    ) AS height_label
    ON height_label.itemid = chart.itemid
ORDER BY
    chart.subject_id
LIMIT 100