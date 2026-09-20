from datetime import datetime

import requests
import streamlit as st

from frontend.api_client import (
    APIClient,
    APIClientError,
    AuthenticationError,
    BackendUnavailableError,
    IntelligenceNotFoundError,
)


BACKEND_URL = "http://localhost:8000"


st.set_page_config(
    page_title="NOVI",
    page_icon="🎓",
    layout="centered",
)


st.title("🎓 NOVI")
st.caption("Your AI Career Counsellor")


# =========================================================
# Session state
# =========================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "completion_percentage" not in st.session_state:
    st.session_state.completion_percentage = 0

if "onboarding_status" not in st.session_state:
    st.session_state.onboarding_status = None

if "missing_categories" not in st.session_state:
    st.session_state.missing_categories = []


# =========================================================
# Login / Register
# =========================================================

if not st.session_state.access_token:

    st.subheader("Login")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password",
    )

    col1, col2 = st.columns(2)

    # -------------------------
    # Login
    # -------------------------

    with col1:

        if st.button(
            "Login",
            use_container_width=True,
        ):

            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.access_token = data[
                    "access_token"
                ]

                # Reset UI state for this login
                st.session_state.messages = []
                st.session_state.session_initialized = False
                st.session_state.conversation_id = None
                st.session_state.completion_percentage = 0
                st.session_state.onboarding_status = None
                st.session_state.missing_categories = []

                st.success(
                    "Logged in successfully."
                )

                st.rerun()

            else:

                st.error(
                    response.json().get(
                        "detail",
                        "Login failed.",
                    )
                )

    # -------------------------
    # Register
    # -------------------------

    with col2:

        if st.button(
            "Register",
            use_container_width=True,
        ):

            response = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "email": email,
                    "password": password,
                },
            )

            if response.status_code == 201:

                st.success(
                    "Registration successful. "
                    "Now login."
                )

            else:

                st.error(
                    response.json().get(
                        "detail",
                        "Registration failed.",
                    )
                )

    st.stop()


# =========================================================
# Headers
# =========================================================

headers = {
    "Authorization": (
        f"Bearer {st.session_state.access_token}"
    )
}


# =========================================================
# Sidebar
# =========================================================

st.sidebar.success("Logged in")


# -------------------------
# Onboarding Progress
# -------------------------

st.sidebar.subheader(
    "Onboarding Progress"
)

completion_percentage = (
    st.session_state.get(
        "completion_percentage",
        0,
    )
)

st.sidebar.progress(
    completion_percentage / 100
)

st.sidebar.caption(
    f"{completion_percentage}% complete"
)


# -------------------------
# Onboarding Status
# -------------------------

onboarding_status = (
    st.session_state.get(
        "onboarding_status"
    )
)

if onboarding_status == "completed":

    st.sidebar.success(
        "✓ Onboarding Complete"
    )

elif onboarding_status == "in_progress":

    st.sidebar.info(
        "Getting to know you..."
    )


# -------------------------
# Logout
# -------------------------

if st.sidebar.button("Logout"):

    st.session_state.access_token = None
    st.session_state.messages = []
    st.session_state.session_initialized = False
    st.session_state.conversation_id = None
    st.session_state.completion_percentage = 0
    st.session_state.onboarding_status = None
    st.session_state.missing_categories = []

    st.rerun()


view = st.sidebar.radio(
    "View",
    ["NOVI Chat", "Career Intelligence"],
)


def display_percentage(value):
    if isinstance(value, (int, float)):
        return f"{value * 100:.0f}%"
    return "N/A"


def display_progress(value):
    if not isinstance(value, (int, float)):
        return 0.0
    return max(0.0, min(float(value), 1.0))


def display_snapshot_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime(
            "%b %d, %Y at %H:%M"
        )
    except (AttributeError, TypeError, ValueError):
        return str(value)


