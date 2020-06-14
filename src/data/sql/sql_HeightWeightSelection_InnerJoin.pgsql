WITH chart_inputs AS
(SELECT
    chart.subject_id,
    chart.hadm_id,
    chart.charttime,
    chart.value,
    chart.valueuom,
    chart.warning,
    inputs.starttime,
    inputs.endtime,
    inputs.itemid,
    inputs.amount,
    inputs.amountuom,
    inputs.rate,
    inputs.rateuom,
    inputs.storetime,
    inputs.ordercategoryname,
    inputs.ordercategorydescription,
    inputs.secondaryordercategoryname,
    inputs.ordercomponenttypedescription
FROM
    mimiciii.chartevents as chart
LEFT JOIN
    (SELECT
        ie.subject_id,
        ie.starttime,
        ie.endtime,
        ie.itemid, 
        ie.amount,
        ie.amountuom,
        ie.rate,
        ie.rateuom,
        ie.storetime,
        ie.ordercategoryname,
        ie.ordercategorydescription,
        ie.secondaryordercategoryname,
        ie.ordercomponenttypedescription
    FROM
        mimiciii.inputevents_mv as ie
    ) AS inputs
    ON inputs.subject_id = chart.subject_id
ORDER BY chart.subject_id)
, hw AS
(SELECT 
        ditems.itemid,
        ditems.label,
        ditems.category,
        ditems.unitname,
        ditems.param_type,
        ditems.conceptid
    FROM 
        mimiciii.d_items as ditems
    WHERE
        (lower(ditems.label) LIKE '%ht%') OR
        (lower(ditems.label) LIKE '%height%')
    EXCEPT
    SELECT
        ditems.itemid,
        ditems.label,
        ditems.category,
        ditems.unitname,
        ditems.param_type,
        ditems.conceptid
    FROM 
        mimiciii.d_items as ditems
    WHERE
        (lower(ditems.label) LIKE '%pulse%') OR
        (lower(ditems.label) LIKE '%groin%') OR
        (lower(ditems.label) LIKE '%right%') OR
        (lower(ditems.label) LIKE '%light%') OR
        (lower(ditems.label) LIKE '%midnight%') OR
        (lower(ditems.label) LIKE '%straight%') OR
        (lower(ditems.label) LIKE '%apache%') OR
        (lower(ditems.label) LIKE '%might%') OR
        (lower(ditems.label) LIKE '%diphtheroids%') OR
        (lower(ditems.label) LIKE '%chucks%') OR
        (lower(ditems.label) LIKE '%ideal%') OR
        (lower(ditems.label) LIKE '%bed%') OR
        (lower(ditems.label) LIKE '%chtube%') OR
        (lower(ditems.label) LIKE '%unintentional%') OR
        (lower(ditems.label) LIKE '%status%') OR
        (lower(ditems.label) LIKE '%feeding%')
)
SELECT
    chart_inputs.subject_id,
    chart_inputs.hadm_id,
    chart_inputs.charttime,
    chart_inputs.value,
    chart_inputs.valueuom,
    chart_inputs.warning,
    chart_inputs.hadm_id,
    chart_inputs.starttime,
    chart_inputs.endtime,
    chart_inputs.itemid,
    hw.itemid,
    hw.label,
    hw.category,
    hw.unitname,
    hw.param_type,
    hw.conceptid,
    chart_inputs.amount,
    chart_inputs.amountuom,
    chart_inputs.rate,
    chart_inputs.rateuom,
    chart_inputs.storetime,
    chart_inputs.ordercategoryname,
    chart_inputs.ordercategorydescription,
    chart_inputs.secondaryordercategoryname,
    chart_inputs.ordercomponenttypedescription
FROM chart_inputs
INNER JOIN hw
    ON hw.itemid = chart_inputs.itemid
ORDER BY
    chart_inputs.subject_id
LIMIT 100; --comment this out to select the whole table