import streamlit as st
from openai import OpenAI, APIStatusError, APITimeoutError, APIConnectionError
import os
import json
import logging
from datetime import datetime

# ============================================================
# 0. LOGGING & AUDIT TRAIL (Enterprise Compliance)
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("kagent-chat")

# ============================================================
# 1. CONFIGURATION & VALIDATION
# ============================================================
AGENT_GATEWAY_URL = os.getenv(
    "AGENT_GATEWAY_URL",
    "http://agentgateway-svc.default.svc.cluster.local/v1"
)
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "120.0"))  # k-agent tool calls can be slow

# Agent Registry: name -> description (shown in UI)
AGENT_REGISTRY = {
    "k8s-expert-agent": {
        "description": "🔧 Kubernetes troubleshooting, pod logs, deployments",
        "icon": "☸️"
    },
    "cilium-debug-agent": {
        "description": "🌐 Cilium network policies, Hubble flow analysis",
        "icon": "🔗"
    },
    "promql-agent": {
        "description": "📊 Prometheus queries, metrics analysis, alerting",
        "icon": "🔥"
    },
    "istio-agent": {
        "description": "🕸️ Istio service mesh, traffic management, mTLS",
        "icon": "⛵"
    },
}

# RBAC Mapping: Enterprise IdP Groups -> Allowed Agent Names
RBAC_MAPPING = {
    "k8s-admins": ["k8s-expert-agent", "cilium-debug-agent", "promql-agent", "istio-agent"],
    "platform-team": ["k8s-expert-agent", "cilium-debug-agent", "promql-agent"],
    "dev-team-a": ["k8s-expert-agent"],
    "ops-team-b": ["cilium-debug-agent", "promql-agent"],
    "sre-team": ["k8s-expert-agent", "cilium-debug-agent", "istio-agent"],
}

# ============================================================
# 2. ENTERPRISE AUTHENTICATION
# ============================================================
def get_user_info() -> dict:
    """
    Extracts identity from headers injected by oauth2-proxy / enterprise IdP.
    Falls back to local-dev defaults when running outside the cluster.
    """
    try:
        headers = st.context.headers
    except Exception:
        headers = {}

    user = headers.get("x-forwarded-user", "local-dev-user")
    groups_header = headers.get("x-forwarded-groups", "k8s-admins")
    jwt_token = headers.get("authorization", "").replace("Bearer ", "")

    try:
        if groups_header.startswith("["):
            groups = json.loads(groups_header)
        else:
            groups = [g.strip() for g in groups_header.split(",") if g.strip()]
    except Exception:
        groups = [groups_header] if groups_header else []

    return {"user": user, "groups": groups, "token": jwt_token}


def get_allowed_agents(groups: list[str]) -> list[str]:
    """Returns deduplicated list of agents the user's groups permit."""
    allowed = set()
    for group in groups:
        if group in RBAC_MAPPING:
            allowed.update(RBAC_MAPPING[group])
    # Only return agents that actually exist in the registry
    return [a for a in allowed if a in AGENT_REGISTRY]


# ============================================================
# 3. GATEWAY HEALTH CHECK
# ============================================================
@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid hammering the gateway
def check_gateway_health(url: str) -> bool:
    """Quick check to see if agentgateway is reachable."""
    import requests
    try:
        # Try the /models endpoint (standard OpenAI-compatible)
        resp = requests.get(
            f"{url}/models",
            timeout=5,
            headers={"Authorization": "Bearer health-check"}
        )
        # Even a 401 means the gateway is alive
        return resp.status_code in [200, 401, 403]
    except Exception:
        return False


# ============================================================
# 4. OPENAI CLIENT FACTORY
# ============================================================
def get_client(token: str) -> OpenAI:
    """Creates an OpenAI client pointed at agentgateway with proper timeouts."""
    return OpenAI(
        base_url=AGENT_GATEWAY_URL,
        api_key=token if token else "local-dev-key",
        timeout=REQUEST_TIMEOUT,
        max_retries=2,
    )


