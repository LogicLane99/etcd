import asyncio


from .config import Settings
from .harness import create_platform_harness
from .remote_agents import create_remote_agents


async def main():

    print()
    print("=" * 70)
    print(" Kubernetes Platform Harness")
    print("=" * 70)
    print()

    settings = Settings.from_env()

    print(
        f"Agentgateway : "
        f"{settings.agentgateway_base_url}"
    )

    print(
        f"Model        : "
        f"{settings.harness_model}"
    )

    print(
        f"Kyverno      : "
        f"{settings.kyverno_agent_url}"
    )

    print(
        f"Flux         : "
        f"{settings.flux_agent_url}"
    )

    print(
        f"cert-manager : "
        f"{settings.cert_manager_agent_url}"
    )

    print(
        f"ExternalDNS  : "
        f"{settings.external_dns_agent_url}"
    )

    print()
    print("Type 'exit' or 'quit' to stop.")
    print()


    # Create A2A clients.
    remote_agents = create_remote_agents(
        settings
    )


    # Create Harness.
    harness = create_platform_harness(
        settings,
        remote_agents,
    )


    # One session keeps the Harness state across turns.
    session = harness.create_session()


    while True:

        try:
            user_input = input("\nYou > ")

        except (KeyboardInterrupt, EOFError):
            print()
            break


        if not user_input.strip():
            continue


        if user_input.strip().lower() in {
            "exit",
            "quit",
        }:
            break


        print()
        print("Harness > ", end="", flush=True)


        try:

            async for chunk in harness.run(
                user_input,
                session=session,
                stream=True,
            ):

                if chunk.text:
                    print(
                        chunk.text,
                        end="",
                        flush=True,
                    )

            print()


        except Exception as exc:

            print()
            print(
                f"\nERROR: {type(exc).__name__}: {exc}"
            )


if __name__ == "__main__":
    asyncio.run(main())
