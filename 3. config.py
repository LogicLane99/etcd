import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# PostgreSQL
# ============================================================

DATABASE_URL = os.environ["DATABASE_URL"]


# ============================================================
# Agentgateway
# ============================================================

# Example:
#
# http://agentgateway-proxy.agentgateway-system.svc.cluster.local/v1
#
LLM_BASE_URL = os.environ["LLM_BASE_URL"]


# Model exposed by agentgateway.
#
# Example:
#
# gpt-4.1
# claude-sonnet-4
# llama-...
#
EVAL_MODEL = os.environ["EVAL_MODEL"]


# ============================================================
# Optional gateway authentication
# ============================================================

# IMPORTANT:
#
# This is NOT an OpenAI API key.
#
# If your agentgateway allows internal requests without
# authentication, this can remain unset.
#
# If agentgateway requires clients to authenticate,
# store the gateway client token in a Kubernetes Secret.
#
AGENTGATEWAY_API_KEY = os.getenv(
    "AGENTGATEWAY_API_KEY",
    "not-used",
)


# ============================================================
# Evaluation
# ============================================================

EVAL_VERSION = os.getenv(
    "EVAL_VERSION",
    "v1.0",
)


EVAL_BATCH_SIZE = int(
    os.getenv(
        "EVAL_BATCH_SIZE",
        "1000",
    )
)
