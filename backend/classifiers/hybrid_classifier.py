import os
import time
from typing import Optional
from dataclasses import dataclass
import logging

from .llm_classifier import LLMClassifier, ClassificationResult as LLMClassificationResult
from .keyword_classifier import KeywordClassifier, ClassificationResult as KeywordClassificationResult

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of document classification."""
    category: str
    confidence: float
    reasoning: str
    processing_time_ms: int = 0

class HybridClassifier:
    """Combines LLM and keyword-based classification with fallback logic."""
    
    def __init__(self):
        self.llm_classifier = None
        self.keyword_classifier = KeywordClassifier()
        
        # Try to initialize LLM classifier
        try:
            self.llm_classifier = LLMClassifier()
            logger.info("LLM classifier initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM classifier: {e}")
            logger.info("Falling back to keyword-only classification")
        
        # Classification thresholds
        self.llm_confidence_threshold = 0.7
        self.keyword_confidence_threshold = 0.5
        self.min_text_length = 50  # Minimum text length for LLM classification
    
    def classify(self, text: str) -> ClassificationResult:
        """Classify document using hybrid approach."""
        start_time = time.time()
        
        try:
            # Clean and validate text
            text = text.strip()
            if not text:
                return ClassificationResult(
                    category="general",
                    confidence=0.0,
                    reasoning="Empty text",
                    processing_time_ms=0
                )
            
            # If text is too short, use keyword classifier only
            if len(text) < self.min_text_length:
                logger.info("Text too short for LLM, using keyword classifier only")
                result = self.keyword_classifier.classify(text)
                result.processing_time_ms = int((time.time() - start_time) * 1000)
                return result
            
            # Try LLM classification first (if available)
            llm_result = None
            if self.llm_classifier:
                try:
                    llm_result = self.llm_classifier.classify(text)
                    logger.info(f"LLM classification: {llm_result.category} (confidence: {llm_result.confidence})")
                except Exception as e:
                    logger.warning(f"LLM classification failed: {e}")
                    llm_result = None
            
            # Get keyword classification
            keyword_result = self.keyword_classifier.classify(text)
            logger.info(f"Keyword classification: {keyword_result.category} (confidence: {keyword_result.confidence})")
            
            # Decision logic
            if llm_result and llm_result.confidence >= self.llm_confidence_threshold:
                # High confidence LLM result - use it
                final_result = llm_result
                final_result.reasoning = f"LLM classification (high confidence): {llm_result.reasoning}"
                logger.info("Using LLM result (high confidence)")
                
            elif llm_result and keyword_result.confidence >= self.keyword_confidence_threshold:
                # Both classifiers available, compare results
                if llm_result.category == keyword_result.category:
                    # Agreement - use LLM result with boosted confidence
                    final_result = llm_result
                    final_result.confidence = min(0.9, llm_result.confidence + 0.1)
                    final_result.reasoning = f"LLM + Keyword agreement: {llm_result.reasoning}"
                    logger.info("Using LLM result (agreement with keywords)")
                else:
                    # Disagreement - use keyword result (more conservative)
                    final_result = keyword_result
                    final_result.confidence = min(0.7, keyword_result.confidence + 0.1)
                    final_result.reasoning = f"Keyword classification (disagreement with LLM): {keyword_result.reasoning}"
                    logger.info("Using keyword result (disagreement with LLM)")
                    
            elif llm_result:
                # LLM available but low confidence - use keyword if available
                if keyword_result.confidence >= self.keyword_confidence_threshold:
                    final_result = keyword_result
                    final_result.reasoning = f"Keyword classification (LLM low confidence): {keyword_result.reasoning}"
                    logger.info("Using keyword result (LLM low confidence)")
                else:
                    # Both low confidence - use LLM result
                    final_result = llm_result
                    final_result.reasoning = f"LLM classification (low confidence): {llm_result.reasoning}"
                    logger.info("Using LLM result (both low confidence)")
                    
            else:
                # No LLM classifier - use keyword result
                final_result = keyword_result
                final_result.reasoning = f"Keyword-only classification: {keyword_result.reasoning}"
                logger.info("Using keyword result (no LLM classifier)")
            
            # Update processing time
            final_result.processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Final classification: {final_result.category} (confidence: {final_result.confidence})")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in hybrid classification: {e}")
            return ClassificationResult(
                category="general",
                confidence=0.1,
                reasoning=f"Classification error: {str(e)}",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def health_check(self) -> dict:
        """Check health of both classifiers."""
        return {
            'llm_classifier': self.llm_classifier.health_check() if self.llm_classifier else False,
            'keyword_classifier': True,  # Always available
            'hybrid_available': self.llm_classifier is not None
        }
    
    def get_classification_stats(self, text: str) -> dict:
        """Get detailed classification statistics for debugging."""
        stats = {
            'text_length': len(text),
            'llm_available': self.llm_classifier is not None,
            'keyword_counts': self.keyword_classifier.get_keyword_counts(text)
        }
        
        if self.llm_classifier:
            try:
                llm_result = self.llm_classifier.classify(text)
                stats['llm_result'] = {
                    'category': llm_result.category,
                    'confidence': llm_result.confidence,
                    'reasoning': llm_result.reasoning
                }
            except Exception as e:
                stats['llm_error'] = str(e)
        
        keyword_result = self.keyword_classifier.classify(text)
        stats['keyword_result'] = {
            'category': keyword_result.category,
            'confidence': keyword_result.confidence,
            'reasoning': keyword_result.reasoning
        }
        
        return stats
