from collections import defaultdict


class OnboardingService:
    """
    Determines what information we know about a student,
    what foundational onboarding information is still missing,
    and what foundational category NOVI should explore next.
    """

    # -------------------------------------------------
    # REQUIRED FOUNDATIONAL CATEGORIES
    # -------------------------------------------------

    REQUIRED_CATEGORIES = [
        "education",
        "interest",
        "skill",
        "career_goal",
        "learning_preference",
    ]

    # -------------------------------------------------
    # OPTIONAL / FUTURE STUDENT INFORMATION
    # -------------------------------------------------

    OPTIONAL_CATEGORIES = [
        "strength",
        "weakness",
        "experience",
        "constraint",
        "motivation",
        "extracurricular",
        "project",
        "achievement",
        "hobby",
        "leadership",
    ]

    # -------------------------------------------------
    # CATEGORY ALIASES
    # -------------------------------------------------
    #
    # Different memory types can satisfy the same
    # foundational onboarding category.
    #
    # Example:
    #
    # learning_style
    #       ↓
    # learning_preference
    #
    # -------------------------------------------------

    CATEGORY_ALIASES = {
        "learning_preference": {
            "learning_preference",
            "learning_style",
            "preference",
        },
    }

    # -------------------------------------------------
    # CHECK CATEGORY COMPLETION
    # -------------------------------------------------

    def _is_category_completed(
        self,
        category: str,
        memory_types: set[str],
    ) -> bool:
        """
        Check whether an onboarding category is satisfied,
        including accepted aliases.
        """

        accepted_types = self.CATEGORY_ALIASES.get(
            category,
            {category},
        )

        return bool(
            memory_types.intersection(
                accepted_types
            )
        )

    # -------------------------------------------------
    # GET NEXT ONBOARDING FOCUS
    # -------------------------------------------------

    def get_next_onboarding_focus(
        self,
        completed_categories: list[str],
    ) -> str | None:
        """
        Determine the next foundational category NOVI
        should explore.

        This is deterministic.

        The LLM should decide HOW to ask about the category,
        but it should NOT decide WHICH foundational category
        comes next.
        """

        completed = set(
            completed_categories
        )

        for category in self.REQUIRED_CATEGORIES:

            if category not in completed:
                return category

        # All foundational categories are complete.
        return None

    # -------------------------------------------------
    # ANALYZE STUDENT PROFILE
    # -------------------------------------------------

    def analyze_profile(
        self,
        memories: list[dict],
    ) -> dict:
        """
        Analyze the student's known memories and determine:

        - known memory categories
        - completed foundational categories
        - missing foundational categories
        - onboarding completion percentage
        - whether onboarding is complete
        - next foundational onboarding focus
        """

        memory_types = set()

        profile = defaultdict(list)

        # -------------------------------------------------
        # COLLECT MEMORY INFORMATION
        # -------------------------------------------------

        for memory in memories:

            memory_type = memory.get(
                "memory_type"
            )

            if not memory_type:
                continue

            memory_types.add(
                memory_type
            )

            profile[memory_type].append(
                {
                    "key": memory.get(
                        "memory_key"
                    ),
                    "value": memory.get(
                        "value"
                    ),
                    "confidence": memory.get(
                        "confidence"
                    ),
                }
            )

        # -------------------------------------------------
        # DETERMINE COMPLETED / MISSING CATEGORIES
        # -------------------------------------------------

        completed_categories = []

        missing_categories = []

        for category in self.REQUIRED_CATEGORIES:

            if self._is_category_completed(
                category,
                memory_types,
            ):

                completed_categories.append(
                    category
                )

            else:

                missing_categories.append(
                    category
                )

        # -------------------------------------------------
        # CALCULATE ONBOARDING PERCENTAGE
        # -------------------------------------------------

        completion_percentage = int(
            (
                len(completed_categories)
                / len(self.REQUIRED_CATEGORIES)
            )
            * 100
        )

        # -------------------------------------------------
        # DETERMINE WHETHER FOUNDATION IS COMPLETE
        # -------------------------------------------------

        onboarding_complete = (
            len(missing_categories) == 0
        )

        # -------------------------------------------------
        # DETERMINE NEXT FOCUS
        # -------------------------------------------------

        next_onboarding_focus = (
            self.get_next_onboarding_focus(
                completed_categories
            )
        )

        # -------------------------------------------------
        # RETURN ANALYSIS
        # -------------------------------------------------

        return {
            "profile": dict(
                profile
            ),

            "known_categories": sorted(
                list(memory_types)
            ),

            "completed_categories":
                completed_categories,

            "missing_categories":
                missing_categories,

            "completion_percentage":
                completion_percentage,

            "onboarding_complete":
                onboarding_complete,

            "next_onboarding_focus":
                next_onboarding_focus,
        }


onboarding_service = OnboardingService()