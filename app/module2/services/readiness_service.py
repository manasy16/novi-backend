class ReadinessService:

    def calculate_readiness(
        self,
        career_matches: list[dict],
        skill_gaps: list[dict],
        career_dna: dict,
    ) -> dict:

        if not career_matches:
            return {
                "readiness_score": 0.0,
                "confidence": 0.0,
                "status": "insufficient_data",
                "evidence": [],
                "strengths": [],
                "gaps": [],
            }

        top_match = career_matches[0]

        skill_score = top_match.get("skill_score", 0.0)
        goal_score = top_match.get("goal_score", 0.0)

        top_career_id = top_match.get("career_id")

        career_gaps = [
            gap
            for gap in skill_gaps
            if gap.get("career_id") == top_career_id
        ]

        critical_gaps = [
            gap
            for gap in career_gaps
            if gap.get("is_critical")
        ]

        gap_penalty = min(
            len(career_gaps) * 0.05,
            0.5,
        )

        readiness_score = (
            0.6 * skill_score
            + 0.3 * goal_score
            + 0.1 * self._dna_support(career_dna)
        )

        readiness_score = max(
            0.0,
            min(
                readiness_score - gap_penalty,
                1.0,
            ),
        )

        if readiness_score >= 0.75:
            status = "high"
        elif readiness_score >= 0.50:
            status = "moderate"
        else:
            status = "developing"

        evidence = [
            f"Top career match: {top_match.get('career_name')}",
            f"Skill alignment: {skill_score:.2f}",
            f"Career goal alignment: {goal_score:.2f}",
            f"Skill gaps identified: {len(career_gaps)}",
        ]

        strengths = []

        if skill_score >= 0.5:
            strengths.append(
                "Several required skills are already present."
            )

        if goal_score > 0:
            strengths.append(
                "Career goal aligns with the matched career."
            )

        gaps = [
            gap.get("skill_name")
            for gap in career_gaps
            if gap.get("skill_name")
        ]

        return {
            "readiness_score": round(readiness_score, 4),
            "confidence": 0.75,
            "status": status,
            "career_id": top_career_id,
            "career_name": top_match.get("career_name"),
            "evidence": evidence,
            "strengths": strengths,
            "gaps": gaps,
            "critical_gaps": len(critical_gaps),
        }

    def _dna_support(self, career_dna: dict) -> float:

        if not career_dna:
            return 0.0

        scores = []

        for dimension in career_dna.values():
            score = dimension.get("score")

            if score is not None:
                scores.append(score)

        if not scores:
            return 0.0

        return sum(scores) / len(scores)


readiness_service = ReadinessService()