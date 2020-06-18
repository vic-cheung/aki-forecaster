from textwrap import dedent


def build_query_lab_events(
    blood_labels_list: list = None, urine_labels_list: list = None, limit: int = None
) -> str:
    blood_labels = (
        blood_labels_list
        if blood_labels_list
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
            "wbc",
            "rbc",
            "red blood cells",
            "hemoglobin",
            "hematocrit",
            "platelet",
            "mcv",
            "aminotransferase",
            "(alt)",
            "(ast)",
            "bilirubin",
            "alkaline phosphatase",
            "troponin",
            "bnp",
            "c-reactive protein",
            "sedimentation",
            "neutrophil",
        ]
    )
    blood_str = " OR\n".join([f"lower(li.label) LIKE '%{x}%'" for x in blood_labels])
    urine_labels = (
        urine_labels_list
        if urine_labels_list
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
    urine_str = " OR\n".join([f"lower(li.label) LIKE '%{x}%'" for x in urine_labels])
    urine_labels_except = [
        "wbc clumps",
        "rbc clumps",
        "24 hr",
        "porphobilinogen screen",
        "crystals",
        "prot. electrophoresis",
        "eosinophils",
        "amorphous",
        "amphetamine",
        "hyphenated",
        "total protein",
        "phosphate",
    ]
    urine_except_str = " AND\n".join(
        [f"lower(li.label) NOT LIKE '%{x}%'" for x in urine_labels_except]
    )
    sql = f"""
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
                lower(li.fluid) = 'blood' AND ({blood_str})
            )
            OR
            (
                lower(li.fluid) = 'urine' AND 
                (
                    ({urine_str}) AND ({urine_except_str})
                )
            )
        ORDER BY
            le.subject_id ASC,
            le.hadm_id ASC,
            le.charttime ASC
    """
    if limit:
        sql += f"\nLIMIT {limit}"
    return dedent(sql)


def build_query_lab_items_id(
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
        ORDER BY
            diag.hadm_id
        """
    return dedent(sql)


def build_query_adm() -> str:
    sql = """
        SELECT
            adm.hadm_id,
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
            adm.hadm_id
        """
    return dedent(sql)


def build_query_height() -> str:
    sql = """
    SELECT
        chart.hadm_id,
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
        chart.hadm_id
    """
    return dedent(sql)


def build_query_weight() -> str:
    sql = """
    SELECT
        ie.hadm_id,
        ie.starttime,
        ie.endtime,
        ie.patientweight
    FROM
        mimiciii.inputevents_mv as ie
    ORDER BY
        ie.hadm_id
    """
    return dedent(sql)
