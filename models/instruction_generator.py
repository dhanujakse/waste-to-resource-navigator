import os
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from utils.gemini_config import get_gemini_model_name, is_strict_genai

load_dotenv()


class InstructionGenerator:
    """
    Generates step-by-step disposal instructions using Gemini with strict JSON output.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        model_name = get_gemini_model_name()
        self.model = genai.GenerativeModel(model_name)
        self.strict = is_strict_genai()

    def generate(
        self,
        material_analysis: Dict[str, Any],
        safety_assessment: Dict[str, Any],
        compliance_info: Dict[str, Any],
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        material_type = material_analysis.get("material_type", "unknown")
        description = material_analysis.get("description", "")
        hazardous = safety_assessment.get("is_hazardous", False)
        risk_level = safety_assessment.get("risk_level", "low")
        guidelines = compliance_info.get("guidelines", "")

        prompt = f"""
You are Circular AI, a waste-to-resource assistant.
Return STRICT JSON only with keys: instructions (list of strings), do_not (list of strings), nudge (string).
Constraints:
- Use ONLY the provided guidelines if available.
- If hazardous is true, never suggest general bins or household disposal.
- If hazardous, include PPE and authorized facility handling steps.
- Keep instructions short and actionable.

Inputs:
material_type: {material_type}
description: {description}
city: {city or "unknown"}
hazardous: {hazardous}
risk_level: {risk_level}
guidelines: {guidelines}
"""

        try:
            response = self.model.generate_content(prompt)
            content = response.text or ""
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return self._normalize_output(data, material_analysis, safety_assessment)
        except Exception as e:
            if self.strict:
                raise RuntimeError(f"Gemini instruction generation failed: {e}")

        return self._fallback_output(material_analysis, safety_assessment)

    def _normalize_output(self, data: Dict[str, Any], material_analysis: Dict[str, Any], safety_assessment: Dict[str, Any]) -> Dict[str, Any]:
        instructions = data.get("instructions", [])
        do_not = data.get("do_not", [])
        nudge = data.get("nudge") or material_analysis.get("sustainability_nudge", "")

        if not isinstance(instructions, list):
            instructions = [str(instructions)] if instructions else []
        if not isinstance(do_not, list):
            do_not = [str(do_not)] if do_not else []

        return {
            "instructions": instructions,
            "do_not": do_not,
            "nudge": nudge
        }

    def _fallback_output(self, material_analysis: Dict[str, Any], safety_assessment: Dict[str, Any]) -> Dict[str, Any]:
        material_type = material_analysis.get("material_type", "material")
        hazardous = safety_assessment.get("is_hazardous", False)

        if hazardous:
            instructions = [
                "Do not open or rinse the item.",
                "Wear gloves and a mask before handling.",
                "Place in a leak-proof container.",
                "Contact an authorized hazardous waste collection center."
            ]
            do_not = [
                "Do not place in household or public bins.",
                "Do not burn or crush the item."
            ]
        else:
            instructions = [
                f"Rinse and dry the {material_type} if safe to do so.",
                "Segregate into dry waste.",
                "Hand over to an authorized recycler or collection center."
            ]
            do_not = [
                "Do not mix with wet waste.",
                "Do not burn the item."
            ]

        return {
            "instructions": instructions,
            "do_not": do_not,
            "nudge": material_analysis.get("sustainability_nudge", "")
        }
