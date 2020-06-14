WITH height AS
    (
    SELECT
        chart.subject_id,
        chart.itemid,
        chart.charttime,
        chart.value AS height,
        chart.valueuom,
        height_label.label
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
    )

, weight AS
    (
    SELECT
        ie.subject_id,
        ie.starttime,
        ie.endtime,
        ie.itemid,
        ie.patientweight
    FROM
        mimiciii.inputevents_mv as ie
    )
SELECT
    weight.subject_id,
    weight.starttime,
    weight.endtime,
    weight.patientweight,
FROM weight
UNION ALL
SELECT 
    height.charttime,
    height.label,
    height.height,
    height.valueuom as height_units
FROM height
ORDER BY
    weight.subject_id
LIMIT 100; -- comment this out for the whole table