def render_career_intelligence(intelligence):
    st.header("🧠 Career Intelligence")

    snapshot_date = display_snapshot_date(intelligence.get("created_at"))
    if snapshot_date:
        st.caption(f"Latest snapshot: {snapshot_date}")

    profile_summary = intelligence.get("profile_summary") or {}
    career_dna = intelligence.get("career_dna") or {}
    career_alignment = intelligence.get("career_alignment") or {}
    skill_gaps = intelligence.get("skill_gaps") or []
    readiness = intelligence.get("readiness") or {}
    insights = intelligence.get("insights") or []
    top_careers = career_alignment.get("top_careers") or []

    top_career_name = (
        top_careers[0].get("career_name", "N/A")
        if isinstance(top_careers[0], dict)
        else "N/A"
    ) if top_careers else "N/A"

    summary_columns = st.columns(4)
    with summary_columns[0]:
        st.metric(
            "Career Readiness",
            display_percentage(readiness.get("readiness_score")),
        )
    with summary_columns[1]:
        career_clarity = career_dna.get("career_clarity") or {}
        st.metric(
            "Career Clarity",
            display_percentage(career_clarity.get("score")),
        )
    with summary_columns[2]:
        st.metric("Profile Facts", profile_summary.get("total_facts", "N/A"))
    with summary_columns[3]:
        st.metric("Top Career Match", top_career_name)

    st.divider()
    st.subheader("🧬 Career DNA")
    if career_dna:
        dna_columns = st.columns(min(3, len(career_dna)))
        for index, (dimension, values) in enumerate(career_dna.items()):
            values = values if isinstance(values, dict) else {}
            with dna_columns[index % len(dna_columns)]:
                st.markdown(f"**{dimension.replace('_', ' ').title()}**")
                st.caption(f"Score: {display_percentage(values.get('score'))}")
                st.progress(display_progress(values.get("score")))
                st.caption(
                    f"Confidence: {display_percentage(values.get('confidence'))}"
                )
    else:
        st.info("Career DNA is not available yet.")

    st.subheader("🎯 Career Alignment")
    if top_careers:
        for career in top_careers[:5]:
            if not isinstance(career, dict):
                st.write(career)
                continue
            with st.container(border=True):
                st.markdown(f"**{career.get('career_name', 'N/A')}**")
                score_columns = st.columns(3)
                with score_columns[0]:
                    st.metric("Final Score", display_percentage(career.get("final_score")))
                with score_columns[1]:
                    st.metric("Skill Score", display_percentage(career.get("skill_score")))
                with score_columns[2]:
                    st.metric("Goal Score", display_percentage(career.get("goal_score")))
    else:
        st.info("No career alignment is available yet.")

    st.subheader("⚠️ Skill Gaps")
    if skill_gaps:
        gap_rows = []
        for gap in skill_gaps:
            if not isinstance(gap, dict):
                gap_rows.append({"Skill": gap})
                continue
            row = {}
            if "skill_name" in gap:
                row["Skill"] = gap["skill_name"]
            if "required_level" in gap:
                row["Required Level"] = gap["required_level"]
            if "student_skill_level" in gap:
                row["Student Level"] = gap["student_skill_level"]
            if "gap_severity" in gap:
                row["Gap Severity"] = display_percentage(gap["gap_severity"])
            if "is_critical" in gap:
                row["Priority"] = "🔴 Critical" if gap["is_critical"] else "🟡 Non-critical"
            gap_rows.append(row)
        st.dataframe(gap_rows, hide_index=True, use_container_width=True)
    else:
        st.info("No skill gaps identified for the current analysis.")

    st.subheader("📊 Readiness")
    if readiness:
        readiness_columns = st.columns(3)
        with readiness_columns[0]:
            st.metric("Readiness Score", display_percentage(readiness.get("readiness_score")))
        with readiness_columns[1]:
            st.metric("Status", readiness.get("status", "N/A"))
        with readiness_columns[2]:
            st.metric("Confidence", display_percentage(readiness.get("confidence")))
        st.progress(display_progress(readiness.get("readiness_score")))
        for label in ("strengths", "gaps", "evidence"):
            values = readiness.get(label)
            if values:
                st.markdown(f"**{label.replace('_', ' ').title()}**")
                st.write(values)
        if "critical_gaps" in readiness:
            st.markdown(f"**Critical Gaps:** {readiness['critical_gaps']}")
    else:
        st.info("Readiness is not available yet.")

    st.subheader("💡 Insights")
    if insights:
        for index, insight in enumerate(insights, start=1):
            if not isinstance(insight, dict):
                st.write(insight)
                continue
            title = insight.get("title") or insight.get("type") or f"Insight {index}"
            with st.expander(str(title)):
                for key in ("description", "confidence", "evidence"):
                    if key in insight:
                        st.markdown(f"**{key.replace('_', ' ').title()}**")
                        st.write(insight[key])
    else:
        st.info("No insights are available yet.")

    st.subheader("👤 Profile Summary")
    if profile_summary:
        st.metric("Total Facts", profile_summary.get("total_facts", "N/A"))
        categories = profile_summary.get("categories_present")
        if categories:
            st.write(categories)
    else:
        st.info("Profile summary is not available yet.")

    with st.expander("View raw intelligence data"):
        st.json({
            key: intelligence.get(key)
            for key in (
                "profile_summary",
                "insights",
                "career_dna",
                "career_alignment",
                "skill_gaps",
                "readiness",
            )
        })


