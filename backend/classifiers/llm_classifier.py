#!/usr/bin/env python3
"""
LLM-Based Document Classifier
Uses Claude/GPT to classify documents into categories with confidence scores
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

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

class LLMClassifier:
    """LLM-based document classifier using Claude or GPT"""
    
    def __init__(self, provider: str = "claude", model: str = None):
        self.provider = provider.lower()
        self.model = model
        self.claude_client = None
        self.openai_client = None
        
        # Initialize clients
        self._init_clients()
        
        # Classification categories
        self.categories = ["legal", "technical", "financial", "hr", "general"]
        
        # Classification prompt template
        self.classification_prompt = """
You are an expert document classifier. Analyze the given document content and filename to classify it into one of these categories:

- legal: Legal documents, contracts, terms, compliance, regulations
- technical: Technical documentation, API docs, code, specifications, engineering
- financial: Financial reports, budgets, invoices, accounting, monetary documents
- hr: Human resources, employee policies, benefits, training, personnel
- general: General documents that don't fit other categories

Document Content: {content}
Filename: {filename}

Return your classification as a JSON object with:
- category: one of the five categories above
- confidence: float between 0.0 and 1.0
- reasoning: brief explanation of your classification

Example response:
{{
    "category": "technical",
    "confidence": 0.95,
    "reasoning": "Document contains API specifications and technical implementation details"
}}

Classify this document:
"""
    
    def _init_clients(self):
        """Initialize LLM clients"""
        if self.provider == "claude" and ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                self.model = self.model or "claude-3-5-haiku-20241022"
                logger.info("✅ Claude client initialized")
            else:
                logger.warning("ANTHROPIC_API_KEY not found")
        
        elif self.provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.model = self.model or "gpt-4"
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("OPENAI_API_KEY not found")
        
        else:
            logger.warning(f"Provider {self.provider} not available or not supported")
    
    def _extract_content_preview(self, content: str, max_length: int = 2000) -> str:
        """Extract a preview of document content for classification"""
        if len(content) <= max_length:
            return content
        
        # Take first part and last part for better context
        first_part = content[:max_length//2]
        last_part = content[-max_length//2:]
        
        return f"{first_part}\n\n... [content truncated] ...\n\n{last_part}"
    
    async def classify_with_claude(self, content: str, filename: str = "") -> ClassificationResult:
        """Classify document using Claude"""
        start_time = time.time()
        
        try:
            content_preview = self._extract_content_preview(content)
            prompt = self.classification_prompt.format(
                content=content_preview,
                filename=filename
            )
            
            response = self.claude_client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,  # Low temperature for consistent classification
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate result
                category = result.get("category", "general").lower()
                if category not in self.categories:
                    category = "general"
                
                confidence = float(result.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
                
                reasoning = result.get("reasoning", "No reasoning provided")
                
                processing_time = time.time() - start_time
                
                return ClassificationResult(
                    category=category,
                    confidence=confidence,
                    reasoning=reasoning,
                    processing_time=processing_time,
                    classifier_used="llm",
                    model=self.model
                )
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Claude classification error: {e}")
            processing_time = time.time() - start_time
            
            return ClassificationResult(
                category="general",
                confidence=0.0,
                reasoning=f"Classification failed: {str(e)}",
                processing_time=processing_time,
                classifier_used="llm",
                model=self.model
            )
    
    async def classify_with_openai(self, content: str, filename: str = "") -> ClassificationResult:
        """Classify document using OpenAI GPT"""
        start_time = time.time()
        
        try:
            content_preview = self._extract_content_preview(content)
            prompt = self.classification_prompt.format(
                content=content_preview,
                filename=filename
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate result
                category = result.get("category", "general").lower()
                if category not in self.categories:
                    category = "general"
                
                confidence = float(result.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
                
                reasoning = result.get("reasoning", "No reasoning provided")
                
                processing_time = time.time() - start_time
                
                return ClassificationResult(
                    category=category,
                    confidence=confidence,
                    reasoning=reasoning,
                    processing_time=processing_time,
                    classifier_used="llm",
                    model=self.model
                )
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"OpenAI classification error: {e}")
            processing_time = time.time() - start_time
            
            return ClassificationResult(
                category="general",
                confidence=0.0,
                reasoning=f"Classification failed: {str(e)}",
                processing_time=processing_time,
                classifier_used="llm",
                model=self.model
            )
    
    async def classify(self, content: str, filename: str = "") -> ClassificationResult:
        """Classify document using the configured LLM provider"""
        if self.provider == "claude" and self.claude_client:
            return await self.classify_with_claude(content, filename)
        elif self.provider == "openai" and self.openai_client:
            return await self.classify_with_openai(content, filename)
        else:
            # Fallback to general classification
            processing_time = time.time()
            return ClassificationResult(
                category="general",
                confidence=0.0,
                reasoning=f"LLM provider {self.provider} not available",
                processing_time=0.0,
                classifier_used="llm",
                model="none"
            )
    
    def is_available(self) -> bool:
        """Check if the classifier is available"""
        if self.provider == "claude":
            return self.claude_client is not None
        elif self.provider == "openai":
            return self.openai_client is not None
        return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model"""
        return {
            "provider": self.provider,
            "model": self.model,
            "available": self.is_available()
        }

