from dataclasses import dataclass

from agent_framework.a2a import A2AAgent

from .config import Settings


@dataclass
class PlatformAgents:

    kyverno: A2AAgent

    flux: A2AAgent

    cert_manager: A2AAgent

    external_dns: A2AAgent


def create_remote_agents(
    settings: Settings,
) -> PlatformAgents:

    return PlatformAgents(

        kyverno=A2AAgent(
            name="kyverno-agent",
            url=settings.kyverno_agent_url,
            timeout=180.0,
        ),

        flux=A2AAgent(
            name="flux-system-agent",
            url=settings.flux_agent_url,
            timeout=180.0,
        ),

        cert_manager=A2AAgent(
            name="cert-manager-agent",
            url=settings.cert_manager_agent_url,
            timeout=180.0,
        ),

        external_dns=A2AAgent(
            name="external-dns-agent",
            url=settings.external_dns_agent_url,
            timeout=180.0,
        ),
    )
