from typing import Any

from deepeval.test_case import LLMTestCase

from config import (
    EVAL_MODEL,
    EVAL_VERSION,
)

from metrics import create_metrics


METRICS = create_metrics()


# ============================================================
# HELPERS
# ============================================================

def safe_string(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# DETERMINISTIC CHECKS
# ============================================================

def deterministic_checks(
    incident: dict,
):

    rootcause = safe_string(
        incident.get("rootcause")
    )

    evidence = safe_string(
        incident.get("evidence")
    )

    next_step = safe_string(
        incident.get("next_step")
    )

    confidence = incident.get(
        "confidence"
    )

    received_at = incident.get(
        "received_at"
    )

    completed_at = incident.get(
        "completed_at"
    )


    # --------------------------------------------------------
    # Root cause exists
    # --------------------------------------------------------

    has_rootcause = bool(
        rootcause
    )


    # --------------------------------------------------------
    # Evidence exists
    # --------------------------------------------------------

    has_evidence = bool(
        evidence
    )


    # --------------------------------------------------------
    # Next step exists
    # --------------------------------------------------------

    has_next_step = bool(
        next_step
    )


    # --------------------------------------------------------
    # Confidence valid
    # --------------------------------------------------------

    try:

        if confidence is None:

            confidence_valid = False

        else:

            confidence_value = float(
                confidence
            )

            confidence_valid = (
                0.0
                <= confidence_value
                <= 1.0
            )

            # If your DB stores confidence as 0-100,
            # change this logic accordingly.

    except (
        ValueError,
        TypeError,
    ):

        confidence_valid = False


    # --------------------------------------------------------
    # Timestamp validation
    # --------------------------------------------------------

    timestamps_valid = True


    if (
        received_at is not None
        and completed_at is not None
    ):

        try:

            timestamps_valid = (
                completed_at
                >=
                received_at
            )

        except TypeError:

            timestamps_valid = False


    checks = [

        has_rootcause,

        has_evidence,

        has_next_step,

        confidence_valid,

        timestamps_valid,
    ]


    deterministic_score = (
        sum(checks)
        /
        len(checks)
    )


    return {

        "has_rootcause":
            has_rootcause,

        "has_evidence":
            has_evidence,

        "has_next_step":
            has_next_step,

        "confidence_valid":
            confidence_valid,

        "timestamps_valid":
            timestamps_valid,

        "deterministic_score":
            deterministic_score,
    }


# ============================================================
# BUILD DEEPEVAL TEST CASE
# ============================================================

def build_test_case(
    incident: dict,
):

    incident_input = f"""
INCIDENT INFORMATION

Incident ID:
{safe_string(incident.get("incident_id"))}

Received At:
{safe_string(incident.get("received_at"))}

Alert Name:
{safe_string(incident.get("alert_name"))}

Severity:
{safe_string(incident.get("severity"))}

Cluster:
{safe_string(incident.get("cluster_name"))}

Namespace:
{safe_string(incident.get("namespace"))}

Incident Summary:
{safe_string(incident.get("summary"))}
""".strip()


    actual_output = f"""
AGENT ANALYSIS

Status:
{safe_string(incident.get("status"))}

Confidence:
{safe_string(incident.get("confidence"))}

Root Cause:
{safe_string(incident.get("rootcause"))}

Evidence:
{safe_string(incident.get("evidence"))}

Next Step:
{safe_string(incident.get("next_step"))}
""".strip()


    return LLMTestCase(

        input=incident_input,

        actual_output=actual_output,
    )


# ============================================================
# RUN ONE METRIC
# ============================================================

def run_metric(
    metric,
    test_case,
):

    try:

        metric.measure(
            test_case
        )


        score = metric.score


        reason = getattr(
            metric,
            "reason",
            None,
        )


        return (

            float(score)
            if score is not None
            else None,

            reason,

            None,
        )


    except Exception as exc:

        return (

            None,

            None,

            str(exc),
        )


# ============================================================
# EVALUATE INCIDENT
# ============================================================

def evaluate_incident(
    incident: dict,
):

    test_case = build_test_case(
        incident
    )


    deterministic = (
        deterministic_checks(
            incident
        )
    )


    result = {

        "incident_id":
            str(
                incident["incident_id"]
            ),

        "evaluator_version":
            EVAL_VERSION,

        "evaluator_model":
            EVAL_MODEL,


        "rootcause_score":
            None,

        "rootcause_reason":
            None,


        "evidence_score":
            None,

        "evidence_reason":
            None,


        "next_step_score":
            None,

        "next_step_reason":
            None,


        "completeness_score":
            None,

        "completeness_reason":
            None,


        "overall_score":
            None,


        "final_score":
            None,


        "evaluation_error":
            None,


        **deterministic,
    }


    errors = []


    # ========================================================
    # ROOT CAUSE
    # ========================================================

    (
        score,
        reason,
        error,
    ) = run_metric(
        METRICS["rootcause"],
        test_case,
    )


    result[
        "rootcause_score"
    ] = score

    result[
        "rootcause_reason"
    ] = reason


    if error:

        errors.append(
            f"Root cause: {error}"
        )


    # ========================================================
    # EVIDENCE
    # ========================================================

    (
        score,
        reason,
        error,
    ) = run_metric(
        METRICS["evidence"],
        test_case,
    )


    result[
        "evidence_score"
    ] = score

    result[
        "evidence_reason"
    ] = reason


    if error:

        errors.append(
            f"Evidence: {error}"
        )


    # ========================================================
    # NEXT STEP
    # ========================================================

    (
        score,
        reason,
        error,
    ) = run_metric(
        METRICS["next_step"],
        test_case,
    )


    result[
        "next_step_score"
    ] = score

    result[
        "next_step_reason"
    ] = reason


    if error:

        errors.append(
            f"Next step: {error}"
        )


    # ========================================================
    # COMPLETENESS
    # ========================================================

    (
        score,
        reason,
        error,
    ) = run_metric(
        METRICS["completeness"],
        test_case,
    )


    result[
        "completeness_score"
    ] = score

    result[
        "completeness_reason"
    ] = reason


    if error:

        errors.append(
            f"Completeness: {error}"
        )


    # ========================================================
    # ERROR
    # ========================================================

    if errors:

        result[
            "evaluation_error"
        ] = "\n".join(
            errors
        )


    # ========================================================
    # WEIGHTED SCORE
    # ========================================================

    scores = [

        result["rootcause_score"],

        result["evidence_score"],

        result["next_step_score"],

        result["completeness_score"],
    ]


    weights = [

        0.30,  # RCA

        0.25,  # Evidence

        0.20,  # Next step

        0.25,  # Completeness
    ]


    valid = [

        (
            score,
            weight,
        )

        for score, weight
        in zip(
            scores,
            weights,
        )

        if score is not None
    ]


    if valid:

        result[
            "overall_score"
        ] = (

            sum(
                score * weight
                for score, weight
                in valid
            )

            /

            sum(
                weight
                for _, weight
                in valid
            )
        )


    # ========================================================
    # FINAL SCORE
    # ========================================================

    if (
        result["overall_score"]
        is not None
    ):

        # 90% LLM judge
        # 10% deterministic quality

        result[
            "final_score"
        ] = (

            result["overall_score"]
            * 0.90

            +

            result["deterministic_score"]
            * 0.10
        )


    return result