# Factory function to create classifier
def create_llm_classifier(provider: str = "claude", model: str = None) -> LLMClassifier:
    """Create an LLM classifier instance"""
    return LLMClassifier(provider=provider, model=model)

# Test function
async def test_llm_classifier():
    """Test the LLM classifier with sample documents"""
    print("🧪 Testing LLM Classifier")
    print("=" * 40)
    
    # Test documents
    test_docs = [
        {
            "content": "This software license agreement governs the use of our proprietary software. By installing or using the software, you agree to be bound by the terms and conditions set forth herein.",
            "filename": "license_agreement.pdf",
            "expected": "legal"
        },
        {
            "content": "The API endpoint /api/v1/users returns a list of user objects. Each user object contains id, name, email, and created_at fields. Authentication is required via Bearer token.",
            "filename": "api_documentation.md",
            "expected": "technical"
        },
        {
            "content": "Q3 2024 Financial Report: Revenue increased by 15% compared to Q2. Operating expenses were $2.3M. Net profit margin improved to 12%.",
            "filename": "q3_financial_report.pdf",
            "expected": "financial"
        },
        {
            "content": "Employee Handbook: All employees are entitled to 15 days of paid vacation annually. Health insurance coverage begins on the first day of employment.",
            "filename": "employee_handbook.pdf",
            "expected": "hr"
        },
        {
            "content": "Meeting notes from the weekly team standup. Discussed project progress, upcoming deadlines, and resource allocation.",
            "filename": "meeting_notes.txt",
            "expected": "general"
        }
    ]
    
    # Test with Claude
    claude_classifier = create_llm_classifier("claude")
    if claude_classifier.is_available():
        print("\n🔵 Testing Claude Classifier:")
        for i, doc in enumerate(test_docs):
            result = await claude_classifier.classify(doc["content"], doc["filename"])
            correct = result.category == doc["expected"]
            print(f"   Doc {i+1}: {result.category} (expected: {doc['expected']}) {'✅' if correct else '❌'}")
            print(f"   Confidence: {result.confidence:.2f}, Time: {result.processing_time:.2f}s")
    
    # Test with OpenAI
    openai_classifier = create_llm_classifier("openai")
    if openai_classifier.is_available():
        print("\n🟢 Testing OpenAI Classifier:")
        for i, doc in enumerate(test_docs):
            result = await openai_classifier.classify(doc["content"], doc["filename"])
            correct = result.category == doc["expected"]
            print(f"   Doc {i+1}: {result.category} (expected: {doc['expected']}) {'✅' if correct else '❌'}")
            print(f"   Confidence: {result.confidence:.2f}, Time: {result.processing_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_llm_classifier())
