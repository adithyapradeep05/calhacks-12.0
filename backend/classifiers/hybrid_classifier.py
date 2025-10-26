#!/usr/bin/env python3
"""
Hybrid Document Classifier
Combines LLM-based and keyword-based classification for optimal accuracy
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from llm_classifier import LLMClassifier, ClassificationResult as LLMResult
from keyword_classifier import KeywordClassifier, ClassificationResult as KeywordResult

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of hybrid document classification"""
    category: str
    confidence: float
    reasoning: str
    processing_time: float
    classifier_used: str
    model: str
    llm_result: Optional[LLMResult] = None
    keyword_result: Optional[KeywordResult] = None
    agreement: bool = False

class HybridClassifier:
    """Hybrid classifier combining LLM and keyword-based approaches"""
    
    def __init__(self, llm_provider: str = "claude", llm_model: str = None):
        self.llm_classifier = LLMClassifier(provider=llm_provider, model=llm_model)
        self.keyword_classifier = KeywordClassifier()
        
        # Agreement thresholds
        self.agreement_threshold = 0.7  # Minimum confidence for agreement
        self.llm_weight = 0.7  # Weight for LLM results when in agreement
        self.keyword_weight = 0.3  # Weight for keyword results when in agreement
        
        # Fallback thresholds
        self.llm_fallback_threshold = 0.3  # Use keyword if LLM confidence < 0.3
        self.keyword_fallback_threshold = 0.5  # Use LLM if keyword confidence < 0.5
    
    async def classify(self, content: str, filename: str = "") -> ClassificationResult:
        """Classify document using hybrid approach"""
        start_time = time.time()
        
        try:
            # Run both classifiers in parallel
            llm_task = self.llm_classifier.classify(content, filename)
            keyword_task = asyncio.create_task(
                asyncio.to_thread(self.keyword_classifier.classify, content, filename)
            )
            
            # Wait for both results
            llm_result = await llm_task
            keyword_result = await keyword_task
            
            # Determine the best approach
            final_result = self._combine_results(llm_result, keyword_result)
            
            processing_time = time.time() - start_time
            final_result.processing_time = processing_time
            
            return final_result
            
        except Exception as e:
            logger.error(f"Hybrid classification error: {e}")
            processing_time = time.time() - start_time
            
            # Fallback to keyword classifier
            try:
                keyword_result = self.keyword_classifier.classify(content, filename)
                return ClassificationResult(
                    category=keyword_result.category,
                    confidence=keyword_result.confidence,
                    reasoning=f"Hybrid classification failed, using keyword fallback: {str(e)}",
                    processing_time=processing_time,
                    classifier_used="hybrid-fallback",
                    model="keyword-matching",
                    keyword_result=keyword_result
                )
            except Exception as fallback_error:
                logger.error(f"Fallback classification also failed: {fallback_error}")
                return ClassificationResult(
                    category="general",
                    confidence=0.0,
                    reasoning=f"All classification methods failed: {str(e)}",
                    processing_time=processing_time,
                    classifier_used="hybrid-error",
                    model="none"
                )
    
    def _combine_results(self, llm_result: LLMResult, keyword_result: KeywordResult) -> ClassificationResult:
        """Combine LLM and keyword results intelligently"""
        
        # Check if results agree
        agreement = (llm_result.category == keyword_result.category)
        
        # Determine which classifier to trust more
        if agreement:
            # Results agree - combine confidences
            combined_confidence = (llm_result.confidence * self.llm_weight + 
                                 keyword_result.confidence * self.keyword_weight)
            
            # Use the more detailed reasoning
            if len(llm_result.reasoning) > len(keyword_result.reasoning):
                reasoning = llm_result.reasoning
            else:
                reasoning = keyword_result.reasoning
            
            reasoning += f" (LLM: {llm_result.confidence:.2f}, Keyword: {keyword_result.confidence:.2f})"
            
            return ClassificationResult(
                category=llm_result.category,
                confidence=combined_confidence,
                reasoning=reasoning,
                processing_time=0.0,  # Will be set by caller
                classifier_used="hybrid-agreement",
                model=f"llm+keyword",
                llm_result=llm_result,
                keyword_result=keyword_result,
                agreement=True
            )
        
        else:
            # Results disagree - choose the more confident one
            if llm_result.confidence >= self.agreement_threshold:
                # LLM is confident, use it
                reasoning = f"LLM result chosen (confidence: {llm_result.confidence:.2f}). "
                reasoning += f"Keyword suggested: {keyword_result.category} (confidence: {keyword_result.confidence:.2f})"
                
                return ClassificationResult(
                    category=llm_result.category,
                    confidence=llm_result.confidence,
                    reasoning=reasoning,
                    processing_time=0.0,
                    classifier_used="hybrid-llm-chosen",
                    model=llm_result.model,
                    llm_result=llm_result,
                    keyword_result=keyword_result,
                    agreement=False
                )
            
            elif keyword_result.confidence >= self.agreement_threshold:
                # Keyword is confident, use it
                reasoning = f"Keyword result chosen (confidence: {keyword_result.confidence:.2f}). "
                reasoning += f"LLM suggested: {llm_result.category} (confidence: {llm_result.confidence:.2f})"
                
                return ClassificationResult(
                    category=keyword_result.category,
                    confidence=keyword_result.confidence,
                    reasoning=reasoning,
                    processing_time=0.0,
                    classifier_used="hybrid-keyword-chosen",
                    model="keyword-matching",
                    llm_result=llm_result,
                    keyword_result=keyword_result,
                    agreement=False
                )
            
            else:
                # Both are uncertain - use LLM as primary, keyword as backup
                if llm_result.confidence > keyword_result.confidence:
                    chosen_result = llm_result
                    chosen_name = "LLM"
                else:
                    chosen_result = keyword_result
                    chosen_name = "keyword"
                
                reasoning = f"Both classifiers uncertain. {chosen_name} chosen (confidence: {chosen_result.confidence:.2f}). "
                reasoning += f"LLM: {llm_result.category} ({llm_result.confidence:.2f}), "
                reasoning += f"Keyword: {keyword_result.category} ({keyword_result.confidence:.2f})"
                
                return ClassificationResult(
                    category=chosen_result.category,
                    confidence=chosen_result.confidence,
                    reasoning=reasoning,
                    processing_time=0.0,
                    classifier_used="hybrid-uncertain",
                    model=chosen_result.model,
                    llm_result=llm_result,
                    keyword_result=keyword_result,
                    agreement=False
                )
    
    def get_classifier_info(self) -> Dict[str, any]:
        """Get information about the hybrid classifier"""
        return {
            "llm_available": self.llm_classifier.is_available(),
            "llm_provider": self.llm_classifier.provider,
            "llm_model": self.llm_classifier.model,
            "keyword_info": self.keyword_classifier.get_keyword_info(),
            "agreement_threshold": self.agreement_threshold,
            "llm_weight": self.llm_weight,
            "keyword_weight": self.keyword_weight
        }

