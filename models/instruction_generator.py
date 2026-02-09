import os
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from utils.openrouter_config import (
    get_openrouter_client,
    get_openrouter_headers,
    get_openrouter_model_text,
    is_strict_genai
)

load_dotenv()


class InstructionGenerator:
    """
    Generates step-by-step disposal instructions using Gemini with strict JSON output.
    """

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        self.client = get_openrouter_client()
        self.model_name = get_openrouter_model_text()
        self.headers = get_openrouter_headers()
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
            response = self.client.chat.completions.create(
                model=self.model_name,
                extra_headers=self.headers,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content or ""
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return self._normalize_output(data, material_analysis, safety_assessment)
            raise RuntimeError("OpenRouter returned non-JSON output.")
        except Exception as e:
            raise RuntimeError(f"OpenRouter instruction generation failed: {e}")

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
