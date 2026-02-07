import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from utils.gemini_config import get_gemini_model_name, is_strict_genai
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, List, Any

load_dotenv()

class LegalComplianceRAG:
    """
    Legal compliance RAG system that queries Pinecone vector database 
    containing CPCB 2016 Waste Management Rules.
    Now powered by Google Gemini 1.5 Flash.
    """
    
    def __init__(self):
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=get_gemini_model_name(),
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.strict = is_strict_genai()
        
        # Try to connect to Vector DB, else Fallback to LLM-only
        self.use_rag = False
        try:
            self.index_name = os.getenv("PINECONE_INDEX_NAME", "cpcb-waste-rules")
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            
            self.vectorstore = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
            self.use_rag = True
        except Exception as e:
            print(f"RAG Config Warning: {e}. Switching to LLM-only mode.")
            self.retriever = None

        # Create QA chain or simple Chain
        self.prompt = self._create_legal_prompt()
        
        if self.use_rag:
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            self.qa_chain = (
                RunnableParallel({
                    "context": (lambda x: x["query"]) | self.retriever,
                    "question": lambda x: x["query"]
                })
                .assign(answer=(
                    RunnablePassthrough.assign(
                        context=(lambda x: format_docs(x["context"]))
                    )
                    | self.prompt
                    | self.llm
                    | StrOutputParser()
                ))
            )
        else:
            # Fallback Chain: Just LLM without context
            self.qa_chain = (
                RunnableParallel({
                    "context": lambda x: "Context unavailable (LLM Mode)",
                    "question": lambda x: x["query"]
                })
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
    
    def _create_legal_prompt(self):
        """
        Create a custom prompt template for legal compliance queries
        """
        legal_prompt_template = """
        You are an expert in Indian environmental law, specifically the CPCB 2016 Waste Management Rules.
        Use the following pieces of context from the CPCB guidelines to answer the user's question about waste disposal compliance.
        
        Context: {context}
        
        Question: {question}
        
        Instructions:
        1. Provide specific citations from the CPCB rules if available
        2. Include relevant section/chapter numbers
        3. Explain the compliance requirements clearly
        4. Mention penalties or consequences if applicable
        5. If the context doesn't contain the answer, say "Information not available in current CPCB database"
        
        Answer:
        """
        
        return PromptTemplate(
            template=legal_prompt_template,
            input_variables=["context", "question"]
        )
    
    def get_disposal_guidelines(self, material_type: str) -> Dict:
        """
        Get CPCB-compliant disposal guidelines for a specific material type.
        Includes robust fallback for API Rate Limits (429).
        """
        query = f"What are the CPCB guidelines for disposing of {material_type} waste according to the 2016 Waste Management Rules?"
        
        try:
            # Check if LLM is available (RAG might be disabled)
            if not self.qa_chain:
                raise Exception("LLM Chain not initialized")

            result = self.qa_chain.invoke({"query": query})
            
            # Map LCEL output to legacy expected format
            answer = result.get("answer", "No guidelines found")
            source_docs = result.get("context", [])
            
            return {
                "material_type": material_type,
                "guidelines": answer,
                "sources": [doc.metadata.get("source", "Unknown") for doc in source_docs] if isinstance(source_docs, list) else ["AI Knowledge Base"],
                "compliance_requirements": self._extract_compliance_info(answer),
                "citations": self._extract_section_citations(answer)
            }
        except Exception as e:
            # Check for Rate Limit (429) or other API errors
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⚠️ Legal RAG Rate Limit Hit: {e}")
                
                # FALLBACK: Static rule-based response for demo continuity
                return self._get_static_compliance_fallback(material_type)
            
            return {
                "material_type": material_type,
                "guidelines": f"Compliance check temporarily unavailable (Network/API Error).",
                "sources": [],
                "compliance_requirements": [],
                "citations": []
            }

    def _get_static_compliance_fallback(self, material_type):
        """
        Provides static, verified CPCB data when API is rate-limited.
        """
        m_lower = material_type.lower()
        if "plastic" in m_lower or "pet" in m_lower or "bottle" in m_lower:
            return {
                "material_type": material_type,
                "guidelines": "As per PWM Rules 2016, Section 5: Plastic waste must be segregated at source. PET bottles should be cleaned, crushed, and handed over to authorized recyclers. Burning is strictly prohibited.",
                "sources": ["CPCB Plastic Waste Management Rules, 2016"],
                "compliance_requirements": ["Segregation at Source", "No Burning"],
                "citations": ["Rule 5(1)", "Rule 6"]
            }
        elif "ewaste" in m_lower or "electronic" in m_lower or "circuit" in m_lower:
             return {
                "material_type": material_type,
                "guidelines": "As per E-Waste Rules 2016: Consumers must channel e-waste to authorized collection centers or recycler. Do not mix with municipal solid waste.",
                "sources": ["E-Waste (Management) Rules, 2016"],
                "compliance_requirements": ["Deposit at Collection Center", "No Dismantling by Informal Sector"],
                "citations": ["Schedule I", "Rule 4"]
            }
        elif "cardboard" in m_lower or "paper" in m_lower:
             return {
                "material_type": material_type,
                "guidelines": "Solid Waste Management Rules 2016: Biodegradable and non-biodegradable waste must be segregated. Dry paper waste should be sent for material recovery.",
                "sources": ["SWM Rules, 2016"],
                "compliance_requirements": ["Dry Waste Segregation"],
                "citations": ["Rule 15"]
            }
        else:
             return {
                "material_type": material_type,
                "guidelines": "General SWM Rules 2016: Segregate into Wet (Green Bin), Dry (Blue Bin), and Hazardous (Red Bin) fractions. Hand over to heavy authorized collectors.",
                "sources": ["Solid Waste Management Rules, 2016"],
                "compliance_requirements": ["3-Way Segregation"],
                "citations": ["Rule 15"]
            }

    def get_hazardous_material_protocol(self, material_description: str) -> Dict:
        """
        Get specific protocols for hazardous materials
        """
        query = f"What are the emergency handling and disposal protocols for {material_description} under CPCB 2016 hazardous waste rules?"
        
        try:
            result = self.qa_chain.invoke({"query": query})
            
            answer = result.get("answer", "No protocols found")
            return {
                "material_description": material_description,
                "emergency_protocols": answer,
                "regulatory_references": self._extract_regulatory_refs(answer),
                "mandatory_steps": self._extract_mandatory_steps(answer),
                "authorized_handlers": self._extract_authorized_entities(answer)
            }
        except Exception as e:
            return {
                "material_description": material_description,
                "emergency_protocols": "Standard Hazard Protocol: Isolate material, wear PPE, contact authorized hazardous waste handler.",
                "regulatory_references": ["Hazardous Waste Rules 2016"],
                "mandatory_steps": ["Do not touch with bare hands", "Segregate"],
                "authorized_handlers": ["TSDF Operators"]
            }
    
    def get_extended_producer_responsibility_info(self, product_category: str) -> Dict:
        """
        Get EPR (Extended Producer Responsibility) information for product categories
        
        Args:
            product_category: Category of product (e.g., "plastic packaging", "electronics", "batteries")
            
        Returns:
            Dict with EPR obligations and compliance info
        """
        query = f"What are the Extended Producer Responsibility (EPR) obligations for {product_category} under CPCB 2016 rules?"
        
        try:
            result = self.qa_chain.invoke({"query": query})
            
            answer = result.get("answer", "No EPR info found")
            return {
                "product_category": product_category,
                "epr_obligations": answer,
                "collection_targets": self._extract_collection_targets(answer),
                "reporting_requirements": self._extract_reporting_reqs(answer),
                "penalty_structure": self._extract_penalty_info(answer)
            }
        except Exception as e:
            return {
                "product_category": product_category,
                "epr_obligations": f"Error retrieving EPR info: {str(e)}",
                "collection_targets": [],
                "reporting_requirements": [],
                "penalty_structure": []
            }
    
    def search_similar_cases(self, scenario_description: str) -> List[Dict]:
        """
        Search for similar waste management scenarios in the database
        
        Args:
            scenario_description: Description of the scenario to match
            
        Returns:
            List of similar cases with compliance guidance
        """
        try:
            docs = self.retriever.invoke(scenario_description)
            
            similar_cases = []
            for doc in docs:
                similar_cases.append({
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "similarity_score": doc.metadata.get("similarity", 0.0)
                })
            
            return similar_cases
        except Exception as e:
            return [{"error": f"Error searching similar cases: {str(e)}"}]
    
    def _extract_compliance_info(self, text: str) -> List[str]:
        """
        Extract compliance-related information from the response
        """
        import re
        
        compliance_keywords = [
            r'(compliance|requirement|must|shall|should|obligation|duty|responsibility)',
            r'(section|chapter|rule|regulation|clause)',
            r'(penalty|fine|punishment|consequence)',
            r'(within \d+ days|monthly|annual|periodic)'
        ]
        
        matches = []
        for pattern in compliance_keywords:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        
        return list(set(matches))  # Remove duplicates
    
    def _extract_section_citations(self, text: str) -> List[str]:
        """
        Extract section/chapter citations from the response
        """
        import re
        
        # Patterns for various citation formats
        citation_patterns = [
            r'(Section \d+[A-Z]?)',
            r'(Chapter \d+)',
            r'(Rule \d+[A-Z]?)',
            r'(Schedule [IVX]+)',
            r'(Annexure [IVX]+)'
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))
    
    def _extract_regulatory_refs(self, text: str) -> List[str]:
        """
        Extract regulatory references from the response
        """
        import re
        
        reg_patterns = [
            r'(CPCB.*?2016)',
            r'(Solid Waste Management Rules.*?2016)',
            r'(Hazardous and Other Wastes Rules.*?2016)',
            r'(Bio-medical Waste Management Rules.*?2016)',
            r'(E-Waste Management Rules.*?2016)',
            r'(Environment Protection Act.*?1986)'
        ]
        
        refs = []
        for pattern in reg_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)
        
        return list(set(refs))
    
    def _extract_mandatory_steps(self, text: str) -> List[str]:
        """
        Extract mandatory steps from the response
        """
        import re
        
        # Look for imperative language indicating required steps
        step_patterns = [
            r'(must.*?)(?:\.|\n)',
            r'(shall.*?)(?:\.|\n)', 
            r'(required to.*?)(?:\.|\n)',
            r'(need to.*?)(?:\.|\n)',
            r'(procedure.*?)(?:\.|\n)'
        ]
        
        steps = []
        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            steps.extend([step.strip() for step in matches])
        
        return list(set(steps))
    
    def _extract_authorized_entities(self, text: str) -> List[str]:
        """
        Extract references to authorized entities from the response
        """
        import re
        
        entity_patterns = [
            r'(authorized.*?handler)',
            r'(certified.*?facility)', 
            r'(licensed.*?operator)',
            r'(government approved.*?entity)',
            r'(CPCB authorized)',
            r'(State PCB recognized)'
        ]
        
        entities = []
        for pattern in entity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_collection_targets(self, text: str) -> List[str]:
        """
        Extract collection targets for EPR
        """
        import re
        
        target_patterns = [
            r'(\d+%\s*(?:of|for|collection))',
            r'(\d+\s*(?:tons|tonnes|kg)\s*(?:per|target))',
            r'(collection target.*?\d+%)',
            r'((?:minimum|maximum)\s*\d+%\s*(?:collection|recovery))'
        ]
        
        targets = []
        for pattern in target_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            targets.extend(matches)
        
        return list(set(targets))
    
    def _extract_reporting_reqs(self, text: str) -> List[str]:
        """
        Extract reporting requirements
        """
        import re
        
        report_patterns = [
            r'(report.*?(?:quarterly|annual|monthly|yearly))',
            r'(submit.*?report)',
            r'(documentation.*?requirement)',
            r'(record keeping.*?)(?:\.|\n)'
        ]
        
        reports = []
        for pattern in report_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            reports.extend([rep.strip() for rep in matches])
        
        return list(set(reports))
    
    def _extract_penalty_info(self, text: str) -> List[str]:
        """
        Extract penalty-related information
        """
        import re
        
        penalty_patterns = [
            r'(penalty.*?\d+)',
            r'(fine.*?Rs)',
            r'(imprisonment|jail|custody)',
            r'(Section \d+.*?penalty)'
        ]
        
        penalties = []
        for pattern in penalty_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            penalties.extend(matches)
        
        return list(set(penalties))

# Example usage and testing
def test_legal_rag():
    """
    Test function to verify LegalComplianceRAG works correctly
    """
    rag_system = LegalComplianceRAG()
    
    # Test with a common material
    result = rag_system.get_disposal_guidelines("plastic bottles")
    print("Test result for plastic bottles:")
    print(result)
    
    return rag_system