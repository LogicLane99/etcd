from .remote_agents import PlatformAgents


class PlatformTools:

    def __init__(
        self,
        agents: PlatformAgents,
    ):
        self.agents = agents

    async def ask_kyverno_agent(
        self,
        task: str,
    ) -> str:
        """
        Ask the Kyverno specialist to investigate or manage
        Kyverno policies, policy reports, admission controls,
        validation failures and policy violations.
        """

        response = await self.agents.kyverno.run(task)

        return (
            response.text
            or "Kyverno agent returned no text."
        )


    async def ask_flux_agent(
        self,
        task: str,
    ) -> str:
        """
        Ask the Flux specialist to investigate or manage
        Flux GitOps resources, Kustomizations, HelmReleases,
        GitRepositories and reconciliation problems.
        """

        response = await self.agents.flux.run(task)

        return (
            response.text
            or "Flux agent returned no text."
        )


    async def ask_cert_manager_agent(
        self,
        task: str,
    ) -> str:
        """
        Ask the cert-manager specialist to investigate or manage
        Certificates, CertificateRequests, Issuers, ClusterIssuers,
        ACME challenges and certificate renewal.
        """

        response = await self.agents.cert_manager.run(task)

        return (
            response.text
            or "cert-manager agent returned no text."
        )


    async def ask_external_dns_agent(
        self,
        task: str,
    ) -> str:
        """
        Ask the ExternalDNS specialist to investigate or manage
        DNS records, DNSEndpoints, DNS providers and
        ExternalDNS synchronization.
        """

        response = await self.agents.external_dns.run(task)

        return (
            response.text
            or "ExternalDNS agent returned no text."
        )
