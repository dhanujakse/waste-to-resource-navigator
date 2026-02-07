class LocalizationManager:
    """
    Manages localization for the Circular AI application with Hindi/English support
    """
    
    def __init__(self):
        self.translations = {
            "upload_waste": {
                "en": "Upload Waste Image",
                "hi": "कचरा चित्र अपलोड करें"
            },
            "hazardous_detected": {
                "en": "⚠️ HAZARDOUS MATERIAL DETECTED",
                "hi": "⚠️ खतरनाक सामग्री पाई गई"
            },
            "safe_for_recycling": {
                "en": "✅ SAFE FOR RECYCLING",
                "hi": "✅ पुनः चक्रण के लिए सुरक्षित"
            },
            "processing": {
                "en": "Processing image...",
                "hi": "छवि संसोधित की जा रही है..."
            },
            "results": {
                "en": "Analysis Results",
                "hi": "विश्लेषण परिणाम"
            },
            "material_type": {
                "en": "Material Type",
                "hi": "सामग्री का प्रकार"
            },
            "confidence": {
                "en": "Confidence",
                "hi": "आत्मविश्वास"
            },
            "analyze_button": {
                "en": "🔍 Analyze Waste Material",
                "hi": "🔍 कचरा सामग्री का विश्लेषण करें"
            },
            "material_analysis": {
                "en": "🔬 Material Analysis",
                "hi": "🔬 सामग्री विश्लेषण"
            },
            "safety_guidelines": {
                "en": "🛡️ Safety Guidelines",
                "hi": "🛡️ सुरक्षा दिशानिर्देश"
            },
            "compliance_info": {
                "en": "📋 Regulatory Compliance",
                "hi": "📋 नियामक अनुपालन"
            },
            "recycling_options": {
                "en": "♻️ Local Recycling Options",
                "hi": "♻️ स्थानीय पुनर्चक्रण विकल्प"
            },
            "welcome_message": {
                "en": "Upload an image of waste material to begin analysis. Our AI will identify the material type, assess safety, check compliance with CPCB regulations, and connect you with local recyclers.",
                "hi": "विश्लेषण शुरू करने के लिए कचरा सामग्री की छवि अपलोड करें। हमारा एआई सामग्री के प्रकार की पहचान करेगा, सुरक्षा का मूल्यांकन करेगा, सीपीसीबी नियमों के अनुपालन की जाँच करेगा और आपको स्थानीय पुनर्चक्रण कर्ताओं से जोड़ेगा।"
            },
            "about_title": {
                "en": "About Circular AI",
                "hi": "सर्कुलर एआई के बारे में"
            },
            "about_description": {
                "en": "Circular AI bridges waste generation and resource recovery using multimodal GenAI.",
                "hi": "सर्कुलर एआई मल्टीमॉडल जेनएआई का उपयोग करके अपशिष्ट उत्पादन और संसाधन पुनर्प्राप्ति के बीच पुल बनाता है।"
            },
            "features_title": {
                "en": "Features",
                "hi": "विशेषताएँ"
            },
            "multimodal_identification": {
                "en": "Multimodal waste identification",
                "hi": "मल्टीमॉडल कचरा पहचान"
            },
            "cpcb_compliance": {
                "en": "CPCB 2016 compliance checking",
                "hi": "सीपीसीबी 2016 अनुपालन जांच"
            },
            "hazardous_detection": {
                "en": "Hazardous material detection",
                "hi": "खतरनाक सामग्री का पता लगाना"
            },
            "recycler_matching": {
                "en": "Local recycler price matching",
                "hi": "स्थानीय पुनर्चक्रण कर्ता मूल्य मिलान"
            },
            "language_support": {
                "en": "Hindi/English interface",
                "hi": "हिंदी/अंग्रेजी इंटरफेस"
            },
            "epr_tracking": {
                "en": "EPR compliance tracking",
                "hi": "ईपीआर अनुपालन ट्रैकिंग"
            },
            "image_details": {
                "en": "Image Details:",
                "hi": "छवि विवरण:"
            },
            "size_label": {
                "en": "Size:",
                "hi": "आकार:"
            },
            "format_label": {
                "en": "Format:",
                "hi": "प्रारूप:"
            },
            "mode_label": {
                "en": "Mode:",
                "hi": "मोड:"
            },
            "settings_title": {
                "en": "Settings",
                "hi": "सेटिंग्स"
            },
            "api_configured": {
                "en": "API Keys Configured",
                "hi": "एपीआई कुंजियाँ कॉन्फ़िगर की गईं"
            },
            "configure_api_warning": {
                "en": "Please configure your API keys in .env file",
                "hi": "कृपया अपनी एपीआई कुंजियाँ .env फ़ाइल में कॉन्फ़िगर करें"
            },
            "contact_recycler": {
                "en": "Contact Recycler",
                "hi": "पुनर्चक्रणकर्ता से संपर्क करें"
            },
            "contact_request_sent": {
                "en": "Contact request sent to",
                "hi": "से संपर्क अनुरोध भेजा गया"
            },
            "location_label": {
                "en": "Location:",
                "hi": "स्थान:"
            },
            "distance_label": {
                "en": "Distance:",
                "hi": "दूरी:"
            },
            "materials_accepted": {
                "en": "Materials Accepted:",
                "hi": "स्वीकृत सामग्री:"
            },
            "capacity_label": {
                "en": "Capacity:",
                "hi": "क्षमता:"
            },
            "contact_label": {
                "en": "Contact:",
                "hi": "संपर्क:"
            },
            "cpcb_guidelines": {
                "en": "CPCB Disposal Guidelines:",
                "hi": "सीपीसीबी निपटान दिशानिर्देश:"
            },
            "regulatory_citations": {
                "en": "Regulatory Citations:",
                "hi": "नियामक उद्धरण:"
            },
            "reference_sources": {
                "en": "Reference Sources:",
                "hi": "संदर्भ स्रोत:"
            },
            "risk_categories": {
                "en": "Risk Categories:",
                "hi": "जोखिम श्रेणियाँ:"
            },
            "required_safety_measures": {
                "en": "Required Safety Measures:",
                "hi": "आवश्यक सुरक्षा उपाय:"
            },
            "standard_procedures": {
                "en": "Follow standard recycling procedures.",
                "hi": "मानक पुनर्चक्रण प्रक्रियाओं का पालन करें।"
            },
            "protective_equipment": {
                "en": "Use regular protective equipment.",
                "hi": "नियमित सुरक्षात्मक उपकरण का उपयोग करें।"
            },
            "hazard_warning": {
                "en": "This material poses potential risks.",
                "hi": "यह सामग्री संभावित जोखिम पैदा करती है।"
            },
            "high_risk_warning": {
                "en": "⚠️ HIGH RISK - HAZARDOUS MATERIAL DETECTED",
                "hi": "⚠️ उच्च जोखिम - खतरनाक सामग्री पाई गई"
            },
            "medium_risk_warning": {
                "en": "⚠️ MEDIUM RISK - CAUTION ADVISED",
                "hi": "⚠️ माध्यम जोखिम - सावधानी की सलाह दी जाती है"
            },
            "category_label": {
                "en": "Category:",
                "hi": "श्रेणी:"
            },
            "description_label": {
                "en": "Description:",
                "hi": "विवरण:"
            },
            "confidence_score": {
                "en": "Confidence Score:",
                "hi": "आत्मविश्वास स्कोर:"
            },
            "language_selection": {
                "en": "Language",
                "hi": "भाषा"
            },
            "english_option": {
                "en": "English",
                "hi": "English"
            },
            "hindi_option": {
                "en": "Hindi",
                "hi": "हिंदी"
            },
            "title_en": {
                "en": "🌍 Circular AI: Waste-to-Resource Navigator",
                "hi": "🌍 सर्कुलर एआई: कचरा-से-संसाधन नेविगेटर"
            },
            "subtitle_en": {
                "en": "Bridging Waste Generation and Resource Recovery with AI",
                "hi": "एआई के साथ कचरा उत्पादन और संसाधन पुनर्प्राप्ति के बीच पुल बनाना"
            }
        }
    
    def get_translation(self, text_key: str, language: str = "en") -> str:
        """
        Get translation for a given text key and language
        
        Args:
            text_key: Key for the text to translate
            language: Language code ('en' for English, 'hi' for Hindi)
            
        Returns:
            Translated text
        """
        if text_key in self.translations:
            if language in self.translations[text_key]:
                return self.translations[text_key][language]
            else:
                # Fallback to English if language not available
                return self.translations[text_key]["en"]
        else:
            # If key doesn't exist, return the key itself
            return text_key
    
    def get_available_languages(self) -> list:
        """
        Get list of available languages
        
        Returns:
            List of language codes
        """
        languages = set()
        for key, translations in self.translations.items():
            languages.update(translations.keys())
        return sorted(list(languages))
    
    def translate_dict(self, data: dict, language: str = "en") -> dict:
        """
        Translate all string values in a dictionary
        
        Args:
            data: Dictionary to translate
            language: Target language
            
        Returns:
            Dictionary with translated values
        """
        translated = {}
        for key, value in data.items():
            if isinstance(value, str):
                translated[key] = self.get_translation(key, language)
            elif isinstance(value, dict):
                translated[key] = self.translate_dict(value, language)
            elif isinstance(value, list):
                translated_list = []
                for item in value:
                    if isinstance(item, str):
                        # If it's a known key, translate it
                        translated_list.append(self.get_translation(item, language))
                    elif isinstance(item, dict):
                        translated_list.append(self.translate_dict(item, language))
                    else:
                        translated_list.append(item)
                translated[key] = translated_list
            else:
                translated[key] = value
        return translated

# Global instance for easy access
localization_manager = LocalizationManager()

def get_text(text_key: str, language: str = "en") -> str:
    """
    Convenience function to get translated text
    
    Args:
        text_key: Key for the text to translate
        language: Language code ('en' for English, 'hi' for Hindi)
        
    Returns:
        Translated text
    """
    return localization_manager.get_translation(text_key, language)

def get_available_languages() -> list:
    """
    Get available languages
    
    Returns:
        List of language codes
    """
    return localization_manager.get_available_languages()

# Test function
def test_localization():
    """
    Test the localization functionality
    """
    print("Testing localization...")
    
    # Test English
    print("English:", get_text("upload_waste", "en"))
    
    # Test Hindi
    print("Hindi:", get_text("upload_waste", "hi"))
    
    # Test fallback
    print("Fallback:", get_text("non_existent_key", "en"))
    
    # Test available languages
    print("Available languages:", get_available_languages())
    
    return localization_manager

if __name__ == "__main__":
    test_localization()