import os
import json
import time
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import anthropic
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of document classification."""
    category: str
    confidence: float
    reasoning: str
    processing_time_ms: int = 0

class LLMClassifier:
    """Claude-based document classifier."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for LLM classification")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Classification prompt template
        self.classification_prompt = """Analyze this document and classify it into ONE category:

Categories:
- legal: Contracts, agreements, legal documents, compliance, terms of service, privacy policies, legal briefs, court documents
- technical: Code, APIs, technical specifications, architecture documents, software documentation, technical manuals, system designs
- financial: Invoices, budgets, financial reports, accounting documents, tax forms, expense reports, financial statements, billing
- hr_docs: Employee records, policies, job descriptions, benefits, employee handbooks, HR procedures, performance reviews, training materials
- general: Everything else that doesn't fit the above categories

Document excerpt:
{text_sample}

Respond ONLY with valid JSON in this exact format:
{{
  "category": "legal|technical|financial|hr|general",
  "confidence": 0.95,
  "reasoning": "Brief explanation of why this category was chosen"
}}

Do not include any other text or formatting."""
    
    def classify(self, text: str) -> ClassificationResult:
        """Classify document text into a category."""
        start_time = time.time()
        
        try:
            # Take first 2000 characters as sample
            text_sample = text[:2000].strip()
            
            if not text_sample:
                return ClassificationResult(
                    category="general",
                    confidence=0.0,
                    reasoning="Empty or invalid text",
                    processing_time_ms=0
                )
            
            # Prepare prompt
            prompt = self.classification_prompt.format(text_sample=text_sample)
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Validate result
                category = result.get('category', 'general')
                confidence = float(result.get('confidence', 0.0))
                reasoning = result.get('reasoning', 'No reasoning provided')
                
                # Ensure category is valid
                valid_categories = ['legal', 'technical', 'financial', 'hr_docs', 'general']
                if category not in valid_categories:
                    category = 'general'
                    confidence = min(confidence, 0.5)
                
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                return ClassificationResult(
                    category=category,
                    confidence=confidence,
                    reasoning=reasoning,
                    processing_time_ms=processing_time_ms
                )
            else:
                # Fallback if JSON parsing fails
                logger.warning(f"Failed to parse JSON from Claude response: {response_text}")
                return ClassificationResult(
                    category="general",
                    confidence=0.3,
                    reasoning="Failed to parse classification response",
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in classification: {e}")
            return ClassificationResult(
                category="general",
                confidence=0.2,
                reasoning="JSON parsing error",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            logger.error(f"Error in LLM classification: {e}")
            return ClassificationResult(
                category="general",
                confidence=0.1,
                reasoning=f"Classification error: {str(e)}",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def health_check(self) -> bool:
        """Check if Claude API is accessible."""
        try:
            # Simple test call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Claude health check failed: {e}")
            return False