if view == "Career Intelligence":

    if st.button("🔄 Refresh", key="refresh_intelligence"):
        st.rerun()

    intelligence_client = APIClient(
        BACKEND_URL,
        st.session_state.access_token,
    )

    try:
        intelligence = intelligence_client.get_student_intelligence()
        render_career_intelligence(intelligence)
    except IntelligenceNotFoundError:
        st.info(
            "No career intelligence is available yet. Continue your "
            "conversation with NOVI to build your profile."
        )
    except AuthenticationError:
        st.error(
            "Your authentication has expired. Please log in again."
        )
    except BackendUnavailableError as error:
        st.error(str(error))
    except APIClientError as error:
        st.error(f"Unable to load career intelligence: {error}")

    st.stop()


# =========================================================
# Initialize NOVI session
# =========================================================

if not st.session_state.session_initialized:

    response = requests.get(
        f"{BACKEND_URL}/module1/session",
        headers=headers,
    )

    if response.status_code == 200:

        data = response.json()

        # -------------------------
        # Save session information
        # -------------------------

        st.session_state.conversation_id = (
            data.get("conversation_id")
        )

        st.session_state.completion_percentage = (
            data.get(
                "completion_percentage",
                0,
            )
        )

        st.session_state.onboarding_status = (
            data.get(
                "onboarding_status"
            )
        )

        st.session_state.missing_categories = (
            data.get(
                "missing_categories",
                [],
            )
        )

        # -------------------------
        # Add NOVI opening message
        # -------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": data[
                    "assistant_response"
                ],
            }
        )

        st.session_state.session_initialized = True

        st.rerun()

    else:

        st.error(
            response.json().get(
                "detail",
                "Failed to initialize NOVI session.",
            )
        )


# =========================================================
# Chat history
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# =========================================================
# Chat input
# =========================================================

user_message = st.chat_input(
    "Ask NOVI about your career..."
)


if user_message:

    # =====================================================
    # Show user message
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):

        st.write(
            user_message
        )


    # =====================================================
    # Send message to backend
    # =====================================================

    payload = {
        "message": user_message,
    }

    # IMPORTANT:
    # Continue the existing conversation
    # instead of creating a new one.

    if st.session_state.conversation_id:

        payload["conversation_id"] = (
            st.session_state.conversation_id
        )


    response = requests.post(
        f"{BACKEND_URL}/module1/chat",
        headers=headers,
        json=payload,
    )


    # =====================================================
    # Handle successful response
    # =====================================================

    if response.status_code == 200:

        data = response.json()


        # -------------------------
        # Update conversation ID
        # -------------------------

        returned_conversation_id = (
            data.get(
                "conversation_id"
            )
        )

        if returned_conversation_id:

            st.session_state.conversation_id = (
                returned_conversation_id
            )


        # -------------------------
        # Update onboarding progress
        # -------------------------

        st.session_state.completion_percentage = (
            data.get(
                "completion_percentage",
                st.session_state.completion_percentage,
            )
        )


        # -------------------------
        # Update onboarding status
        # -------------------------

        st.session_state.onboarding_status = (
            data.get(
                "onboarding_status",
                st.session_state.onboarding_status,
            )
        )


        # -------------------------
        # Update missing categories
        # -------------------------

        st.session_state.missing_categories = (
            data.get(
                "missing_categories",
                st.session_state.missing_categories,
            )
        )


        # -------------------------
        # Assistant response
        # -------------------------

        assistant_message = data[
            "assistant_response"
        ]


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )


        with st.chat_message(
            "assistant"
        ):

            st.write(
                assistant_message
            )


        # Rerun so sidebar progress
        # immediately reflects new percentage.

        st.rerun()


    # =====================================================
    # Handle backend error
    # =====================================================

    else:

        st.error(
            response.json().get(
                "detail",
                "Something went wrong.",
            )
        )