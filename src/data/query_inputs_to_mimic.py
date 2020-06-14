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


def build_query_kidney_events() -> str:
    sql = """
        SELECT
            icd.row_id,
            icd.icd9_code,
            icd.short_title,
            icd.long_title
        FROM
            mimiciii.d_icd_diagnoses as icd
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


def build_query_htwt() -> str:
    sql = """
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
            chart_inputs.subject_id"""
    return dedent(sql)
