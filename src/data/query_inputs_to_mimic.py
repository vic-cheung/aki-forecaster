from textwrap import dedent


def build_query_lab_events(
    blood_lab_labels_list: list = None, urine_lab_labels_list: list = None
) -> str:
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
            "sodium, urine",
        ]
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


def build_query_lab_items_id() -> str:
    sql = """
    SELECT
        li.itemid,
        li.label,
        li.fluid,
        li.category,
        li.loinc_code
    FROM
        mimiciii.d_labitems AS li
    WHERE
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%potassium%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%sodium%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%chloride%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%bicarbonate%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%creatinine%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%glucose%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%phosphate%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%a1c%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%wbc%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%white blood cells%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%red blood cells%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE 'hemoglobin') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%hematocrit%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%platelet%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%mcv%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%alanine aminotransferase%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%asparate aminotransferase%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%bilirubin%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE 'alkaline phosphatase')OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%troponin%')OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%bnp%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%c-reactive protein%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%sedimentation%') OR
        (lower(li.fluid) = 'blood' AND lower(li.label) LIKE '%neutrophil%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%bacteria%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%blood%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%broad casts%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%cellular cast%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%albumin, urine%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%albumin/creatinine, urine%') OR
        (lower(li.fluid) = 'urine'AND lower(li.label) LIKE '%osmolality, urine%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%ph%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%protein/creatinine ratio%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%sodium, urine%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine creatinine%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine volume%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine volume, total%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%granular casts%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%hyaline casts%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%ketone%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%leukocytes%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%nitrite%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%protein%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%rbc%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%rbc casts%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%specific gravity%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine appearance%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine casts, other%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%urine color%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%wbc%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%wbc casts%') OR
        (lower(li.fluid) = 'urine' AND lower(li.label) LIKE '%yeast%')
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
    """
    return dedent(sql)


def build_query_kidney_events() -> str:
    sql = """
        SELECT
            diag.subject_id,
            diag.hadm_id,
            diag.icd9_code
        FROM
            mimiciii.diagnoses_icd as diag
        INNER JOIN mimiciii.d_icd_diagnoses as icd
            ON icd.icd9_code = diag.icd9_code
        WHERE
            (lower(icd.short_title) LIKE '%kidney%') OR
            (lower(icd.short_title) LIKE 'renal%')
        """
    return dedent(sql)


def build_query_adm() -> str:
    sql = """
        SELECT
            adm.subject_id,
            adm.admittime,
            adm.dischtime,
            adm.admission_type,
            adm.ethnicity,
            p.gender,
            p.dob,
            p.dod,
            adm.diagnosis,
            adm.hospital_expire_flag
        FROM
            mimiciii.admissions AS adm
        LEFT JOIN mimiciii.patients AS p
            ON p.subject_id = adm.subject_id
        ORDER BY
            adm.subject_id
        """
    return dedent(sql)


def build_query_height() -> str:
    sql = """
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
    """
    return dedent(sql)


def build_query_weight() -> str:
    sql = """
    SELECT
        ie.subject_id,
        ie.starttime,
        ie.endtime,
        ie.patientweight
    FROM
        mimiciii.inputevents_mv as ie
    ORDER BY
        ie.subject_id
    """
    return dedent(sql)
