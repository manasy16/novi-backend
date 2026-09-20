class InsightService:

    def analyze(self, profile: dict) -> list[dict]:

        insights = []

        skills = profile.get("skills", [])
        projects = profile.get("projects", [])
        career_goals = profile.get("career_goals", [])
        interests = profile.get("interests", [])

        # -------------------------------------------------
        # 1. Career direction
        # -------------------------------------------------

        if career_goals:

            goal_values = [
                item.get("normalized_value")
                or item.get("value")
                for item in career_goals
            ]

            evidence = [
                f"Career goal: {goal}"
                for goal in goal_values
                if goal
            ]

            if projects:
                evidence.append(
                    f"Projects recorded: {len(projects)}"
                )

            if skills:
                evidence.append(
                    f"Skills recorded: {len(skills)}"
                )

            insights.append({
                "type": "career_direction",
                "title": "Career direction identified",
                "description": (
                    "The student has explicitly recorded "
                    "one or more career goals."
                ),
                "evidence": evidence,
                "confidence": 0.9,
            })

        # -------------------------------------------------
        # 2. Project-based learning evidence
        # -------------------------------------------------

        if projects and skills:

            insights.append({
                "type": "applied_learning",
                "title": "Applied learning evidence",
                "description": (
                    "The student has both recorded skills "
                    "and project experience."
                ),
                "evidence": [
                    f"Projects: {len(projects)}",
                    f"Skills: {len(skills)}",
                ],
                "confidence": 0.8,
            })

        # -------------------------------------------------
        # 3. Interest + career goal relationship
        # -------------------------------------------------

        if interests and career_goals:

            insights.append({
                "type": "interest_career_alignment",
                "title": "Interest connected to career goal",
                "description": (
                    "The student has recorded both interests "
                    "and career goals."
                ),
                "evidence": [
                    f"Interests: {len(interests)}",
                    f"Career goals: {len(career_goals)}",
                ],
                "confidence": 0.75,
            })

        return insights


insight_service = InsightService()