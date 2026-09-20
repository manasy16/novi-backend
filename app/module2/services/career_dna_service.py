class CareerDNAService:

    def build_career_dna(
        self,
        profile: dict,
        insights: list[dict],
    ) -> dict:

        dna = {}

        skills = profile.get("skills", [])
        projects = profile.get("projects", [])
        career_goals = profile.get("career_goals", [])
        interests = profile.get("interests", [])
        learning_preferences = profile.get(
            "learning_preferences",
            [],
        )

        # ---------------------------------------------
        # Technical Orientation
        # ---------------------------------------------

        technical_evidence = []

        if skills:
            technical_evidence.append(
                f"{len(skills)} technical skill(s) recorded"
            )

        if projects:
            technical_evidence.append(
                f"{len(projects)} project(s) recorded"
            )

        if any(
            insight.get("type") == "applied_learning"
            for insight in insights
        ):
            technical_evidence.append(
                "Applied learning evidence detected"
            )

        technical_score = 0.0

        if skills:
            technical_score += 0.4

        if projects:
            technical_score += 0.3

        if any(
            insight.get("type") == "applied_learning"
            for insight in insights
        ):
            technical_score += 0.2

        if technical_evidence:
            technical_score = min(
                technical_score,
                1.0,
            )

            dna["technical_orientation"] = {
                "score": technical_score,
                "confidence": 0.75,
                "evidence": technical_evidence,
            }

        # ---------------------------------------------
        # Analytical Orientation
        # ---------------------------------------------

        analytical_evidence = []

        if skills:
            analytical_evidence.append(
                "Technical skills are recorded"
            )

        if projects:
            analytical_evidence.append(
                "Project-based technical activity is recorded"
            )

        analytical_score = 0.0

        if skills:
            analytical_score += 0.4

        if projects:
            analytical_score += 0.3

        if any(
            insight.get("type") == "applied_learning"
            for insight in insights
        ):
            analytical_score += 0.2

        if analytical_evidence:
            dna["analytical_orientation"] = {
                "score": min(
                    analytical_score,
                    1.0,
                ),
                "confidence": 0.65,
                "evidence": analytical_evidence,
            }

        # ---------------------------------------------
        # Career Clarity
        # ---------------------------------------------

        clarity_evidence = []

        if career_goals:
            clarity_evidence.append(
                f"{len(career_goals)} career goal(s) recorded"
            )

        if any(
            insight.get("type") == "career_direction"
            for insight in insights
        ):
            clarity_evidence.append(
                "Explicit career direction identified"
            )

        if clarity_evidence:
            clarity_score = 0.0

            if career_goals:
                clarity_score += 0.6

            if any(
                insight.get("type") == "career_direction"
                for insight in insights
            ):
                clarity_score += 0.3

            dna["career_clarity"] = {
                "score": min(
                    clarity_score,
                    1.0,
                ),
                "confidence": 0.85,
                "evidence": clarity_evidence,
            }

        # ---------------------------------------------
        # Learning Orientation
        # ---------------------------------------------

        learning_evidence = []

        if learning_preferences:
            learning_evidence.append(
                "Learning preferences recorded"
            )

        if projects:
            learning_evidence.append(
                "Project activity provides learning evidence"
            )

        learning_score = 0.0

        if learning_preferences:
            learning_score += 0.4

        if projects:
            learning_score += 0.3

        if learning_evidence:
            dna["learning_orientation"] = {
                "score": min(
                    learning_score,
                    1.0,
                ),
                "confidence": 0.65,
                "evidence": learning_evidence,
            }

        return dna


career_dna_service = CareerDNAService()