from deepeval.models import GPTModel

from config import (
    AGENTGATEWAY_API_KEY,
    EVAL_MODEL,
    LLM_BASE_URL,
)


def create_judge_model():

    model = GPTModel(
        model=EVAL_MODEL,

        # This points to agentgateway, NOT OpenAI.
        #
        # Example:
        # http://agentgateway-proxy.agentgateway-system.svc.cluster.local/v1
        #
        base_url=LLM_BASE_URL,

        # If agentgateway does not require client authentication,
        # this is just a placeholder.
        #
        # If your gateway requires authentication, put the
        # gateway client token here via Kubernetes Secret.
        api_key=AGENTGATEWAY_API_KEY,

        temperature=0,
    )

    return model
