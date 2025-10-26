#!/usr/bin/env python3
"""
Keyword-Based Document Classifier
Fallback classifier using keyword matching and scoring
"""

import re
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of document classification"""
    category: str
    confidence: float
    reasoning: str
    processing_time: float
    classifier_used: str
    model: str

class KeywordClassifier:
    """Keyword-based document classifier with confidence scoring"""
    
    def __init__(self):
        # Define keyword patterns for each category
        self.keyword_patterns = {
            "legal": {
                "high_confidence": [
                    "agreement", "contract", "terms", "conditions", "liability", "legal", "law",
                    "compliance", "regulation", "statute", "court", "attorney", "lawyer", "litigation",
                    "copyright", "trademark", "patent", "license", "warranty", "disclaimer",
                    "jurisdiction", "governing law", "binding", "enforceable", "breach"
                ],
                "medium_confidence": [
                    "policy", "procedure", "guideline", "standard", "requirement", "mandatory",
                    "obligation", "responsibility", "duty", "right", "entitlement", "authority"
                ],
                "low_confidence": [
                    "document", "information", "data", "record", "file", "report"
                ]
            },
            "technical": {
                "high_confidence": [
                    "api", "endpoint", "function", "method", "class", "interface", "protocol",
                    "algorithm", "implementation", "architecture", "system", "software", "code",
                    "programming", "development", "engineering", "technical", "specification",
                    "documentation", "tutorial", "guide", "reference", "sdk", "framework"
                ],
                "medium_confidence": [
                    "configuration", "setup", "installation", "deployment", "integration",
                    "testing", "debugging", "optimization", "performance", "security"
                ],
                "low_confidence": [
                    "data", "information", "content", "file", "document", "text"
                ]
            },
            "financial": {
                "high_confidence": [
                    "budget", "cost", "price", "revenue", "income", "expense", "profit", "loss",
                    "financial", "monetary", "currency", "dollar", "euro", "payment", "invoice",
                    "accounting", "bookkeeping", "audit", "tax", "taxation", "investment",
                    "portfolio", "asset", "liability", "equity", "debt", "credit", "loan"
                ],
                "medium_confidence": [
                    "report", "statement", "analysis", "forecast", "projection", "planning",
                    "allocation", "distribution", "funding", "capital", "finance"
                ],
                "low_confidence": [
                    "data", "information", "document", "file", "record", "summary"
                ]
            },
            "hr": {
                "high_confidence": [
                    "employee", "staff", "personnel", "human resources", "hr", "workforce",
                    "benefits", "compensation", "salary", "wage", "payroll", "hiring", "recruitment",
                    "training", "development", "performance", "review", "evaluation", "promotion",
                    "termination", "resignation", "leave", "vacation", "sick", "policy", "handbook"
                ],
                "medium_confidence": [
                    "workplace", "office", "department", "team", "management", "supervisor",
                    "director", "manager", "executive", "leadership", "culture", "environment"
                ],
                "low_confidence": [
                    "information", "data", "document", "file", "record", "report", "meeting"
                ]
            },
            "general": {
                "high_confidence": [
                    "meeting", "notes", "minutes", "agenda", "schedule", "calendar", "event",
                    "announcement", "newsletter", "update", "communication", "correspondence"
                ],
                "medium_confidence": [
                    "project", "task", "assignment", "deadline", "milestone", "objective", "goal"
                ],
                "low_confidence": [
                    "document", "file", "information", "data", "content", "text", "record"
                ]
            }
        }
        
        # Confidence weights for different keyword types
        self.confidence_weights = {
            "high_confidence": 3.0,
            "medium_confidence": 2.0,
            "low_confidence": 1.0
        }
        
        # Categories
        self.categories = list(self.keyword_patterns.keys())
    
    def _extract_text_features(self, content: str, filename: str = "") -> Dict[str, any]:
        """Extract text features for classification"""
        # Combine content and filename
        full_text = f"{filename} {content}".lower()
        
        # Extract features
        features = {
            "word_count": len(content.split()),
            "char_count": len(content),
            "filename": filename.lower(),
            "content": content.lower(),
            "full_text": full_text
        }
        
        return features
    
    def _calculate_keyword_scores(self, text: str) -> Dict[str, float]:
        """Calculate keyword scores for each category"""
        scores = {}
        
        for category, patterns in self.keyword_patterns.items():
            total_score = 0.0
            matched_keywords = []
            
            for confidence_level, keywords in patterns.items():
                weight = self.confidence_weights[confidence_level]
                level_score = 0.0
                
                for keyword in keywords:
                    # Count occurrences of keyword (case-insensitive)
                    count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
                    if count > 0:
                        level_score += count * weight
                        matched_keywords.append(f"{keyword}({count})")
                
                total_score += level_score
            
            scores[category] = {
                "score": total_score,
                "matched_keywords": matched_keywords
            }
        
        return scores
    
    def _calculate_filename_score(self, filename: str) -> Dict[str, float]:
        """Calculate scores based on filename patterns"""
        filename_lower = filename.lower()
        scores = {}
        
        # Legal filename patterns
        legal_patterns = ["contract", "agreement", "terms", "legal", "license", "compliance"]
        legal_score = sum(1 for pattern in legal_patterns if pattern in filename_lower)
        
        # Technical filename patterns
        technical_patterns = ["api", "code", "technical", "spec", "doc", "readme", "guide"]
        technical_score = sum(1 for pattern in technical_patterns if pattern in filename_lower)
        
        # Financial filename patterns
        financial_patterns = ["budget", "financial", "invoice", "report", "statement", "cost"]
        financial_score = sum(1 for pattern in financial_patterns if pattern in filename_lower)
        
        # HR filename patterns
        hr_patterns = ["employee", "hr", "handbook", "policy", "benefits", "training"]
        hr_score = sum(1 for pattern in hr_patterns if pattern in filename_lower)
        
        scores = {
            "legal": legal_score,
            "technical": technical_score,
            "financial": financial_score,
            "hr": hr_score,
            "general": 0  # General doesn't have specific filename patterns
        }
        
        return scores
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to [0, 1] range"""
        if not scores:
            return {category: 0.0 for category in self.categories}
        
        max_score = max(scores.values()) if scores else 1.0
        if max_score == 0:
            return {category: 0.0 for category in self.categories}
        
        return {category: score / max_score for category, score in scores.items()}
    
    def _calculate_confidence(self, scores: Dict[str, float], matched_keywords: Dict[str, List[str]]) -> float:
        """Calculate confidence based on score distribution and keyword matches"""
        if not scores:
            return 0.0
        
        # Get the highest scoring category
        max_score = max(scores.values())
        if max_score == 0:
            return 0.0
        
        # Calculate confidence based on score distribution
        sorted_scores = sorted(scores.values(), reverse=True)
        
        if len(sorted_scores) < 2:
            return min(max_score, 0.8)  # Cap at 0.8 for single category
        
        # Confidence based on how much higher the top score is
        score_ratio = sorted_scores[0] / (sorted_scores[1] + 0.1)  # Avoid division by zero
        confidence = min(score_ratio / 2.0, 0.95)  # Cap at 0.95
        
        # Boost confidence based on number of matched keywords
        top_category = max(scores, key=scores.get)
        keyword_count = len(matched_keywords.get(top_category, []))
        keyword_boost = min(keyword_count * 0.05, 0.2)  # Max 0.2 boost
        
        confidence = min(confidence + keyword_boost, 0.95)
        
        return max(0.1, confidence)  # Minimum confidence of 0.1
    
    def classify(self, content: str, filename: str = "") -> ClassificationResult:
        """Classify document using keyword matching"""
        start_time = time.time()
        
        try:
            # Extract features
            features = self._extract_text_features(content, filename)
            
            # Calculate keyword scores
            content_scores = self._calculate_keyword_scores(features["content"])
            filename_scores = self._calculate_filename_score(features["filename"])
            
            # Combine scores (content gets higher weight)
            combined_scores = {}
            for category in self.categories:
                content_score = content_scores[category]["score"]
                filename_score = filename_scores.get(category, 0)
                
                # Weight: 80% content, 20% filename
                combined_scores[category] = (content_score * 0.8) + (filename_score * 0.2)
            
            # Normalize scores
            normalized_scores = self._normalize_scores(combined_scores)
            
            # Get the best category
            best_category = max(normalized_scores, key=normalized_scores.get)
            best_score = normalized_scores[best_category]
            
            # Calculate confidence
            confidence = self._calculate_confidence(normalized_scores, 
                                                 {cat: content_scores[cat]["matched_keywords"] 
                                                  for cat in self.categories})
            
            # Generate reasoning
            matched_keywords = content_scores[best_category]["matched_keywords"]
            reasoning = f"Classified as {best_category} based on keyword matching. "
            reasoning += f"Score: {best_score:.2f}, Confidence: {confidence:.2f}. "
            reasoning += f"Matched keywords: {', '.join(matched_keywords[:5])}"  # Show first 5 keywords
            
            processing_time = time.time() - start_time
            
            return ClassificationResult(
                category=best_category,
                confidence=confidence,
                reasoning=reasoning,
                processing_time=processing_time,
                classifier_used="keyword",
                model="keyword-matching"
            )
            
        except Exception as e:
            logger.error(f"Keyword classification error: {e}")
            processing_time = time.time() - start_time
            
            return ClassificationResult(
                category="general",
                confidence=0.0,
                reasoning=f"Classification failed: {str(e)}",
                processing_time=processing_time,
                classifier_used="keyword",
                model="keyword-matching"
            )
    
    def get_keyword_info(self) -> Dict[str, int]:
        """Get information about keyword patterns"""
        total_keywords = 0
        for patterns in self.keyword_patterns.values():
            for keyword_list in patterns.values():
                total_keywords += len(keyword_list)
        
        return {
            "total_categories": len(self.categories),
            "total_keywords": total_keywords,
            "categories": self.categories
        }

