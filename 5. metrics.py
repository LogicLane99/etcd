from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

from llm_model import create_judge_model


JUDGE_MODEL = create_judge_model()


def create_metrics():

    # ========================================================
    # 1. ROOT CAUSE QUALITY
    # ========================================================

    rootcause_metric = GEval(

        name="Root Cause Quality",

        criteria="""
Evaluate the quality of the incident root cause analysis.

The proposed root cause should:

1. Directly address the alert and incident summary.
2. Be technically plausible.
3. Be specific rather than vague.
4. Explain WHY the incident occurred.
5. Be logically consistent with the available information.
6. Avoid unsupported claims.
7. Distinguish between a confirmed root cause and a hypothesis
   when the evidence is insufficient.

A score of 1.0 means the root cause is highly specific,
technically plausible, well supported and clearly explains
why the incident happened.

A score of 0.0 means the root cause is irrelevant, clearly
incorrect, extremely vague, or unsupported.
""",

        evaluation_steps=[
            "Read the alert information.",
            "Read the incident summary.",
            "Read the proposed root cause.",
            "Determine whether the root cause explains the incident.",
            "Determine whether the root cause is specific.",
            "Check for unsupported assumptions.",
            "Check whether uncertainty is handled appropriately.",
            "Assign a score from 0 to 1.",
            "Explain the main reasons for the score.",
        ],

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.70,

        model=JUDGE_MODEL,

        include_reason=True,
    )


    # ========================================================
    # 2. EVIDENCE QUALITY
    # ========================================================

    evidence_metric = GEval(

        name="Evidence Quality",

        criteria="""
Evaluate whether the evidence actually supports the proposed
root cause.

Good evidence should:

1. Be directly relevant to the incident.
2. Support or contradict the proposed root cause.
3. Contain concrete technical observations.
4. Be specific rather than generic.
5. Allow an engineer to understand why the evidence supports
   the conclusion.
6. Avoid presenting assumptions as facts.

Do NOT give a high score merely because the evidence contains
technical-looking words.

The key question is:

"Does this evidence actually justify the proposed root cause?"
""",

        evaluation_steps=[
            "Read the proposed root cause.",
            "Read the evidence.",
            "Determine whether the evidence is relevant.",
            "Determine whether the evidence supports the root cause.",
            "Identify unsupported conclusions.",
            "Check whether the evidence is concrete and specific.",
            "Assign a score from 0 to 1.",
            "Explain the main reasons for the score.",
        ],

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.70,

        model=JUDGE_MODEL,

        include_reason=True,
    )


    # ========================================================
    # 3. NEXT STEP QUALITY
    # ========================================================

    next_step_metric = GEval(

        name="Next Step Quality",

        criteria="""
Evaluate the recommended next step for the incident.

The next step should:

1. Directly relate to the identified root cause.
2. Be actionable.
3. Be technically appropriate.
4. Be specific enough for an engineer to execute.
5. Help resolve the incident or validate the diagnosis.
6. Avoid unnecessary actions.
7. Avoid unsafe or destructive recommendations unless clearly
   justified and appropriately constrained.

A strong next step should allow an engineer to know what to do
next.
""",

        evaluation_steps=[
            "Read the alert and incident summary.",
            "Read the proposed root cause.",
            "Read the recommended next step.",
            "Determine whether the action addresses the root cause.",
            "Determine whether an engineer can execute it.",
            "Check for unnecessary actions.",
            "Check for unsafe actions.",
            "Assign a score from 0 to 1.",
            "Explain the main reasons for the score.",
        ],

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.70,

        model=JUDGE_MODEL,

        include_reason=True,
    )


    # ========================================================
    # 4. COMPLETENESS
    # ========================================================

    completeness_metric = GEval(

        name="Analysis Completeness",

        criteria="""
Evaluate whether the incident analysis is sufficiently complete.

A good analysis should contain:

1. Clear understanding of the alert.
2. Specific root cause or clearly stated hypothesis.
3. Meaningful evidence.
4. Practical next step.
5. Appropriate handling of uncertainty.

Penalize the analysis when it:

- gives a vague root cause,
- provides no meaningful evidence,
- provides generic next steps,
- omits important incident information,
- makes unjustified claims of certainty,
- or does not provide enough information for an engineer
  to understand the incident.
""",

        evaluation_steps=[
            "Check whether the incident is understood.",
            "Check whether a specific root cause or hypothesis is given.",
            "Check whether meaningful evidence is provided.",
            "Check whether a practical next step is provided.",
            "Check whether uncertainty is handled correctly.",
            "Assign a score from 0 to 1.",
            "Explain the main reasons for the score.",
        ],

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],

        threshold=0.70,

        model=JUDGE_MODEL,

        include_reason=True,
    )


    return {
        "rootcause": rootcause_metric,
        "evidence": evidence_metric,
        "next_step": next_step_metric,
        "completeness": completeness_metric,
    }