# ============================================================
# 5. MAIN APPLICATION
# ============================================================
def main():
    st.set_page_config(
        page_title="Enterprise Agent Chat",
        page_icon="🤖",
        layout="wide"
    )

    user_info = get_user_info()

    # --- Sidebar ---
    with st.sidebar:
        st.title("🔐 Agent Chat")
        st.divider()
        st.write(f"**👤 User:** `{user_info['user']}`")
        st.write(f"**🏷️ Groups:** {', '.join(user_info['groups'])}")
        st.divider()

        # Gateway Health Indicator
        if check_gateway_health(AGENT_GATEWAY_URL):
            st.success("✅ Gateway Connected")
        else:
            st.error("❌ Gateway Unreachable")
            st.caption(f"Endpoint: `{AGENT_GATEWAY_URL}`")
            st.stop()

        # RBAC-filtered agent list
        allowed_agents = get_allowed_agents(user_info["groups"])

        if not allowed_agents:
            st.error("🚫 No agents available for your groups.")
            st.info("Contact your platform team to request access.")
            st.stop()

        # Agent selector with descriptions
        agent_options = {
            f"{AGENT_REGISTRY[a]['icon']} {a}": a for a in allowed_agents
        }
        selected_label = st.selectbox(
            "Select Agent",
            options=list(agent_options.keys()),
            format_func=lambda x: f"{x}\n   └ {AGENT_REGISTRY[agent_options[x]]['description']}"
        )
        selected_agent = agent_options[selected_label]
        st.caption(AGENT_REGISTRY[selected_agent]["description"])

        st.divider()

        # Clear chat button (per-agent)
        if st.button("🗑️ Clear This Chat"):
            if selected_agent in st.session_state.get("agent_histories", {}):
                del st.session_state.agent_histories[selected_agent]
            st.rerun()

        # Export chat
        if st.button("📥 Export Chat"):
            history = st.session_state.get("agent_histories", {}).get(selected_agent, [])
            if history:
                export_text = "\n\n".join(
                    f"[{m['role'].upper()}] {m['content']}" for m in history
                )
                st.download_button(
                    label="Download .txt",
                    data=export_text,
                    file_name=f"chat-{selected_agent}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.caption("No messages to export.")

        if st.button("🚪 Logout"):
            st.markdown(
                '<meta http-equiv="refresh" content="0;url=/oauth2/sign_out">',
                unsafe_allow_html=True
            )
            st.stop()

    # --- Main Chat Area ---
    st.title(f"{AGENT_REGISTRY[selected_agent]['icon']} {selected_agent}")

    # Per-agent message history (FIXES the cross-agent bleed issue)
    if "agent_histories" not in st.session_state:
        st.session_state.agent_histories = {}
    if selected_agent not in st.session_state.agent_histories:
        st.session_state.agent_histories[selected_agent] = []

    messages = st.session_state.agent_histories[selected_agent]

    # Render existing messages
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(f"Ask {selected_agent}..."):
        # Append user message
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Audit log
        logger.info(
            "CHAT | user=%s | agent=%s | prompt_length=%d",
            user_info["user"], selected_agent, len(prompt)
        )

        # Build context window (limit to last N messages to avoid token overflow)
        context = messages[-MAX_CONTEXT_MESSAGES:]

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            try:
                client = get_client(user_info["token"])

                stream = client.chat.completions.create(
                    model=selected_agent,  # Gateway routes based on this
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in context
                    ],
                    stream=True,
                    extra_headers={
                        "X-User-Identity": user_info["user"],
                        "X-User-Groups": ",".join(user_info["groups"]),
                    },
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        full_response += delta.content
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                messages.append({"role": "assistant", "content": full_response})

                logger.info(
                    "CHAT | user=%s | agent=%s | response_length=%d",
                    user_info["user"], selected_agent, len(full_response)
                )

            except APIStatusError as e:
                if e.status_code in [401, 403]:
                    placeholder.error(
                        "🔒 **Session Expired or Access Denied.** "
                        "Please [log out](/oauth2/sign_out) and log in again."
                    )
                    logger.warning(
                        "AUTH_FAILURE | user=%s | agent=%s | status=%d",
                        user_info["user"], selected_agent, e.status_code
                    )
                else:
                    placeholder.error(
                        f"⚠️ **Agent Error ({e.status_code}):** {e.message}"
                    )
                    logger.error(
                        "API_ERROR | user=%s | agent=%s | status=%d | msg=%s",
                        user_info["user"], selected_agent, e.status_code, e.message
                    )

            except APITimeoutError:
                placeholder.error(
                    "⏱️ **Request Timed Out.** The agent took too long to respond. "
                    "Try a simpler query or check if the agent's backend is healthy."
                )
                logger.error(
                    "TIMEOUT | user=%s | agent=%s", user_info["user"], selected_agent
                )

            except APIConnectionError:
                placeholder.error(
                    "🔌 **Cannot reach AgentGateway.** "
                    "Check network policies and gateway pod status."
                )
                logger.error(
                    "CONNECTION_ERROR | user=%s | agent=%s",
                    user_info["user"], selected_agent
                )

            except Exception as e:
                placeholder.error(f"❌ **Unexpected Error:** {str(e)}")
                logger.exception(
                    "UNEXPECTED | user=%s | agent=%s", user_info["user"], selected_agent
                )


if __name__ == "__main__":
    main()