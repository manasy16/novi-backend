from app.module2.schemas.input import Module2Input
from app.module2.graph.workflow import module2_graph
from app.module2.repositories.discovery_repository import (
    DiscoveryRepository,
)
from app.module2.repositories.career_match_repository import (
    CareerMatchRepository,
)
from app.module2.repositories.career_match_gap_repository import (
    CareerMatchGapRepository,
)
from app.module2.repositories.readiness_repository import (
    ReadinessRepository,
)
from app.module2.repositories.intelligence_repository import (
    IntelligenceRepository,
)


class Module2Service:

    def __init__(
        self,
        discovery_repository=None,
        career_match_repository=None,
        career_match_gap_repository=None,
        readiness_repository=None,
        intelligence_repository=None,
        graph=None,
    ):
        self.discovery_repository = (
            discovery_repository or DiscoveryRepository()
        )
        self.career_match_repository = (
            career_match_repository or CareerMatchRepository()
        )
        self.career_match_gap_repository = (
            career_match_gap_repository or CareerMatchGapRepository()
        )
        self.readiness_repository = (
            readiness_repository or ReadinessRepository()
        )
        self.intelligence_repository = (
            intelligence_repository or IntelligenceRepository()
        )
        self.graph = graph or module2_graph

    def run(
        self,
        module2_input: Module2Input,
        db,
    ):

        trigger = module2_input.trigger or (
            module2_input.trigger_reasons[0]
            if module2_input.trigger_reasons
            else None
        )

        discovery_run = self.discovery_repository.create_run(
            db=db,
            student_id=module2_input.student_id,
            trigger=trigger,
            career_dna_version=1,
            thread_id=getattr(module2_input, "thread_id", None),
        )

        db.commit()

        initial_state = {
            "student_id": module2_input.student_id,
            "relevant_memories": module2_input.relevant_memories,
            "weekly_update_summary": module2_input.weekly_update_summary,
            "weekly_new_information": module2_input.weekly_new_information,
            "weekly_changes": module2_input.weekly_changes,
            "trigger": trigger,
            "discovery_run_id": discovery_run.id,
            "status": "running",
        }

        try:
            result = self.graph.invoke(
                initial_state,
                context={
                    "db": db
                },
            )
            persisted_matches = self.career_match_repository.create_matches(
                db=db,
                discovery_run_id=discovery_run.id,
                student_id=module2_input.student_id,
                matches=result.get("career_matches", []),
            )
            self.career_match_gap_repository.create_gaps(
                db=db,
                career_matches=persisted_matches,
                skill_gaps=result.get("skill_gaps", []),
            )
            self.readiness_repository.create_readiness(
                db=db,
                student_id=module2_input.student_id,
                discovery_run_id=discovery_run.id,
                readiness_result=result.get("readiness", {}),
            )
            persisted_intelligence = (
                self.intelligence_repository.create_intelligence(
                    db=db,
                    student_id=module2_input.student_id,
                    discovery_run_id=discovery_run.id,
                    student_intelligence=result["student_intelligence"],
                )
            )

            self.discovery_repository.mark_completed(discovery_run)
            db.commit()
        except Exception as error:
            db.rollback()
            error_message = str(error) or type(error).__name__
            self.discovery_repository.mark_failed(
                discovery_run,
                error_message=error_message,
            )
            db.commit()
            raise

        result["discovery_run_id"] = discovery_run.id
        result["student_intelligence_id"] = persisted_intelligence.id
        result["status"] = "completed"

        return result


module2_service = Module2Service()