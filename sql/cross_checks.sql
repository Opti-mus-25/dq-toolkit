-- name: visit_before_enrollment
-- category: visit_before_enrollment
-- table: visits
SELECT
    v.visit_id AS record_key,
    'visit_date' AS field,
    v.visit_date AS value,
    'Visit date ' || v.visit_date || ' is before enrollment date ' || p.enrollment_date AS message
FROM visits v
JOIN participants p ON v.participant_id = p.participant_id
WHERE v.visit_date < p.enrollment_date;

-- name: birth_date_mismatch
-- category: cross_db_birth_date_mismatch
-- table: participants
SELECT
    p.participant_id AS record_key,
    'birth_date' AS field,
    p.birth_date AS value,
    'Research database has ' || p.birth_date || ' but clinical database has ' || c.birth_date AS message
FROM participants p
JOIN clinical_participants c ON p.participant_id = c.participant_id
WHERE p.birth_date <> c.birth_date;

-- name: sex_mismatch
-- category: cross_db_sex_mismatch
-- table: participants
SELECT
    p.participant_id AS record_key,
    'sex' AS field,
    p.sex AS value,
    'Research database has ' || p.sex || ' but clinical database has ' || c.sex AS message
FROM participants p
JOIN clinical_participants c ON p.participant_id = c.participant_id
WHERE p.sex IN ('F', 'M')
  AND c.sex IN ('F', 'M')
  AND p.sex <> c.sex;

-- name: missing_in_clinical
-- category: cross_db_missing_participant
-- table: participants
SELECT
    p.participant_id AS record_key,
    'participant_id' AS field,
    p.participant_id AS value,
    'Participant is in the research database but not in the clinical database' AS message
FROM participants p
LEFT JOIN clinical_participants c ON p.participant_id = c.participant_id
WHERE c.participant_id IS NULL;

-- name: extra_in_clinical
-- category: cross_db_extra_participant
-- table: clinical_participants
SELECT
    c.participant_id AS record_key,
    'participant_id' AS field,
    c.participant_id AS value,
    'Participant is in the clinical database but not in the research database' AS message
FROM clinical_participants c
LEFT JOIN participants p ON c.participant_id = p.participant_id
WHERE p.participant_id IS NULL;
