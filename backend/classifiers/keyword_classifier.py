import re
from typing import Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of document classification."""
    category: str
    confidence: float
    reasoning: str
    processing_time_ms: int = 0

class KeywordClassifier:
    """Rule-based keyword classifier as fallback."""
    
    def __init__(self):
        # Define keyword patterns for each category
        self.category_patterns = {
            'legal': [
                r'\b(contract|agreement|terms|conditions|legal|law|attorney|lawyer|court|judge|litigation|compliance|regulatory|privacy policy|terms of service|liability|warranty|indemnification)\b',
                r'\b(shall|must|required|obligation|breach|damages|penalty|fine|regulation|statute|code|act)\b'
            ],
            'technical': [
                r'\b(code|programming|api|database|server|client|function|class|method|variable|algorithm|architecture|system|software|hardware|technical|specification|documentation|implementation|deployment|configuration)\b',
                r'\b(python|javascript|java|c\+\+|sql|html|css|react|node|docker|kubernetes|aws|azure|github|git)\b',
                r'\b(endpoint|request|response|json|xml|rest|graphql|microservice|container|pipeline|ci/cd)\b'
            ],
            'financial': [
                r'\b(invoice|payment|billing|account|budget|expense|revenue|profit|loss|tax|financial|accounting|audit|balance|statement|transaction|cost|price|fee|charge|refund|credit|debit)\b',
                r'\b(\$|dollar|euro|currency|exchange|rate|investment|portfolio|stock|bond|market|trading)\b',
                r'\b(quarterly|annual|monthly|fiscal|year|period|report|statement|ledger|bookkeeping)\b'
            ],
            'hr_docs': [
                r'\b(employee|staff|personnel|human resources|hr|job|position|role|hiring|recruitment|interview|candidate|resume|cv|benefits|salary|wage|compensation|performance|review|training|onboarding|policy|handbook|vacation|sick leave|pto)\b',
                r'\b(manager|supervisor|director|executive|team|department|organization|company|culture|workplace|diversity|inclusion)\b'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def classify(self, text: str) -> ClassificationResult:
        """Classify document text using keyword matching."""
        import time
        start_time = time.time()
        
        try:
            # Convert to lowercase for matching
            text_lower = text.lower()
            
            # Count matches for each category
            category_scores = {}
            
            for category, patterns in self.compiled_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = pattern.findall(text_lower)
                    score += len(matches)
                
                category_scores[category] = score
            
            # Find the category with highest score
            if not category_scores or max(category_scores.values()) == 0:
                # No keywords found, classify as general
                return ClassificationResult(
                    category="general",
                    confidence=0.1,
                    reasoning="No specific keywords found",
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            # Calculate confidence based on score and text length
            total_words = len(text.split())
            confidence = min(0.8, best_score / max(total_words * 0.01, 1))
            
            # Generate reasoning
            reasoning = f"Found {best_score} keyword matches for {best_category} category"
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return ClassificationResult(
                category=best_category,
                confidence=confidence,
                reasoning=reasoning,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Error in keyword classification: {e}")
            return ClassificationResult(
                category="general",
                confidence=0.1,
                reasoning=f"Classification error: {str(e)}",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def get_keyword_counts(self, text: str) -> Dict[str, int]:
        """Get keyword counts for each category (for debugging)."""
        text_lower = text.lower()
        counts = {}
        
        for category, patterns in self.compiled_patterns.items():
            total_count = 0
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                total_count += len(matches)
            counts[category] = total_count
        
        return counts