# Test function
async def test_hybrid_classifier():
    """Test the hybrid classifier with sample documents"""
    print("🧪 Testing Hybrid Classifier")
    print("=" * 40)
    
    # Test documents
    test_docs = [
        {
            "content": "This software license agreement governs the use of our proprietary software. By installing or using the software, you agree to be bound by the terms and conditions set forth herein. This agreement is legally binding and enforceable under applicable law.",
            "filename": "license_agreement.pdf",
            "expected": "legal"
        },
        {
            "content": "The API endpoint /api/v1/users returns a list of user objects. Each user object contains id, name, email, and created_at fields. Authentication is required via Bearer token. This is a RESTful API implementation with proper error handling.",
            "filename": "api_documentation.md",
            "expected": "technical"
        },
        {
            "content": "Q3 2024 Financial Report: Revenue increased by 15% compared to Q2. Operating expenses were $2.3M. Net profit margin improved to 12%. Budget allocation for next quarter is $3.5M. Investment portfolio shows 8% growth.",
            "filename": "q3_financial_report.pdf",
            "expected": "financial"
        },
        {
            "content": "Employee Handbook: All employees are entitled to 15 days of paid vacation annually. Health insurance coverage begins on the first day of employment. Performance reviews are conducted quarterly. Training programs are available for professional development.",
            "filename": "employee_handbook.pdf",
            "expected": "hr"
        },
        {
            "content": "Meeting notes from the weekly team standup. Discussed project progress, upcoming deadlines, and resource allocation. Next meeting scheduled for Friday. Action items assigned to team members.",
            "filename": "meeting_notes.txt",
            "expected": "general"
        }
    ]
    
    classifier = HybridClassifier()
    
    print(f"📊 Classifier Info: {classifier.get_classifier_info()}")
    
    for i, doc in enumerate(test_docs):
        result = await classifier.classify(doc["content"], doc["filename"])
        correct = result.category == doc["expected"]
        
        print(f"\n📄 Document {i+1}: {doc['filename']}")
        print(f"   Category: {result.category} (expected: {doc['expected']}) {'✅' if correct else '❌'}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Processing Time: {result.processing_time:.3f}s")
        print(f"   Classifier Used: {result.classifier_used}")
        print(f"   Agreement: {'✅' if result.agreement else '❌'}")
        print(f"   Reasoning: {result.reasoning}")
        
        if result.llm_result and result.keyword_result:
            print(f"   LLM: {result.llm_result.category} ({result.llm_result.confidence:.2f})")
            print(f"   Keyword: {result.keyword_result.category} ({result.keyword_result.confidence:.2f})")

if __name__ == "__main__":
    asyncio.run(test_hybrid_classifier())
