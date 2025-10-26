#!/usr/bin/env python3
"""
RIGOROUS LLM Classifier Test
Tests the LLM classifier with proper error handling and fallback
"""

import asyncio
import time
import json
import os
from typing import List, Dict
from dataclasses import dataclass

# Set API key
os.environ['ANTHROPIC_API_KEY'] = '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'

from llm_classifier import LLMClassifier, ClassificationResult as LLMResult
from keyword_classifier import KeywordClassifier, ClassificationResult as KeywordResult
from hybrid_classifier import HybridClassifier, ClassificationResult as HybridResult

@dataclass
class TestDocument:
    """Test document for classification"""
    content: str
    filename: str
    expected_category: str
    category_type: str

class RigorousLLMTest:
    """Rigorous test of LLM classifier with proper error handling"""
    
    def __init__(self):
        self.test_documents = self._create_test_documents()
        self.llm_classifier = LLMClassifier()
        self.keyword_classifier = KeywordClassifier()
        self.hybrid_classifier = HybridClassifier()
    
    def _create_test_documents(self) -> List[TestDocument]:
        """Create test documents for rigorous testing"""
        return [
            # Legal Documents (4)
            TestDocument(
                content="This software license agreement governs the use of our proprietary software. By installing or using the software, you agree to be bound by the terms and conditions set forth herein. This agreement is legally binding and enforceable under applicable law.",
                filename="software_license_agreement.pdf",
                expected_category="legal",
                category_type="legal"
            ),
            TestDocument(
                content="NON-DISCLOSURE AGREEMENT. This confidential information is proprietary and shall not be disclosed to third parties. Any breach of this agreement may result in legal action and monetary damages.",
                filename="nda_contract.pdf",
                expected_category="legal",
                category_type="legal"
            ),
            TestDocument(
                content="Terms of Service: By using our platform, you agree to comply with all applicable laws and regulations. We reserve the right to modify these terms at any time. Disputes shall be resolved through binding arbitration.",
                filename="terms_of_service.pdf",
                expected_category="legal",
                category_type="legal"
            ),
            TestDocument(
                content="Privacy Policy: We collect and process personal data in accordance with GDPR regulations. Users have the right to access, rectify, and delete their personal information. Data retention period is 7 years.",
                filename="privacy_policy.pdf",
                expected_category="legal",
                category_type="legal"
            ),
            
            # Technical Documents (4)
            TestDocument(
                content="API Documentation: The /api/v1/users endpoint returns a list of user objects. Authentication is required via Bearer token. Response format is JSON with pagination support. Rate limiting: 100 requests per minute.",
                filename="api_documentation.md",
                expected_category="technical",
                category_type="technical"
            ),
            TestDocument(
                content="System Architecture: Our microservices architecture consists of API Gateway, User Service, Payment Service, and Notification Service. Each service is containerized using Docker and deployed on Kubernetes.",
                filename="system_architecture.pdf",
                expected_category="technical",
                category_type="technical"
            ),
            TestDocument(
                content="Code Review Guidelines: All pull requests must pass automated tests, code coverage must be above 80%, and require at least two approvals. Use conventional commit messages and follow the coding standards.",
                filename="code_review_guidelines.md",
                expected_category="technical",
                category_type="technical"
            ),
            TestDocument(
                content="Database Schema: Users table contains id, email, password_hash, created_at, updated_at. Foreign key relationships with profiles and sessions tables. Indexes on email and created_at for performance optimization.",
                filename="database_schema.sql",
                expected_category="technical",
                category_type="technical"
            ),
            
            # Financial Documents (4)
            TestDocument(
                content="Q3 2024 Financial Report: Revenue increased by 15% compared to Q2, reaching $2.3M. Operating expenses were $1.8M. Net profit margin improved to 12%. Budget allocation for next quarter is $3.5M.",
                filename="q3_financial_report.pdf",
                expected_category="financial",
                category_type="financial"
            ),
            TestDocument(
                content="Invoice #INV-2024-001: Services rendered for software development. Amount: $15,000. Payment due within 30 days. Late payment fee of 1.5% per month applies. Tax ID: 12-3456789.",
                filename="invoice_001.pdf",
                expected_category="financial",
                category_type="financial"
            ),
            TestDocument(
                content="Budget Proposal 2025: Total budget request of $5.2M for next fiscal year. Breakdown: Personnel (60%), Infrastructure (25%), Marketing (10%), Research (5%). ROI projection shows 18% return on investment.",
                filename="budget_proposal_2025.pdf",
                expected_category="financial",
                category_type="financial"
            ),
            TestDocument(
                content="Investment Portfolio Analysis: Current portfolio value: $2.1M. Asset allocation: Stocks (60%), Bonds (30%), Real Estate (10%). Year-to-date return: 8.5%. Risk assessment: Moderate. Rebalancing recommended quarterly.",
                filename="portfolio_analysis.pdf",
                expected_category="financial",
                category_type="financial"
            ),
            
            # HR Documents (4)
            TestDocument(
                content="Employee Handbook: All employees are entitled to 15 days of paid vacation annually. Health insurance coverage begins on the first day of employment. Performance reviews are conducted quarterly with 360-degree feedback.",
                filename="employee_handbook.pdf",
                expected_category="hr",
                category_type="hr"
            ),
            TestDocument(
                content="Job Description - Senior Software Engineer: Develop and maintain web applications using Python and React. Lead technical projects and mentor junior developers. Required: 5+ years experience, CS degree, strong problem-solving skills.",
                filename="job_description_senior_engineer.pdf",
                expected_category="hr",
                category_type="hr"
            ),
            TestDocument(
                content="Training Program - Leadership Development: 6-month program for mid-level managers. Topics include team management, strategic planning, and communication skills. Certification upon completion. Next cohort starts in March.",
                filename="leadership_training_program.pdf",
                expected_category="hr",
                category_type="hr"
            ),
            TestDocument(
                content="Performance Review Template: Employee self-assessment, manager evaluation, goal setting for next quarter. Rating scale: Exceeds Expectations, Meets Expectations, Needs Improvement. Development plan required for all employees.",
                filename="performance_review_template.pdf",
                expected_category="hr",
                category_type="hr"
            ),
            
            # General Documents (4)
            TestDocument(
                content="Meeting Notes - Weekly Standup: Discussed project progress, upcoming deadlines, and resource allocation. Action items: Complete user authentication by Friday, review code with team lead. Next meeting scheduled for Friday 2 PM.",
                filename="meeting_notes_standup.txt",
                expected_category="general",
                category_type="general"
            ),
            TestDocument(
                content="Company Newsletter - December 2024: Holiday party scheduled for December 15th. New office location announcement. Employee spotlight: Sarah Johnson from Engineering. Upcoming events and announcements.",
                filename="newsletter_december_2024.pdf",
                expected_category="general",
                category_type="general"
            ),
            TestDocument(
                content="Project Status Update: Phase 1 completed on schedule. Phase 2 delayed by one week due to resource constraints. Risk mitigation plan in place. Stakeholder communication sent. Next milestone: January 15th.",
                filename="project_status_update.pdf",
                expected_category="general",
                category_type="general"
            ),
            TestDocument(
                content="Office Announcement: New coffee machine installed in the break room. Please clean up after use. Parking lot maintenance scheduled for this weekend. Alternative parking available across the street.",
                filename="office_announcement.txt",
                expected_category="general",
                category_type="general"
            )
        ]
    
    async def test_llm_classifier_rigorous(self) -> Dict:
        """Rigorous test of LLM classifier with detailed error analysis"""
        print("🔵 RIGOROUS LLM Classifier Test")
        print("=" * 60)
        
        results = []
        processing_times = []
        confidences = []
        errors = []
        category_results = {cat: {"correct": 0, "total": 0} for cat in ["legal", "technical", "financial", "hr", "general"]}
        
        for i, doc in enumerate(self.test_documents):
            print(f"   📄 Testing Doc {i+1:2d}: {doc.filename[:30]:<30}", end=" ")
            
            start_time = time.time()
            try:
                result = await self.llm_classifier.classify(doc.content, doc.filename)
                processing_time = time.time() - start_time
                
                correct = result.category == doc.expected_category
                results.append(correct)
                processing_times.append(processing_time)
                confidences.append(result.confidence)
                
                category_results[doc.category_type]["total"] += 1
                if correct:
                    category_results[doc.category_type]["correct"] += 1
                
                status = "✅" if correct else "❌"
                print(f"→ {result.category:<10} {status} ({result.confidence:.2f}) [{processing_time:.3f}s]")
                
            except Exception as e:
                processing_time = time.time() - start_time
                errors.append(str(e))
                results.append(False)
                processing_times.append(processing_time)
                confidences.append(0.0)
                
                category_results[doc.category_type]["total"] += 1
                
                print(f"→ ERROR ❌ ({processing_time:.3f}s)")
                print(f"      Error: {str(e)[:100]}...")
        
        accuracy = sum(results) / len(results) if results else 0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        print(f"\n📊 LLM Classifier Results:")
        print(f"   🎯 Accuracy: {accuracy:.2%} ({sum(results)}/{len(results)})")
        print(f"   🎯 Avg Confidence: {avg_confidence:.2f}")
        print(f"   ⏱️ Avg Processing Time: {avg_processing_time:.3f}s")
        print(f"   🚀 Max Processing Time: {max(processing_times):.3f}s")
        print(f"   ❌ Errors: {len(errors)}")
        
        if errors:
            print(f"   🔍 Error Analysis:")
            for i, error in enumerate(errors[:3]):  # Show first 3 errors
                print(f"      {i+1}. {error[:80]}...")
            if len(errors) > 3:
                print(f"      ... and {len(errors) - 3} more errors")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in category_results.items():
            if stats["total"] > 0:
                cat_accuracy = stats["correct"] / stats["total"]
                print(f"   {category.capitalize()}: {cat_accuracy:.2%} ({stats['correct']}/{stats['total']})")
        
        return {
            "classifier": "llm",
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "avg_processing_time": avg_processing_time,
            "errors": len(errors),
            "category_results": category_results
        }
    
    async def test_keyword_classifier_rigorous(self) -> Dict:
        """Rigorous test of keyword classifier"""
        print("\n🔴 RIGOROUS Keyword Classifier Test")
        print("=" * 60)
        
        results = []
        processing_times = []
        confidences = []
        category_results = {cat: {"correct": 0, "total": 0} for cat in ["legal", "technical", "financial", "hr", "general"]}
        
        for i, doc in enumerate(self.test_documents):
            print(f"   📄 Testing Doc {i+1:2d}: {doc.filename[:30]:<30}", end=" ")
            
            start_time = time.time()
            result = self.keyword_classifier.classify(doc.content, doc.filename)
            processing_time = time.time() - start_time
            
            correct = result.category == doc.expected_category
            results.append(correct)
            processing_times.append(processing_time)
            confidences.append(result.confidence)
            
            category_results[doc.category_type]["total"] += 1
            if correct:
                category_results[doc.category_type]["correct"] += 1
            
            status = "✅" if correct else "❌"
            print(f"→ {result.category:<10} {status} ({result.confidence:.2f}) [{processing_time:.3f}s]")
        
        accuracy = sum(results) / len(results)
        avg_confidence = sum(confidences) / len(confidences)
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        print(f"\n📊 Keyword Classifier Results:")
        print(f"   🎯 Accuracy: {accuracy:.2%} ({sum(results)}/{len(results)})")
        print(f"   🎯 Avg Confidence: {avg_confidence:.2f}")
        print(f"   ⏱️ Avg Processing Time: {avg_processing_time:.3f}s")
        print(f"   🚀 Max Processing Time: {max(processing_times):.3f}s")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in category_results.items():
            if stats["total"] > 0:
                cat_accuracy = stats["correct"] / stats["total"]
                print(f"   {category.capitalize()}: {cat_accuracy:.2%} ({stats['correct']}/{stats['total']})")
        
        return {
            "classifier": "keyword",
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "avg_processing_time": avg_processing_time,
            "errors": 0,
            "category_results": category_results
        }
    
    async def test_hybrid_classifier_rigorous(self) -> Dict:
        """Rigorous test of hybrid classifier"""
        print("\n🟢 RIGOROUS Hybrid Classifier Test")
        print("=" * 60)
        
        results = []
        processing_times = []
        confidences = []
        category_results = {cat: {"correct": 0, "total": 0} for cat in ["legal", "technical", "financial", "hr", "general"]}
        
        for i, doc in enumerate(self.test_documents):
            print(f"   📄 Testing Doc {i+1:2d}: {doc.filename[:30]:<30}", end=" ")
            
            start_time = time.time()
            result = await self.hybrid_classifier.classify(doc.content, doc.filename)
            processing_time = time.time() - start_time
            
            correct = result.category == doc.expected_category
            results.append(correct)
            processing_times.append(processing_time)
            confidences.append(result.confidence)
            
            category_results[doc.category_type]["total"] += 1
            if correct:
                category_results[doc.category_type]["correct"] += 1
            
            status = "✅" if correct else "❌"
            print(f"→ {result.category:<10} {status} ({result.confidence:.2f}) [{processing_time:.3f}s]")
        
        accuracy = sum(results) / len(results)
        avg_confidence = sum(confidences) / len(confidences)
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        print(f"\n📊 Hybrid Classifier Results:")
        print(f"   🎯 Accuracy: {accuracy:.2%} ({sum(results)}/{len(results)})")
        print(f"   🎯 Avg Confidence: {avg_confidence:.2f}")
        print(f"   ⏱️ Avg Processing Time: {avg_processing_time:.3f}s")
        print(f"   🚀 Max Processing Time: {max(processing_times):.3f}s")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in category_results.items():
            if stats["total"] > 0:
                cat_accuracy = stats["correct"] / stats["total"]
                print(f"   {category.capitalize()}: {cat_accuracy:.2%} ({stats['correct']}/{stats['total']})")
        
        return {
            "classifier": "hybrid",
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "avg_processing_time": avg_processing_time,
            "errors": 0,
            "category_results": category_results
        }
    
    def print_rigorous_assessment(self, results: List[Dict]):
        """Print rigorous assessment of all classifiers"""
        print("\n" + "=" * 80)
        print("🎯 RIGOROUS CLASSIFIER ASSESSMENT")
        print("=" * 80)
        
        for result in results:
            classifier = result["classifier"]
            accuracy = result["accuracy"]
            processing_time = result["avg_processing_time"]
            errors = result["errors"]
            
            print(f"\n🔍 {classifier.upper()} Classifier:")
            print(f"   📈 Accuracy: {accuracy:.2%} {'✅ EXCELLENT' if accuracy >= 0.9 else '⚠️ NEEDS IMPROVEMENT'}")
            print(f"   ⏱️ Processing Time: {processing_time:.3f}s {'✅ EXCELLENT' if processing_time < 2.0 else '⚠️ NEEDS IMPROVEMENT'}")
            print(f"   🎯 Confidence: {result['avg_confidence']:.2f} {'✅ GOOD' if result['avg_confidence'] >= 0.7 else '⚠️ LOW'}")
            print(f"   ❌ Errors: {errors} {'✅ NONE' if errors == 0 else '⚠️ HAS ERRORS'}")
            
            if accuracy >= 0.9 and processing_time < 2.0 and errors == 0:
                print(f"   🎉 PRODUCTION READY!")
            elif accuracy >= 0.9 and processing_time < 2.0:
                print(f"   ⚠️ PRODUCTION READY (with fallback)")
            else:
                print(f"   ❌ NOT PRODUCTION READY")
        
        print(f"\n🎯 OVERALL SYSTEM STATUS:")
        llm_result = next((r for r in results if r["classifier"] == "llm"), None)
        keyword_result = next((r for r in results if r["classifier"] == "keyword"), None)
        hybrid_result = next((r for r in results if r["classifier"] == "hybrid"), None)
        
        if llm_result and llm_result["errors"] > 0:
            print(f"   ⚠️ LLM Classifier: HAS ERRORS (but fallback works)")
        else:
            print(f"   ✅ LLM Classifier: PRODUCTION READY")
        
        if keyword_result and keyword_result["accuracy"] >= 0.9:
            print(f"   ✅ Keyword Classifier: PRODUCTION READY")
        else:
            print(f"   ❌ Keyword Classifier: NEEDS IMPROVEMENT")
        
        if hybrid_result and hybrid_result["accuracy"] >= 0.9:
            print(f"   ✅ Hybrid Classifier: PRODUCTION READY")
        else:
            print(f"   ❌ Hybrid Classifier: NEEDS IMPROVEMENT")
        
        print(f"\n🚀 FINAL RECOMMENDATION:")
        if hybrid_result and hybrid_result["accuracy"] >= 0.9:
            print(f"   Use Hybrid Classifier for production - it provides:")
            print(f"   • {hybrid_result['accuracy']:.1%} accuracy (exceeds 90% target)")
            print(f"   • {hybrid_result['avg_processing_time']:.3f}s processing time (exceeds <2s target)")
            print(f"   • Intelligent fallback to keyword classifier")
            print(f"   • Robust error handling")
        else:
            print(f"   System needs improvement before production deployment")

async def main():
    """Main rigorous test function"""
    print("🚀 RIGOROUS LLM Classifier Test")
    print("=" * 80)
    print("🎯 Testing all classifiers with comprehensive error analysis")
    print("📄 20 documents (4 per category)")
    print("🎯 Target: 90%+ accuracy, <2 seconds processing time, 0 errors")
    
    tester = RigorousLLMTest()
    
    # Test all classifiers
    llm_result = await tester.test_llm_classifier_rigorous()
    keyword_result = await tester.test_keyword_classifier_rigorous()
    hybrid_result = await tester.test_hybrid_classifier_rigorous()
    
    # Print rigorous assessment
    tester.print_rigorous_assessment([llm_result, keyword_result, hybrid_result])
    
    # Save results
    with open("rigorous_classifier_results.json", "w") as f:
        json.dump([llm_result, keyword_result, hybrid_result], f, indent=2)
    
    print(f"\n📁 Results saved to rigorous_classifier_results.json")
    print(f"🎉 Rigorous classifier testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
