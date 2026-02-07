from typing import Dict, Any, Optional

from models.vision_processor import WasteVisionAnalyzer
from models.safety_guard import SafetyAgent
from models.legal_rag import LegalComplianceRAG
from models.instruction_generator import InstructionGenerator
from utils.recycler_matcher import match_recyclers


class CircularAISystem:
    """
    End-to-end orchestrator: vision -> safety -> compliance -> instructions -> recycler matching
    Produces a final structured JSON output plus component outputs.
    """

    def __init__(self):
        self.vision = WasteVisionAnalyzer()
        self.safety = SafetyAgent()
        self.legal = LegalComplianceRAG()
        self.instruction_gen = InstructionGenerator()

    def run(
        self,
        image_bytes: bytes,
        filename: Optional[str] = None,
        city: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None
    ) -> Dict[str, Any]:
        material_analysis = self.vision.analyze_waste_image(
            image_bytes,
            image_format="bytes",
            filename=filename
        )

        safety_assessment = self.safety.check_hazardous_material(material_analysis)

        compliance_info = self.legal.get_disposal_guidelines(
            material_analysis.get("material_type", "unknown")
        )

        instruction_payload = self.instruction_gen.generate(
            material_analysis,
            safety_assessment,
            compliance_info,
            city=city
        )

        recyclers = match_recyclers(
            material_analysis.get("material_type", ""),
            city=city,
            user_lat=user_lat,
            user_lon=user_lon,
            hazardous=safety_assessment.get("is_hazardous", False),
            limit=3
        )

        local_rules = []
        citations = compliance_info.get("citations", [])
        sources = compliance_info.get("sources", [])
        for c in citations:
            local_rules.append({"rule": c, "source": "CPCB 2016"})
        for s in sources:
            local_rules.append({"rule": "Source document", "source": s})

        final_output = {
            "item": material_analysis.get("description") or material_analysis.get("material_type", "Unknown"),
            "materials": [material_analysis.get("material_type", "Unknown")],
            "hazard_level": safety_assessment.get("risk_level", "low"),
            "confidence": (material_analysis.get("confidence_score", 0) / 100),
            "instructions": instruction_payload.get("instructions", []),
            "do_not": instruction_payload.get("do_not", []),
            "local_rules": local_rules,
            "nearby_options": [
                {
                    "name": r.get("name"),
                    "type": "collection_center",
                    "distance_km": r.get("distance")
                }
                for r in recyclers
            ],
            "nudge": instruction_payload.get("nudge") or material_analysis.get("sustainability_nudge", "")
        }

        return {
            "material_analysis": material_analysis,
            "safety_assessment": safety_assessment,
            "compliance_info": compliance_info,
            "nearby_options": recyclers,
            "final_output": final_output
        }
