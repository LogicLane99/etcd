import argparse
import logging

from datetime import (
    datetime,
    timedelta,
    timezone,
)


from config import (
    EVAL_BATCH_SIZE,
)


from database import (
    get_incidents,
    save_evaluation,
    get_daily_summary,
)


from evaluator import (
    evaluate_incident,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    ),
)


logger = logging.getLogger(
    __name__
)


# ============================================================
# DATE RANGE
# ============================================================

def get_previous_day_range():

    now = datetime.now(
        timezone.utc
    )


    today = datetime(

        year=now.year,

        month=now.month,

        day=now.day,

        tzinfo=timezone.utc,
    )


    yesterday = (
        today
        -
        timedelta(days=1)
    )


    return (
        yesterday,
        today,
    )


# ============================================================
# MAIN
# ============================================================

def run():

    parser = argparse.ArgumentParser()


    parser.add_argument(

        "--date",

        help=(
            "Evaluate a specific UTC date. "
            "Format: YYYY-MM-DD"
        ),
    )


    parser.add_argument(

        "--limit",

        type=int,

        default=None,
    )


    args = parser.parse_args()


    # ========================================================
    # DATE
    # ========================================================

    if args.date:

        target_date = (
            datetime.strptime(
                args.date,
                "%Y-%m-%d",
            )
            .replace(
                tzinfo=timezone.utc
            )
        )


        start_time = target_date


        end_time = (
            target_date
            +
            timedelta(days=1)
        )


    else:

        (
            start_time,
            end_time,
        ) = get_previous_day_range()


    evaluation_date = (
        start_time.date()
    )


    logger.info(
        "=========================================="
    )


    logger.info(
        "Agent evaluation started"
    )


    logger.info(
        "Evaluation date: %s",
        evaluation_date,
    )


    logger.info(
        "Window: %s -> %s",
        start_time,
        end_time,
    )


    logger.info(
        "=========================================="
    )


    # ========================================================
    # LOAD INCIDENTS
    # ========================================================

    limit = (
        args.limit
        if args.limit is not None
        else EVAL_BATCH_SIZE
    )


    incidents = get_incidents(

        start_time=start_time,

        end_time=end_time,

        limit=limit,
    )


    logger.info(
        "Found %d incidents",
        len(incidents),
    )


    if not incidents:

        logger.info(
            "No incidents found."
        )

        return


    # ========================================================
    # EVALUATE
    # ========================================================

    successful = 0

    failed = 0


    for index, incident in enumerate(

        incidents,

        start=1,
    ):

        incident_id = (
            incident["incident_id"]
        )


        logger.info(

            "[%d/%d] Evaluating %s",

            index,

            len(incidents),

            incident_id,
        )


        try:

            result = evaluate_incident(
                incident
            )


            save_evaluation(

                result,

                evaluation_date,
            )


            successful += 1


            final_score = (
                result["final_score"]
            )


            if final_score is not None:

                logger.info(

                    "Incident %s -> %.3f",

                    incident_id,

                    final_score,
                )

            else:

                logger.warning(

                    "Incident %s -> no score",

                    incident_id,
                )


        except Exception as exc:

            failed += 1


            logger.exception(

                "Failed evaluating %s: %s",

                incident_id,

                exc,
            )


    # ========================================================
    # DAILY SUMMARY
    # ========================================================

    summary = get_daily_summary(
        evaluation_date
    )


    logger.info(
        ""
    )

    logger.info(
        "=========================================="
    )

    logger.info(
        "EVALUATION SUMMARY"
    )

    logger.info(
        "=========================================="
    )


    logger.info(
        "Incidents: %s",
        summary["incidents"],
    )


    logger.info(
        "RCA: %.3f",
        summary["avg_rootcause"]
        or 0,
    )


    logger.info(
        "Evidence: %.3f",
        summary["avg_evidence"]
        or 0,
    )


    logger.info(
        "Next step: %.3f",
        summary["avg_next_step"]
        or 0,
    )


    logger.info(
        "Completeness: %.3f",
        summary["avg_completeness"]
        or 0,
    )


    logger.info(
        "Overall: %.3f",
        summary["avg_overall"]
        or 0,
    )


    logger.info(
        "Deterministic: %.3f",
        summary["avg_deterministic"]
        or 0,
    )


    logger.info(
        "FINAL SCORE: %.3f",
        summary["avg_final"]
        or 0,
    )


    logger.info(
        "Low-score incidents: %s",
        summary["low_score_incidents"],
    )


    logger.info(
        "Critical-score incidents: %s",
        summary["critical_score_incidents"],
    )


    logger.info(
        "Successful: %d",
        successful,
    )


    logger.info(
        "Failed: %d",
        failed,
    )


    logger.info(
        "=========================================="
    )


if __name__ == "__main__":

    run()
