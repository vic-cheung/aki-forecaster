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
    inputs.patientweight
FROM
    mimiciii.chartevents as chart
LEFT JOIN
    (SELECT
        ie.subject_id,
        ie.starttime,
        ie.endtime,
        ie.itemid,
        ie.patientweight
    FROM
        mimiciii.inputevents_mv as ie
    ) AS inputs
    ON inputs.subject_id = chart.subject_id
ORDER BY chart.subject_id)
, hw AS
(
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
        (lower(ditems.label) LIKE '%admit ht') OR
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
        (lower(ditems.label) LIKE '%bed%') OR
        (lower(ditems.label) LIKE '%apache%')
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
    chart_inputs.patientweight
FROM chart_inputs
INNER JOIN hw
    ON hw.itemid = chart_inputs.itemid
ORDER BY
    chart_inputs.subject_id
LIMIT 100; --comment this out to select the whole table