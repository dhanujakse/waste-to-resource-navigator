import re
from typing import Dict, List, Tuple
from .vision_processor import WasteVisionAnalyzer

class SafetyAgent:
    """
    Safety agent that checks if materials are hazardous based on analysis
    """
    
    def __init__(self):
        # Define hazardous material keywords and patterns
        self.hazardous_keywords = {
            'chemicals': [
                'acid', 'alkali', 'corrosive', 'toxic', 'poison', 'pesticide',
                'insecticide', 'herbicide', 'solvent', 'paint', 'thinner',
                'battery', 'mercury', 'lead', 'cadmium', 'asbestos',
                'radioactive', 'flammable', 'explosive', 'oxidizer'
            ],
            'medical': [
                'syringe', 'needle', 'scalpel', 'blade', 'blood', 'biohazard',
                'medical waste', 'pharmaceutical', 'medication', 'tablet',
                'capsule', 'IV bag', 'catheter', 'gauze', 'bandage'
            ],
            'electronics': [
                'circuit board', 'electronic', 'computer', 'phone', 'battery',
                'wire', 'cable', 'transformer', 'capacitor', 'resistor'
            ],
            'sharp_objects': [
                'glass', 'broken', 'sharp', 'blade', 'knife', 'scissors',
                'razor', 'nail', 'screw', 'metal'
            ]
        }
        
        # Compile regex patterns for efficient matching
        self.compiled_patterns = {}
        for category, keywords in self.hazardous_keywords.items():
            pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            self.compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def check_hazardous_material(self, material_analysis: Dict) -> Dict:
        """
        Check if the material analysis indicates hazardous materials
        
        Args:
            material_analysis: Dictionary from WasteVisionAnalyzer
            
        Returns:
            Dict with safety assessment
        """
        material_type = material_analysis.get('material_type', '').lower()
        description = material_analysis.get('description', '').lower()
        material_category = material_analysis.get('material_category', '').lower()
        
        # Initialize safety assessment
        safety_assessment = {
            'is_hazardous': False,
            'risk_level': 'low',  # low, medium, high
            'hazard_categories': [],
            'safety_guidelines': [],
            'confidence': material_analysis.get('confidence_score', 0)
        }
        
        # Check for hazardous indicators in various fields
        all_text = f"{material_type} {description} {material_category}".lower()
        
        detected_hazards = []
        
        # Check each category of hazardous keywords
        for category, pattern in self.compiled_patterns.items():
            matches = pattern.findall(all_text)
            if matches:
                detected_hazards.extend([category] * len(matches))
        
        # Also check the hazardous_indicators from the vision analysis
        vision_hazards = material_analysis.get('hazardous_indicators', [])
        if vision_hazards:
            detected_hazards.extend(['vision_detected'] * len(vision_hazards))
        
        # Determine if material is hazardous
        if detected_hazards:
            safety_assessment['is_hazardous'] = True
            
            # Determine risk level based on number and type of hazards
            if len(detected_hazards) >= 3:
                safety_assessment['risk_level'] = 'high'
            elif len(detected_hazards) >= 1:
                safety_assessment['risk_level'] = 'medium'
            
            safety_assessment['hazard_categories'] = list(set(detected_hazards))
        
        # Generate safety guidelines based on hazard type
        safety_assessment['safety_guidelines'] = self._generate_safety_guidelines(
            safety_assessment['is_hazardous'],
            safety_assessment['hazard_categories']
        )
        
        return safety_assessment
    
    def _generate_safety_guidelines(self, is_hazardous: bool, hazard_categories: List[str]) -> List[str]:
        """
        Generate appropriate safety guidelines based on hazard assessment
        """
        guidelines = []
        
        if not is_hazardous:
            guidelines.extend([
                "Material appears safe for standard recycling procedures",
                "Follow general waste segregation guidelines",
                "Handle with regular protective equipment"
            ])
        else:
            if 'chemicals' in hazard_categories or 'vision_detected' in hazard_categories:
                guidelines.extend([
                    "⚠️ CHEMICAL HAZARD DETECTED",
                    "Use chemical-resistant gloves and eye protection",
                    "Ensure adequate ventilation in handling area",
                    "Contact certified hazardous waste disposal facility",
                    "Do not mix with regular recyclables"
                ])
            
            if 'medical' in hazard_categories:
                guidelines.extend([
                    "⚠️ BIOHAZARD/MEDICAL WASTE DETECTED",
                    "Use puncture-resistant gloves and face protection",
                    "Segregate immediately in leak-proof container",
                    "Contact medical waste disposal specialist",
                    "Follow CPCB biomedical waste handling protocols"
                ])
            
            if 'electronics' in hazard_categories:
                guidelines.extend([
                    "⚠️ ELECTRONIC WASTE DETECTED",
                    "Contains potentially toxic materials (lead, mercury, etc.)",
                    "Contact authorized e-waste recycling facility",
                    "Do not attempt to dismantle components",
                    "Follow E-Waste (Management) Rules, 2016"
                ])
            
            if 'sharp_objects' in hazard_categories:
                guidelines.extend([
                    "⚠️ SHARP OBJECTS DETECTED",
                    "Use cut-resistant gloves",
                    "Handle with extreme care to prevent injury",
                    "Place in puncture-proof container",
                    "Label appropriately for safe handling"
                ])
            
            # General hazardous waste guidelines
            guidelines.extend([
                "Report to local CPCB authority if required",
                "Maintain proper documentation for disposal",
                "Ensure handler is trained in hazardous material safety"
            ])
        
        return guidelines
    
    def get_regulatory_compliance_info(self, hazard_categories: List[str]) -> Dict:
        """
        Get regulatory compliance information based on hazard type
        """
        compliance_info = {
            'applicable_laws': [],
            'disposal_requirements': [],
            'documentation_needed': []
        }
        
        if not hazard_categories:
            compliance_info['applicable_laws'] = ['Solid Waste Management Rules, 2016']
            compliance_info['disposal_requirements'] = ['Standard recycling protocols']
            compliance_info['documentation_needed'] = ['Waste segregation records']
            return compliance_info
        
        if 'chemicals' in hazard_categories:
            compliance_info['applicable_laws'].extend([
                'Hazardous and Other Wastes Rules, 2016',
                'Environment Protection Act, 1986'
            ])
            compliance_info['disposal_requirements'].append(
                'Must be disposed through authorized hazardous waste handler'
            )
            compliance_info['documentation_needed'].extend([
                'Hazardous Waste Annual Returns',
                'Form 9 & 10 under Hazardous Wastes Rules'
            ])
        
        if 'medical' in hazard_categories:
            compliance_info['applicable_laws'].append(
                'Bio-medical Waste Management Rules, 2016'
            )
            compliance_info['disposal_requirements'].append(
                'Autoclaving/incineration by authorized facility'
            )
            compliance_info['documentation_needed'].append(
                'BMW Annual Report to State Pollution Control Board'
            )
        
        if 'electronics' in hazard_categories:
            compliance_info['applicable_laws'].append(
                'E-Waste (Management) Rules, 2016'
            )
            compliance_info['disposal_requirements'].append(
                'Processing by authorized dismantler/reprocessor'
            )
            compliance_info['documentation_needed'].append(
                'E-waste annual returns and certificates'
            )
        
        # Add general CPCB compliance
        compliance_info['applicable_laws'].insert(0, 'CPCB Guidelines 2016')
        
        return compliance_info