# Test function
def test_keyword_classifier():
    """Test the keyword classifier with sample documents"""
    print("🧪 Testing Keyword Classifier")
    print("=" * 40)
    
    # Test documents
    test_docs = [
        {
            "content": "This software license agreement governs the use of our proprietary software. By installing or using the software, you agree to be bound by the terms and conditions set forth herein. This agreement is legally binding and enforceable.",
            "filename": "license_agreement.pdf",
            "expected": "legal"
        },
        {
            "content": "The API endpoint /api/v1/users returns a list of user objects. Each user object contains id, name, email, and created_at fields. Authentication is required via Bearer token. This is a RESTful API implementation.",
            "filename": "api_documentation.md",
            "expected": "technical"
        },
        {
            "content": "Q3 2024 Financial Report: Revenue increased by 15% compared to Q2. Operating expenses were $2.3M. Net profit margin improved to 12%. Budget allocation for next quarter is $3.5M.",
            "filename": "q3_financial_report.pdf",
            "expected": "financial"
        },
        {
            "content": "Employee Handbook: All employees are entitled to 15 days of paid vacation annually. Health insurance coverage begins on the first day of employment. Performance reviews are conducted quarterly.",
            "filename": "employee_handbook.pdf",
            "expected": "hr"
        },
        {
            "content": "Meeting notes from the weekly team standup. Discussed project progress, upcoming deadlines, and resource allocation. Next meeting scheduled for Friday.",
            "filename": "meeting_notes.txt",
            "expected": "general"
        }
    ]
    
    classifier = KeywordClassifier()
    
    print(f"📊 Classifier Info: {classifier.get_keyword_info()}")
    
    for i, doc in enumerate(test_docs):
        result = classifier.classify(doc["content"], doc["filename"])
        correct = result.category == doc["expected"]
        print(f"\n📄 Document {i+1}: {doc['filename']}")
        print(f"   Category: {result.category} (expected: {doc['expected']}) {'✅' if correct else '❌'}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Processing Time: {result.processing_time:.3f}s")
        print(f"   Reasoning: {result.reasoning}")

if __name__ == "__main__":
    test_keyword_classifier()
