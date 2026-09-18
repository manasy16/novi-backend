import requests
import streamlit as st


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