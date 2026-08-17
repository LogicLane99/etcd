from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from config import DATABASE_URL


# ============================================================
# CONNECTION
# ============================================================

def get_connection():

    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )


# ============================================================
# GET INCIDENTS
# ============================================================

def get_incidents(
    start_time: datetime,
    end_time: datetime,
    limit: int | None = None,
):

    query = """
        SELECT

            "incident id" AS incident_id,

            "received at" AS received_at,

            "alert name" AS alert_name,

            "severaity" AS severity,

            "clustername" AS cluster_name,

            "namespace" AS namespace,

            "status" AS status,

            "summary" AS summary,

            "confidence" AS confidence,

            "rootcause" AS rootcause,

            "completed at" AS completed_at,

            "Evidence" AS evidence,

            "Next step" AS next_step

        FROM incidents

        WHERE "received at" >= %s

          AND "received at" < %s

        ORDER BY "received at" ASC
    """

    params = [
        start_time,
        end_time,
    ]


    if limit is not None:

        query += """
            LIMIT %s
        """

        params.append(limit)


    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                query,
                params,
            )

            return cursor.fetchall()


# ============================================================
# SAVE EVALUATION
# ============================================================

def save_evaluation(
    result: dict[str, Any],
    evaluation_date,
):

    query = """
        INSERT INTO agent_evaluations (

            incident_id,

            evaluation_date,

            evaluated_at,

            evaluator_version,

            evaluator_model,


            rootcause_score,

            evidence_score,

            next_step_score,

            completeness_score,

            overall_score,


            has_rootcause,

            has_evidence,

            has_next_step,

            confidence_valid,

            timestamps_valid,

            deterministic_score,


            final_score,


            rootcause_reason,

            evidence_reason,

            next_step_reason,

            completeness_reason,


            evaluation_error

        )

        VALUES (

            %s,

            %s,

            NOW(),

            %s,

            %s,


            %s,

            %s,

            %s,

            %s,

            %s,


            %s,

            %s,

            %s,

            %s,

            %s,

            %s,


            %s,


            %s,

            %s,

            %s,

            %s,


            %s
        )


        ON CONFLICT (
            incident_id,
            evaluator_version
        )

        DO UPDATE SET

            evaluation_date =
                EXCLUDED.evaluation_date,

            evaluated_at =
                NOW(),

            evaluator_model =
                EXCLUDED.evaluator_model,


            rootcause_score =
                EXCLUDED.rootcause_score,

            evidence_score =
                EXCLUDED.evidence_score,

            next_step_score =
                EXCLUDED.next_step_score,

            completeness_score =
                EXCLUDED.completeness_score,

            overall_score =
                EXCLUDED.overall_score,


            has_rootcause =
                EXCLUDED.has_rootcause,

            has_evidence =
                EXCLUDED.has_evidence,

            has_next_step =
                EXCLUDED.has_next_step,

            confidence_valid =
                EXCLUDED.confidence_valid,

            timestamps_valid =
                EXCLUDED.timestamps_valid,

            deterministic_score =
                EXCLUDED.deterministic_score,


            final_score =
                EXCLUDED.final_score,


            rootcause_reason =
                EXCLUDED.rootcause_reason,

            evidence_reason =
                EXCLUDED.evidence_reason,

            next_step_reason =
                EXCLUDED.next_step_reason,

            completeness_reason =
                EXCLUDED.completeness_reason,


            evaluation_error =
                EXCLUDED.evaluation_error
    """


    values = (

        result["incident_id"],

        evaluation_date,

        result["evaluator_version"],

        result["evaluator_model"],


        result["rootcause_score"],

        result["evidence_score"],

        result["next_step_score"],

        result["completeness_score"],

        result["overall_score"],


        result["has_rootcause"],

        result["has_evidence"],

        result["has_next_step"],

        result["confidence_valid"],

        result["timestamps_valid"],

        result["deterministic_score"],


        result["final_score"],


        result["rootcause_reason"],

        result["evidence_reason"],

        result["next_step_reason"],

        result["completeness_reason"],


        result["evaluation_error"],
    )


    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                query,
                values,
            )

        conn.commit()


# ============================================================
# DAILY SUMMARY
# ============================================================

def get_daily_summary(
    evaluation_date,
):

    query = """

        SELECT

            COUNT(*) AS incidents,


            ROUND(
                AVG(rootcause_score)::numeric,
                4
            ) AS avg_rootcause,


            ROUND(
                AVG(evidence_score)::numeric,
                4
            ) AS avg_evidence,


            ROUND(
                AVG(next_step_score)::numeric,
                4
            ) AS avg_next_step,


            ROUND(
                AVG(completeness_score)::numeric,
                4
            ) AS avg_completeness,


            ROUND(
                AVG(overall_score)::numeric,
                4
            ) AS avg_overall,


            ROUND(
                AVG(deterministic_score)::numeric,
                4
            ) AS avg_deterministic,


            ROUND(
                AVG(final_score)::numeric,
                4
            ) AS avg_final,


            COUNT(*) FILTER (
                WHERE final_score < 0.70
            ) AS low_score_incidents,


            COUNT(*) FILTER (
                WHERE final_score < 0.50
            ) AS critical_score_incidents


        FROM agent_evaluations

        WHERE evaluation_date = %s
    """


    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                query,
                (evaluation_date,),
            )

            return cursor.fetchone()
