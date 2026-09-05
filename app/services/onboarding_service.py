from collections import defaultdict


class OnboardingService:
    """
    Determines what information we know about a student
    and what important onboarding information is still missing.
    """

    REQUIRED_CATEGORIES = [
        "education",
        "interest",
        "skill",
        "career_goal",
        "learning_preference",
    ]

    OPTIONAL_CATEGORIES = [
        "strength",
        "weakness",
        "experience",
        "constraint",
        "motivation",
    ]

    # Different memory types that satisfy the same
    # onboarding requirement.
    CATEGORY_ALIASES = {
        "learning_preference": {
            "learning_preference",
            "learning_style",
            "preference",
        },
    }

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

    def analyze_profile(
        self,
        memories: list[dict],
    ) -> dict:

        memory_types = set()

        profile = defaultdict(list)

        for memory in memories:

            memory_type = memory.get(
                "memory_type"
            )

            if not memory_type:
                continue

            memory_types.add(memory_type)

            profile[memory_type].append(
                {
                    "key": memory.get("memory_key"),
                    "value": memory.get("value"),
                    "confidence": memory.get(
                        "confidence"
                    ),
                }
            )

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

        completion_percentage = int(
            (
                len(completed_categories)
                / len(self.REQUIRED_CATEGORIES)
            )
            * 100
        )

        onboarding_complete = (
            len(missing_categories) == 0
        )

        return {
            "profile": dict(profile),

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
        }


onboarding_service = OnboardingService()