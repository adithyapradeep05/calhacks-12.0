#!/usr/bin/env python3
"""
Comprehensive Classifier Testing
Tests LLM, Keyword, and Hybrid classifiers with 20 documents (4 per category)
Target: 90%+ accuracy, <2 seconds processing time
"""

import asyncio
import time
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass

from llm_classifier import LLMClassifier, ClassificationResult as LLMResult
from keyword_classifier import KeywordClassifier, ClassificationResult as KeywordResult
from hybrid_classifier import HybridClassifier, ClassificationResult as HybridResult

@dataclass
class TestDocument:
    """Test document for classification"""
    content: str
    filename: str
    expected_category: str
    category_type: str  # "legal", "technical", "financial", "hr", "general"

@dataclass
class TestResult:
    """Result of classifier test"""
    classifier_name: str
    total_documents: int
    correct_predictions: int
    accuracy: float
    avg_confidence: float
    avg_processing_time: float
    category_results: Dict[str, Dict[str, int]]  # category -> {correct, total}
    processing_times: List[float]
    confidences: List[float]

class ClassifierTester:
    """Comprehensive classifier testing"""
    
    def __init__(self):
        self.test_documents = self._create_test_documents()
        self.llm_classifier = LLMClassifier()
        self.keyword_classifier = KeywordClassifier()
        self.hybrid_classifier = HybridClassifier()
    
    def _create_test_documents(self) -> List[TestDocument]:
        """Create 20 test documents (4 per category)"""
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
    
    async def test_llm_classifier(self) -> TestResult:
        """Test LLM classifier"""
        print("🔵 Testing LLM Classifier...")
        
        results = []
        processing_times = []
        confidences = []
        category_results = {cat: {"correct": 0, "total": 0} for cat in ["legal", "technical", "financial", "hr", "general"]}
        
        for doc in self.test_documents:
            start_time = time.time()
            result = await self.llm_classifier.classify(doc.content, doc.filename)
            processing_time = time.time() - start_time
            
            correct = result.category == doc.expected_category
            results.append(correct)
            processing_times.append(processing_time)
            confidences.append(result.confidence)
            
            category_results[doc.category_type]["total"] += 1
            if correct:
                category_results[doc.category_type]["correct"] += 1
        
        correct_predictions = sum(results)
        total_documents = len(results)
        accuracy = correct_predictions / total_documents
        avg_confidence = sum(confidences) / len(confidences)
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        return TestResult(
            classifier_name="LLM",
            total_documents=total_documents,
            correct_predictions=correct_predictions,
            accuracy=accuracy,
            avg_confidence=avg_confidence,
            avg_processing_time=avg_processing_time,
            category_results=category_results,
            processing_times=processing_times,
            confidences=confidences
        )
    
    def test_keyword_classifier(self) -> TestResult:
        """Test keyword classifier"""
        print("🔴 Testing Keyword Classifier...")
        
        results = []
        processing_times = []
        confidences = []
        category_results = {cat: {"correct": 0, "total": 0} for cat in ["legal", "technical", "financial", "hr", "general"]}
        
        for doc in self.test_documents:
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
        
        correct_predictions = sum(results)
        total_documents = len(results)
        accuracy = correct_predictions / total_documents
        avg_confidence = sum(confidences) / len(confidences)
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        return TestResult(
            classifier_name="Keyword",
            total_documents=total_documents,
            correct_predictions=correct_predictions,
            accuracy=accuracy,
            avg_confidence=avg_confidence,
            avg_processing_time=avg_processing_time,
            category_results=category_results,
            processing_times=processing_times,
            confidences=confidences
        )
    
    async def test_hybrid_classifier(self) -> TestResult:
        """Test hybrid classifier"""
        print("🟢 Testing Hybrid Classifier...")
        
        results = []
        processing_times = []
        confidences = []
        category_results = {cat: {"correct": 0, "total": 0} for cat in ["legal", "technical", "financial", "hr", "general"]}
        
        for doc in self.test_documents:
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
        
        correct_predictions = sum(results)
        total_documents = len(results)
        accuracy = correct_predictions / total_documents
        avg_confidence = sum(confidences) / len(confidences)
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        return TestResult(
            classifier_name="Hybrid",
            total_documents=total_documents,
            correct_predictions=correct_predictions,
            accuracy=accuracy,
            avg_confidence=avg_confidence,
            avg_processing_time=avg_processing_time,
            category_results=category_results,
            processing_times=processing_times,
            confidences=confidences
        )
    
    def print_test_results(self, results: List[TestResult]):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE CLASSIFIER TEST RESULTS")
        print("=" * 80)
        
        for result in results:
            print(f"\n🔍 {result.classifier_name} Classifier Results:")
            print(f"   📈 Accuracy: {result.accuracy:.2%} ({result.correct_predictions}/{result.total_documents})")
            print(f"   🎯 Avg Confidence: {result.avg_confidence:.2f}")
            print(f"   ⏱️ Avg Processing Time: {result.avg_processing_time:.3f}s")
            print(f"   🚀 Max Processing Time: {max(result.processing_times):.3f}s")
            print(f"   📊 Min Processing Time: {min(result.processing_times):.3f}s")
            
            print(f"\n   📋 Category Breakdown:")
            for category, stats in result.category_results.items():
                if stats["total"] > 0:
                    cat_accuracy = stats["correct"] / stats["total"]
                    print(f"      {category.capitalize()}: {cat_accuracy:.2%} ({stats['correct']}/{stats['total']})")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"   Target Accuracy: 90%+")
        print(f"   Target Processing Time: <2 seconds")
        
        for result in results:
            accuracy_ok = result.accuracy >= 0.9
            time_ok = result.avg_processing_time < 2.0
            
            print(f"\n   {result.classifier_name} Classifier:")
            print(f"      Accuracy: {'✅ ACHIEVED' if accuracy_ok else '❌ BELOW TARGET'} ({result.accuracy:.2%})")
            print(f"      Processing Time: {'✅ ACHIEVED' if time_ok else '❌ ABOVE TARGET'} ({result.avg_processing_time:.3f}s)")
            
            if accuracy_ok and time_ok:
                print(f"      🎉 ALL TARGETS MET!")
            else:
                print(f"      ⚠️ NEEDS IMPROVEMENT")
    
    async def run_comprehensive_test(self):
        """Run comprehensive classifier testing"""
        print("🚀 Starting Comprehensive Classifier Testing")
        print("=" * 80)
        print(f"📄 Testing with {len(self.test_documents)} documents (4 per category)")
        print(f"🎯 Target: 90%+ accuracy, <2 seconds processing time")
        
        # Test all classifiers
        results = []
        
        # Test LLM classifier
        if self.llm_classifier.is_available():
            llm_result = await self.test_llm_classifier()
            results.append(llm_result)
        else:
            print("⚠️ LLM Classifier not available (missing API keys)")
        
        # Test keyword classifier
        keyword_result = self.test_keyword_classifier()
        results.append(keyword_result)
        
        # Test hybrid classifier
        hybrid_result = await self.test_hybrid_classifier()
        results.append(hybrid_result)
        
        # Print results
        self.print_test_results(results)
        
        return results

# Main test function
async def main():
    """Main test function"""
    tester = ClassifierTester()
    results = await tester.run_comprehensive_test()
    
    print("\n🎉 Comprehensive classifier testing completed!")
    
    # Save results to file
    with open("classifier_test_results.json", "w") as f:
        json.dump([{
            "classifier_name": r.classifier_name,
            "accuracy": r.accuracy,
            "avg_confidence": r.avg_confidence,
            "avg_processing_time": r.avg_processing_time,
            "category_results": r.category_results
        } for r in results], f, indent=2)
    
    print("📁 Results saved to classifier_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
