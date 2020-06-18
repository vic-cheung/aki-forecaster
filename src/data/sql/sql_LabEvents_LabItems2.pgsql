SELECT  
    le.subject_id,
    le.hadm_id,
    le.itemid,
    le.charttime,
    le.value,
    le.valueuom,
    -- le.flag
    li.label,
    li.fluid,
    li.category,
    li.loinc_code
FROM mimiciii.labevents as le
INNER JOIN mimiciii.d_labitems AS li
    ON li.itemid = le.itemid
WHERE
    (
        lower(li.fluid) = 'blood' AND
        (
            lower(li.label) LIKE '%alkaline%'
            -- lower(li.label) LIKE '%asparate aminotransferase%'
        )
    )
    OR
    (
        lower(li.fluid) = 'urine' AND 
        (
            lower(li.label) LIKE '%wbc%' AND
            lower(li.label) NOT LIKE '%wbc clumps%'
        )
    )
ORDER BY
    le.subject_id ASC,
    le.hadm_id ASC,
    le.charttime ASC
LIMIT 1000
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%potassium%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%sodium%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%chloride%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%bicarbonate%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%creatinine%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%glucose%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%phosphate%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%a1c%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%wbc%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%white blood cells%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%red blood cells%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE 'hemoglobin') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%hematocrit%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%platelet%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%mcv%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%alanine aminotransferase%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%asparate aminotransferase%')
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%bilirubin%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE 'alkaline phosphatase')OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%troponin%')OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%bnp%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%c-reactive protein%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%sedimentation%') OR
        -- (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%neutrophil%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%bacteria%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%blood%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%broad casts%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%cellular cast%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%albumin, urine%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%albumin/creatinine, urine%') OR
        -- (lower(li.fluid) = 'urine'AND lower(li.label) LIKE '%osmolality, urine%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%ph%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%protein/creatinine ratio%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%sodium, urine%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine creatinine%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine volume%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine volume, total%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%granular casts%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%hyaline casts%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%ketone%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%leukocytes%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%nitrite%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%protein%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%rbc%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%rbc casts%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%specific gravity%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine appearance%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine casts, other%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine color%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%wbc%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%wbc casts%') OR
        -- (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%yeast%')
    -- EXCEPT
    --   SELECT
    --     li.itemid,
    --     li.label,
    --     li.fluid,
    --     li.category,
    --     li.loinc_code
    -- FROM
    --     mimiciii.d_labitems AS li
    -- WHERE
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%wbc clumps%') OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%rbc clumps%') OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%24 hr%') OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%porphobilinogen screen%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%crystals%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%prot. electrophoresis%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%eosinophils%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%amorphous%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%amphetamine%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%hyphenated%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%total protein%')  OR
    --     (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%phosphate%')
    -- ) AS labitems
    -- ON 
    -- labitems.itemid = le.itemid
-- ORDER BY
--     le.subject_id,
--     le.charttime
-- LIMIT 1000 --comment this out for the whole table length
