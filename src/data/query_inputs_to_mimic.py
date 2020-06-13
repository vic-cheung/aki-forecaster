#%%
from textwrap import dedent


# %%
def build_query_lab_events(blood_lab_labels_list: list = None, urine_lab_labels_list: list = None) -> str:
    blood_lab_labels = (
        blood_lab_labels_list
        if blood_lab_labels_list
        else [
            "potassium",
            "sodium",
            "chloride",
            "bicarbonate",
            "creatinine",
            "glucose",
            "phosphate",
            "a1c",
            "white blood cells",
            "red blood cells",
            "hemoglobin",
            "hematocrit",
            "platelet",
            "mcv",
            "alanine aminotransferase",
            "aspartate aminotransferase",
            "bilirubin",
            "alkaline, phosphatase",
            "troponin",
            "bnp",
            "c-reactive protein",
            "sedimentation",
            "neutrophil",
        ]
    )

    urine_lab_labels = (
        urine_lab_labels_list
        if urine_lab_labels_list
        else [
            "yeast", 
            "urine appearance", 
            "urine creatinine", 
            "ketone", 
            "urine volume", 
            "osmolality, urine", 
            "bacteria", 
            "protein/creatinine ratio", 
            "nitrite",
            "rbc", 
            "cellular cast", 
            "wbc casts",
            "leukocytes",
            "albumin, urine", 
            "specific gravity", 
            "rbc casts", 
            "ph", 
            "protein", 
            "hyaline casts", 
            "albumin/creatinine, urine", 
            "broad casts", 
            "urine casts, other", 
            "wbc",
            "blood", 
            "granular casts", 
            "urine volume, total", 
            "urine color", 
            "sodium, urine"]
    )

    blood_lab_labels_str = [
        f"(lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%{x}%')"
        for x in blood_lab_labels
    ]
    blood_lab_labels_where = " OR\n".join(blood_lab_labels_str)
    urine_lab_labels_str = [
        f"(lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%{x}%')"
        for x in urine_lab_labels
    ]
    urine_lab_labels_where = " OR\n".join(urine_lab_labels_str)


    sql = f"""
    SELECT  
        le.subject_id,
        le.itemid AS labevents_itemid,
        le.charttime,
        labitems.label, 
        labitems.fluid,
        labitems.category,
        labitems.loinc_code,
        le.value AS labevents_value,
        le.valueuom,
        le.flag
    FROM mimiciii.labevents as le
    INNER JOIN
        (SELECT
            li.itemid,
            li.label,
            li.fluid,
            li.category,
            li.loinc_code
        FROM
            mimiciii.d_labitems AS li
        WHERE
            {blood_lab_labels_where} OR 
            {urine_lab_labels_where}
        EXCEPT
        SELECT
            li.itemid,
            li.label,
            li.fluid,
            li.category,
            li.loinc_code
        FROM
            mimiciii.d_labitems AS li
        WHERE
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%wbc clumps%') OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%rbc clumps%') OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%24 hr%') OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%porphobilinogen screen%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%crystals%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%prot. electrophoresis%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%eosinophils%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%amorphous%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%amphetamine%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%hyphenated%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%total protein%')  OR
            (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%phosphate%')
        ) AS labitems
    ON labitems.itemid = le.itemid
    ORDER BY
        le.subject_id,
        le.charttime
    """
    return dedent(sql)


#%%


def build_query_kidney_events() -> str:
        sql = f"""
        SELECT
            diagnosis.subject_id,
            diagnosis.hadm_id AS diagnosis_hadm_id,
            diagnosis.seq_num,
            diagnosis.icd9_code,
            diag.short_title,
            diag.long_title
        FROM
            mimiciii.diagnoses_icd AS diagnosis
        LEFT JOIN
            mimiciii.d_icd_diagnoses AS diag
            ON diag.icd9_code = diagnosis.icd9_code
        """
    return dedent(sql)


# %%
