import os

from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:

    agentgateway_base_url: str

    agentgateway_api_key: str

    harness_model: str

    kyverno_agent_url: str
    flux_agent_url: str
    cert_manager_agent_url: str
    external_dns_agent_url: str

    harness_name: str

    @classmethod
    def from_env(cls) -> "Settings":

        gateway = os.getenv(
            "AGENTGATEWAY_BASE_URL"
        )

        if not gateway:
            raise RuntimeError(
                "AGENTGATEWAY_BASE_URL is required"
            )

        return cls(

            agentgateway_base_url=gateway.rstrip("/"),

            agentgateway_api_key=os.getenv(
                "AGENTGATEWAY_API_KEY",
                "not-needed",
            ),

            harness_model=os.getenv(
                "HARNESS_MODEL",
                "gpt-4o-mini",
            ),

            kyverno_agent_url=os.getenv(
                "KYVERNO_AGENT_URL",
                f"{gateway.rstrip('/')}/kyverno",
            ),

            flux_agent_url=os.getenv(
                "FLUX_AGENT_URL",
                f"{gateway.rstrip('/')}/flux",
            ),

            cert_manager_agent_url=os.getenv(
                "CERT_MANAGER_AGENT_URL",
                f"{gateway.rstrip('/')}/cert-manager",
            ),

            external_dns_agent_url=os.getenv(
                "EXTERNAL_DNS_AGENT_URL",
                f"{gateway.rstrip('/')}/external-dns",
            ),

            harness_name=os.getenv(
                "HARNESS_NAME",
                "kubernetes-platform-harness",
            ),
        )
