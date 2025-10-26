#!/usr/bin/env python3
"""
RAGFlow Demo Script
Automated demonstration of the RAGFlow system capabilities
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict, Any
from pathlib import Path

class RAGFlowDemo:
    """Automated demo script for RAGFlow system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.demo_documents = self._create_demo_documents()
        self.demo_queries = self._create_demo_queries()
    
    def _create_demo_documents(self) -> List[Dict[str, Any]]:
        """Create demo documents for each category"""
        return [
            # Legal Documents
            {
                "filename": "software_license_agreement.pdf",
                "content": """SOFTWARE LICENSE AGREEMENT

This Software License Agreement ("Agreement") is entered into between TechCorp Inc. ("Licensor") and the end user ("Licensee").

1. GRANT OF LICENSE
Subject to the terms and conditions of this Agreement, Licensor hereby grants to Licensee a non-exclusive, non-transferable license to use the Software.

2. RESTRICTIONS
Licensee shall not: (a) reverse engineer, decompile, or disassemble the Software; (b) distribute, sublicense, or transfer the Software to third parties; (c) modify or create derivative works of the Software.

3. TERMINATION
This Agreement shall terminate automatically if Licensee breaches any of its terms. Upon termination, Licensee must cease all use of the Software and destroy all copies.

4. WARRANTY DISCLAIMER
THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

5. LIMITATION OF LIABILITY
IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES.""",
                "category": "legal"
            },
            {
                "filename": "privacy_policy.pdf",
                "content": """PRIVACY POLICY

Last Updated: January 2024

1. INFORMATION WE COLLECT
We collect information you provide directly to us, such as when you create an account, use our services, or contact us for support.

2. HOW WE USE YOUR INFORMATION
We use the information we collect to: (a) provide, maintain, and improve our services; (b) process transactions and send related information; (c) send technical notices and support messages.

3. INFORMATION SHARING
We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.

4. DATA SECURITY
We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.

5. YOUR RIGHTS
You have the right to access, update, or delete your personal information. You may also opt out of certain communications from us.""",
                "category": "legal"
            },
            {
                "filename": "terms_of_service.pdf",
                "content": """TERMS OF SERVICE

1. ACCEPTANCE OF TERMS
By accessing and using our services, you accept and agree to be bound by the terms and provision of this agreement.

2. USE LICENSE
Permission is granted to temporarily download one copy of the materials on our website for personal, non-commercial transitory viewing only.

3. DISCLAIMER
The materials on our website are provided on an 'as is' basis. We make no warranties, expressed or implied, and hereby disclaim all other warranties.

4. LIMITATIONS
In no event shall our company or its suppliers be liable for any damages arising out of the use or inability to use the materials on our website.

5. ACCURACY OF MATERIALS
The materials appearing on our website could include technical, typographical, or photographic errors.""",
                "category": "legal"
            },
            {
                "filename": "nda_contract.pdf",
                "content": """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into between the parties for the purpose of protecting confidential information.

1. DEFINITION OF CONFIDENTIAL INFORMATION
Confidential Information means all non-public, proprietary, or confidential information disclosed by one party to the other.

2. OBLIGATIONS
The receiving party agrees to: (a) hold and maintain the Confidential Information in strict confidence; (b) not disclose the Confidential Information to any third parties; (c) use the Confidential Information solely for the purpose of evaluating potential business opportunities.

3. EXCEPTIONS
The obligations of confidentiality shall not apply to information that: (a) is or becomes publicly available; (b) was known to the receiving party prior to disclosure; (c) is independently developed by the receiving party.

4. TERM
This Agreement shall remain in effect for a period of five (5) years from the date of execution.

5. RETURN OF INFORMATION
Upon termination of this Agreement, the receiving party shall return all Confidential Information to the disclosing party.""",
                "category": "legal"
            },
            
            # Technical Documents
            {
                "filename": "api_documentation.md",
                "content": """# API Documentation

## Authentication
All API requests require authentication using a Bearer token in the Authorization header.

```bash
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

### GET /api/v1/users
Retrieve a list of users.

**Parameters:**
- `page` (optional): Page number for pagination
- `limit` (optional): Number of users per page (max 100)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

### POST /api/v1/users
Create a new user.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword"
}
```

## Rate Limiting
API requests are limited to 1000 requests per hour per API key.

## Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error""",
                "category": "technical"
            },
            {
                "filename": "system_architecture.pdf",
                "content": """SYSTEM ARCHITECTURE OVERVIEW

1. MICROSERVICES ARCHITECTURE
Our system is built using a microservices architecture with the following components:
- API Gateway: Handles routing and authentication
- User Service: Manages user accounts and authentication
- Document Service: Handles document processing and storage
- Search Service: Provides search and retrieval capabilities
- Notification Service: Manages notifications and alerts

2. DATABASE DESIGN
- Primary Database: PostgreSQL for transactional data
- Search Database: Elasticsearch for full-text search
- Cache Layer: Redis for session management and caching
- File Storage: AWS S3 for document storage

3. SECURITY MEASURES
- JWT-based authentication
- Role-based access control (RBAC)
- Data encryption at rest and in transit
- Regular security audits and penetration testing

4. SCALABILITY CONSIDERATIONS
- Horizontal scaling with load balancers
- Auto-scaling based on CPU and memory usage
- Database read replicas for improved performance
- CDN integration for static content delivery

5. MONITORING AND LOGGING
- Application performance monitoring (APM)
- Centralized logging with ELK stack
- Real-time alerting for critical issues
- Health checks and uptime monitoring""",
                "category": "technical"
            },
            {
                "filename": "deployment_guide.md",
                "content": """# Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Kubernetes cluster (for production)
- SSL certificates for HTTPS
- Domain name configured

## Development Deployment

1. Clone the repository
```bash
git clone https://github.com/company/ragflow.git
cd ragflow
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services
```bash
docker-compose up -d
```

4. Verify deployment
```bash
curl http://localhost:8000/health
```

## Production Deployment

1. Build production images
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Deploy to Kubernetes
```bash
kubectl apply -f k8s/
```

3. Configure ingress
```bash
kubectl apply -f k8s/ingress.yaml
```

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `API_KEY`: API key for external services

## Health Checks
- `/health`: Basic health check
- `/health/detailed`: Detailed system status
- `/metrics`: Prometheus metrics endpoint""",
                "category": "technical"
            },
            {
                "filename": "code_review_guidelines.md",
                "content": """# Code Review Guidelines

## General Principles
- All code changes must be reviewed before merging
- Reviews should be constructive and educational
- Focus on code quality, security, and maintainability

## Review Checklist

### Code Quality
- [ ] Code follows established style guidelines
- [ ] Functions and classes are well-documented
- [ ] No code duplication
- [ ] Proper error handling implemented
- [ ] Unit tests written and passing

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection measures
- [ ] Authentication and authorization checks

### Performance
- [ ] No obvious performance bottlenecks
- [ ] Database queries optimized
- [ ] Caching implemented where appropriate
- [ ] Memory leaks prevented
- [ ] Resource cleanup handled

## Review Process
1. Create feature branch from main
2. Implement changes with tests
3. Create pull request with description
4. Request review from team members
5. Address feedback and make changes
6. Merge after approval

## Best Practices
- Keep pull requests small and focused
- Write clear commit messages
- Include tests for new functionality
- Update documentation as needed
- Consider backward compatibility""",
                "category": "technical"
            },
            
            # Financial Documents
            {
                "filename": "q3_financial_report.pdf",
                "content": """Q3 2024 FINANCIAL REPORT

EXECUTIVE SUMMARY
Q3 2024 showed strong financial performance with revenue growth of 15% compared to Q2 2024.

REVENUE ANALYSIS
- Total Revenue: $2,350,000 (up 15% from Q2)
- Subscription Revenue: $1,800,000 (77% of total)
- Professional Services: $550,000 (23% of total)

EXPENSE BREAKDOWN
- Cost of Goods Sold: $450,000
- Sales & Marketing: $680,000
- Research & Development: $420,000
- General & Administrative: $250,000
- Total Operating Expenses: $1,800,000

PROFITABILITY METRICS
- Gross Profit: $1,900,000 (81% margin)
- Operating Income: $550,000 (23% margin)
- Net Income: $420,000 (18% margin)
- EBITDA: $620,000

CASH FLOW
- Operating Cash Flow: $580,000
- Investing Cash Flow: -$120,000
- Financing Cash Flow: $50,000
- Net Cash Change: $510,000

BALANCE SHEET HIGHLIGHTS
- Total Assets: $8,500,000
- Total Liabilities: $2,100,000
- Shareholders' Equity: $6,400,000
- Cash and Equivalents: $2,200,000""",
                "category": "financial"
            },
            {
                "filename": "budget_proposal_2025.pdf",
                "content": """2025 BUDGET PROPOSAL

OVERVIEW
This budget proposal outlines the financial plan for 2025, focusing on growth initiatives and operational efficiency.

REVENUE PROJECTIONS
- Q1 2025: $2,500,000
- Q2 2025: $2,750,000
- Q3 2025: $3,000,000
- Q4 2025: $3,250,000
- Total 2025: $11,500,000

EXPENSE ALLOCATION
- Personnel Costs: $4,600,000 (40%)
- Technology Infrastructure: $1,725,000 (15%)
- Marketing & Sales: $2,300,000 (20%)
- Research & Development: $1,725,000 (15%)
- Operations: $1,150,000 (10%)

INVESTMENT PRIORITIES
1. Product Development: $2,000,000
   - New feature development
   - Platform scalability improvements
   - Security enhancements

2. Market Expansion: $1,500,000
   - International market entry
   - Partnership development
   - Brand awareness campaigns

3. Talent Acquisition: $1,000,000
   - Engineering team expansion
   - Sales team growth
   - Leadership development

RISK FACTORS
- Economic uncertainty
- Competitive pressure
- Technology changes
- Regulatory compliance

CONTINGENCY PLANNING
- 10% contingency fund: $1,150,000
- Emergency reserves: $500,000
- Flexible budget allocation for priority shifts""",
                "category": "financial"
            },
            {
                "filename": "invoice_001.pdf",
                "content": """INVOICE

Invoice Number: INV-2024-001
Date: January 15, 2024
Due Date: February 14, 2024

BILL TO:
ABC Corporation
123 Business Street
New York, NY 10001

FROM:
TechCorp Inc.
456 Tech Avenue
San Francisco, CA 94105

DESCRIPTION OF SERVICES:
- Software License (Annual): $50,000
- Professional Services (100 hours @ $150/hour): $15,000
- Implementation Support: $5,000
- Training Services: $3,000

SUBTOTAL: $73,000
TAX (8.5%): $6,205
TOTAL: $79,205

PAYMENT TERMS:
Net 30 days. Late payments subject to 1.5% monthly service charge.

PAYMENT METHODS:
- Bank Transfer: Account details provided separately
- Check: Payable to TechCorp Inc.
- Credit Card: 2.9% processing fee applies

Thank you for your business!""",
                "category": "financial"
            },
            {
                "filename": "portfolio_analysis.pdf",
                "content": """INVESTMENT PORTFOLIO ANALYSIS

PORTFOLIO OVERVIEW
Total Portfolio Value: $5,000,000
Asset Allocation: 60% Stocks, 30% Bonds, 10% Alternatives

EQUITY HOLDINGS (60% - $3,000,000)
- Technology Sector: 40% ($1,200,000)
  - Apple Inc.: $300,000
  - Microsoft Corp.: $250,000
  - Google (Alphabet): $200,000
  - Amazon.com: $180,000
  - Other Tech: $270,000

- Healthcare Sector: 20% ($600,000)
  - Johnson & Johnson: $150,000
  - Pfizer Inc.: $120,000
  - UnitedHealth Group: $100,000
  - Other Healthcare: $230,000

- Financial Sector: 15% ($450,000)
- Consumer Discretionary: 15% ($450,000)
- Other Sectors: 10% ($300,000)

FIXED INCOME (30% - $1,500,000)
- Government Bonds: 50% ($750,000)
- Corporate Bonds: 30% ($450,000)
- Municipal Bonds: 20% ($300,000)

ALTERNATIVE INVESTMENTS (10% - $500,000)
- Real Estate Investment Trusts: 60% ($300,000)
- Commodities: 25% ($125,000)
- Private Equity: 15% ($75,000)

PERFORMANCE METRICS
- YTD Return: 8.5%
- 1-Year Return: 12.3%
- 3-Year Annualized: 9.8%
- 5-Year Annualized: 11.2%
- Sharpe Ratio: 1.45
- Beta: 1.12

RISK ANALYSIS
- Portfolio Volatility: 15.2%
- Maximum Drawdown: -8.5%
- Value at Risk (95%): -$250,000""",
                "category": "financial"
            },
            
            # HR Documents
            {
                "filename": "employee_handbook.pdf",
                "content": """EMPLOYEE HANDBOOK

WELCOME TO TECHCORP
We're excited to have you join our team! This handbook provides important information about our company policies, benefits, and procedures.

WORKPLACE POLICIES
- Work Hours: 9:00 AM - 5:00 PM, Monday through Friday
- Remote Work: Up to 3 days per week with manager approval
- Dress Code: Business casual, professional attire for client meetings
- Code of Conduct: Treat all colleagues with respect and professionalism

COMPENSATION & BENEFITS
- Salary: Competitive market rates with annual reviews
- Health Insurance: Company covers 80% of premiums
- Dental & Vision: Company covers 70% of premiums
- 401(k): Company matches up to 6% of salary
- Paid Time Off: 15 days annually, increasing with tenure
- Sick Leave: 10 days annually
- Parental Leave: 12 weeks paid leave for new parents

PERFORMANCE MANAGEMENT
- Annual Performance Reviews: Conducted in December
- 360-Degree Feedback: Quarterly peer reviews
- Goal Setting: SMART goals set annually
- Career Development: Individual development plans
- Mentorship Program: Available for all employees

LEAVE POLICIES
- Vacation: Must be requested 2 weeks in advance
- Sick Leave: Can be used for illness or medical appointments
- Personal Leave: Up to 5 days annually for personal matters
- Bereavement Leave: 3 days for immediate family
- Jury Duty: Paid time off for jury service

WORKPLACE SAFETY
- Safety Training: Required for all employees
- Emergency Procedures: Posted in all work areas
- Incident Reporting: All incidents must be reported immediately
- Health & Wellness: Employee assistance program available""",
                "category": "hr"
            },
            {
                "filename": "job_description_senior_engineer.pdf",
                "content": """JOB DESCRIPTION - SENIOR SOFTWARE ENGINEER

POSITION OVERVIEW
We are seeking a Senior Software Engineer to join our development team. The ideal candidate will have 5+ years of experience in full-stack development and a passion for building scalable applications.

RESPONSIBILITIES
- Design and develop high-quality software solutions
- Collaborate with cross-functional teams to define requirements
- Mentor junior developers and conduct code reviews
- Participate in architecture decisions and technical planning
- Ensure code quality through testing and best practices
- Troubleshoot and debug production issues
- Stay current with industry trends and technologies

REQUIRED QUALIFICATIONS
- Bachelor's degree in Computer Science or related field
- 5+ years of software development experience
- Proficiency in Python, JavaScript, and SQL
- Experience with cloud platforms (AWS, Azure, or GCP)
- Knowledge of microservices architecture
- Strong problem-solving and communication skills
- Experience with version control (Git)

PREFERRED QUALIFICATIONS
- Master's degree in Computer Science
- Experience with containerization (Docker, Kubernetes)
- Knowledge of machine learning and AI
- Previous experience in fintech or healthcare
- Open source contributions
- Leadership experience

COMPENSATION & BENEFITS
- Salary Range: $120,000 - $160,000
- Equity participation
- Comprehensive health benefits
- Professional development budget
- Flexible work arrangements
- Generous vacation policy

APPLICATION PROCESS
1. Submit resume and cover letter
2. Technical phone screening
3. Coding challenge
4. On-site interview (4-5 hours)
5. Reference checks
6. Offer decision

Equal Opportunity Employer: We are committed to diversity and inclusion.""",
                "category": "hr"
            },
            {
                "filename": "performance_review_template.pdf",
                "content": """PERFORMANCE REVIEW TEMPLATE

EMPLOYEE INFORMATION
Name: [Employee Name]
Position: [Job Title]
Department: [Department]
Review Period: [Start Date] to [End Date]
Reviewer: [Manager Name]

PERFORMANCE RATING SCALE
5 - Exceeds Expectations
4 - Meets Expectations
3 - Partially Meets Expectations
2 - Below Expectations
1 - Significantly Below Expectations

GOAL ACHIEVEMENT
Rate achievement of previously set goals:
- Goal 1: [Description] - Rating: [1-5]
- Goal 2: [Description] - Rating: [1-5]
- Goal 3: [Description] - Rating: [1-5]

CORE COMPETENCIES
- Technical Skills: [1-5] - Comments: [Feedback]
- Communication: [1-5] - Comments: [Feedback]
- Teamwork: [1-5] - Comments: [Feedback]
- Problem Solving: [1-5] - Comments: [Feedback]
- Leadership: [1-5] - Comments: [Feedback]
- Initiative: [1-5] - Comments: [Feedback]

ACHIEVEMENTS & ACCOMPLISHMENTS
List key achievements during the review period:
1. [Achievement 1]
2. [Achievement 2]
3. [Achievement 3]

AREAS FOR IMPROVEMENT
Identify areas where the employee can improve:
1. [Area 1] - Action Plan: [Specific steps]
2. [Area 2] - Action Plan: [Specific steps]

DEVELOPMENT PLAN
- Short-term goals (next 6 months): [Goals]
- Long-term goals (next 12 months): [Goals]
- Training needs: [Training requirements]
- Career aspirations: [Employee's career goals]

OVERALL PERFORMANCE RATING: [1-5]
SUMMARY: [Overall assessment and recommendations]

EMPLOYEE COMMENTS: [Space for employee feedback]

SIGNATURES
Employee: [Signature] Date: [Date]
Manager: [Signature] Date: [Date]
HR Representative: [Signature] Date: [Date]""",
                "category": "hr"
            },
            {
                "filename": "leadership_training_program.pdf",
                "content": """LEADERSHIP TRAINING PROGRAM

PROGRAM OVERVIEW
Our Leadership Training Program is designed to develop the next generation of leaders within our organization. The program combines theoretical learning with practical application.

PROGRAM OBJECTIVES
- Develop essential leadership skills
- Build emotional intelligence and self-awareness
- Enhance communication and influence abilities
- Foster strategic thinking and decision-making
- Create a network of future leaders

CURRICULUM MODULES

Module 1: Leadership Fundamentals (Week 1-2)
- Leadership styles and approaches
- Emotional intelligence assessment
- Self-awareness and reflection
- Values-based leadership

Module 2: Communication & Influence (Week 3-4)
- Effective communication strategies
- Active listening techniques
- Conflict resolution skills
- Building trust and rapport

Module 3: Strategic Thinking (Week 5-6)
- Systems thinking and analysis
- Decision-making frameworks
- Change management principles
- Innovation and creativity

Module 4: Team Building (Week 7-8)
- Team dynamics and development
- Motivation and engagement
- Performance management
- Diversity and inclusion

Module 5: Business Acumen (Week 9-10)
- Financial literacy
- Market analysis
- Customer focus
- Operational excellence

DELIVERY METHODS
- Interactive workshops: 40%
- Case studies and simulations: 30%
- Mentorship and coaching: 20%
- Self-directed learning: 10%

ASSESSMENT & EVALUATION
- Pre and post-program assessments
- 360-degree feedback
- Project presentations
- Peer evaluations
- Manager feedback

PROGRAM REQUIREMENTS
- Minimum 2 years of experience
- Manager recommendation
- Commitment to full program participation
- Completion of all assignments and projects

BENEFITS OF PARTICIPATION
- Enhanced leadership capabilities
- Increased career opportunities
- Expanded professional network
- Personal development and growth
- Recognition and certification

APPLICATION PROCESS
1. Manager nomination
2. Application submission
3. Interview with program director
4. Selection committee review
5. Program acceptance notification

PROGRAM DURATION: 10 weeks
COHORT SIZE: 12-15 participants
FREQUENCY: Quarterly cohorts""",
                "category": "hr"
            },
            
            # General Documents
            {
                "filename": "meeting_notes_standup.txt",
                "content": """DAILY STANDUP MEETING NOTES

Date: January 15, 2024
Time: 9:00 AM - 9:15 AM
Attendees: John, Sarah, Mike, Lisa, David

AGENDA ITEMS

1. YESTERDAY'S ACCOMPLISHMENTS
- John: Completed user authentication module, fixed login bug
- Sarah: Finished API documentation for user endpoints
- Mike: Implemented caching layer for search functionality
- Lisa: Updated frontend components for new design
- David: Deployed staging environment updates

2. TODAY'S PLANNED WORK
- John: Start working on password reset functionality
- Sarah: Begin integration testing for user management
- Mike: Optimize database queries for better performance
- Lisa: Implement responsive design for mobile devices
- David: Set up monitoring alerts for production

3. BLOCKERS AND ISSUES
- Sarah: Waiting for API key from third-party service
- Mike: Need clarification on caching requirements
- Lisa: Design assets not yet available from design team

4. ACTION ITEMS
- David: Follow up with third-party service for API key
- Mike: Schedule meeting with product team for caching requirements
- Lisa: Check with design team on asset delivery timeline

5. NOTES
- Code review session scheduled for 2:00 PM
- Sprint planning meeting moved to Friday
- Team lunch scheduled for next Tuesday

NEXT STANDUP: Tomorrow at 9:00 AM""",
                "category": "general"
            },
            {
                "filename": "newsletter_december_2024.pdf",
                "content": """COMPANY NEWSLETTER - DECEMBER 2024

HOLIDAY GREETINGS
As we approach the end of another successful year, we want to thank all our employees for their dedication and hard work. Happy holidays and best wishes for the new year!

COMPANY HIGHLIGHTS
- Q4 revenue exceeded targets by 12%
- Launched new product line with great customer response
- Expanded team with 15 new hires across all departments
- Achieved ISO 27001 certification for information security

EMPLOYEE SPOTLIGHT
This month we're featuring Sarah Johnson from the Engineering team. Sarah led the development of our new mobile application, which has received excellent user feedback. Congratulations, Sarah!

UPCOMING EVENTS
- December 20: Company holiday party at the Grand Ballroom
- December 24-26: Office closed for Christmas holiday
- January 2: Office reopens for the new year
- January 15: All-hands meeting to discuss 2025 goals

BENEFITS UPDATES
- Health insurance premiums will remain the same in 2025
- New wellness program launching in January
- 401(k) matching increased to 6%
- Additional paid time off for volunteer work

TECHNOLOGY UPDATES
- New laptops for all employees in Q1 2025
- Upgraded office Wi-Fi network
- New collaboration tools being rolled out
- Enhanced security measures implemented

RECOGNITION & AWARDS
- Employee of the Month: Mike Chen (Sales)
- Team Excellence Award: Customer Support Team
- Innovation Award: Product Development Team
- Safety Award: Facilities Team

SOCIAL EVENTS
- Monthly happy hours continue in the new year
- Book club meeting January 10th
- Fitness challenge starting January 15th
- Volunteer day at local food bank January 20th

THANK YOU
We appreciate everyone's contributions to making this year successful. Looking forward to an even better 2025!""",
                "category": "general"
            },
            {
                "filename": "project_status_update.pdf",
                "content": """PROJECT STATUS UPDATE

Project: Customer Portal Redesign
Project Manager: Jennifer Smith
Date: January 15, 2024
Status: On Track

EXECUTIVE SUMMARY
The Customer Portal Redesign project is progressing well with all major milestones on schedule. The team has successfully completed the design phase and is now in the development phase.

PROJECT TIMELINE
- Project Start: October 1, 2024
- Design Phase: October 1 - November 15, 2024 ✅
- Development Phase: November 16, 2024 - February 28, 2025 🔄
- Testing Phase: March 1 - March 31, 2025
- Launch: April 1, 2025

COMPLETED DELIVERABLES
- User research and requirements gathering
- Wireframes and mockups
- Design system and style guide
- Technical architecture document
- Development environment setup

CURRENT WORK IN PROGRESS
- Frontend component development (60% complete)
- Backend API development (45% complete)
- Database schema updates (80% complete)
- Integration with existing systems (30% complete)

UPCOMING MILESTONES
- January 31: Complete frontend components
- February 15: Complete backend APIs
- February 28: Complete integration work
- March 15: Begin user acceptance testing

RISKS AND ISSUES
- Risk: Third-party API integration delays
  Mitigation: Working with vendor to expedite access
- Issue: Resource availability for testing phase
  Mitigation: Cross-training team members on testing procedures

BUDGET STATUS
- Total Budget: $500,000
- Spent to Date: $180,000 (36%)
- Remaining: $320,000
- Projected Final Cost: $485,000 (under budget)

TEAM UPDATES
- Added 2 additional developers to accelerate development
- UX designer completed work and moved to next project
- QA engineer will join team in February for testing phase

NEXT STEPS
1. Complete remaining frontend components
2. Finalize backend API development
3. Begin integration testing
4. Prepare for user acceptance testing phase

STAKEHOLDER COMMUNICATION
- Weekly status meetings with executive team
- Bi-weekly updates to customer advisory board
- Monthly progress reports to board of directors""",
                "category": "general"
            },
            {
                "filename": "office_announcement.txt",
                "content": """OFFICE ANNOUNCEMENT

Subject: New Office Policies and Procedures

Dear Team,

We're excited to share some important updates about our office policies and procedures that will take effect starting February 1, 2024.

NEW POLICIES

1. FLEXIBLE WORK ARRANGEMENTS
- Remote work: Up to 3 days per week with manager approval
- Core hours: 10:00 AM - 3:00 PM for team collaboration
- Flexible start/end times: 7:00 AM - 6:00 PM window

2. MEETING ROOM BOOKING
- All meeting rooms must be booked through the calendar system
- Maximum booking time: 2 hours per session
- Clean up after meetings and return furniture to original positions

3. KITCHEN AND COMMON AREAS
- Clean up after yourself in the kitchen
- Label personal food items in the refrigerator
- Report any maintenance issues to facilities@company.com

4. PARKING
- Employee parking is available in the garage
- Visitor parking is limited to 2 hours
- Carpooling is encouraged and rewarded with preferred parking

5. SECURITY
- All visitors must be signed in at the front desk
- Badge access required for all office areas
- Report any security concerns immediately

UPCOMING CHANGES

- New coffee machine installation: January 25
- Office furniture refresh: February 15-20
- Network upgrade: February 22 (after hours)
- Emergency evacuation drill: February 28

QUESTIONS AND FEEDBACK

If you have any questions about these new policies or suggestions for improvements, please contact HR at hr@company.com or stop by the HR office.

Thank you for your cooperation and for helping us maintain a great work environment!

Best regards,
The Management Team""",
                "category": "general"
            }
        ]
    
    def _create_demo_queries(self) -> List[Dict[str, Any]]:
        """Create demo queries for each category"""
        return [
            {
                "query": "What are the terms of the software license agreement?",
                "expected_category": "legal",
                "description": "Legal document query"
            },
            {
                "query": "How do I authenticate with the API?",
                "expected_category": "technical",
                "description": "Technical documentation query"
            },
            {
                "query": "What was the Q3 revenue?",
                "expected_category": "financial",
                "description": "Financial report query"
            },
            {
                "query": "What are the vacation policies?",
                "expected_category": "hr",
                "description": "HR policy query"
            },
            {
                "query": "What was discussed in the meeting?",
                "expected_category": "general",
                "description": "General document query"
            }
        ]
    
    async def run_demo(self):
        """Run the complete demo"""
        print("🚀 RAGFlow System Demo")
        print("=" * 50)
        
        # Step 1: Health Check
        print("\n1️⃣ System Health Check")
        await self._demo_health_check()
        
        # Step 2: Document Upload and Classification
        print("\n2️⃣ Document Upload and Classification")
        document_ids = await self._demo_document_upload()
        
        # Step 3: Document Embedding
        print("\n3️⃣ Document Embedding")
        await self._demo_document_embedding(document_ids)
        
        # Step 4: Query Processing
        print("\n4️⃣ Query Processing and Routing")
        await self._demo_query_processing()
        
        # Step 5: System Statistics
        print("\n5️⃣ System Statistics")
        await self._demo_system_statistics()
        
        # Step 6: Cache Performance
        print("\n6️⃣ Cache Performance")
        await self._demo_cache_performance()
        
        print("\n🎉 Demo Complete!")
        print("=" * 50)
    
    async def _demo_health_check(self):
        """Demo system health check"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ System is healthy!")
                    services = data.get("services", {})
                    for service, status in services.items():
                        print(f"   {service}: {status}")
                else:
                    print(f"❌ Health check failed: {response.status}")
    
    async def _demo_document_upload(self) -> List[str]:
        """Demo document upload and classification"""
        document_ids = []
        
        async with aiohttp.ClientSession() as session:
            for doc in self.demo_documents[:5]:  # Upload first 5 documents
                # Create temporary file
                temp_filename = f"temp_{doc['filename']}"
                with open(temp_filename, 'w') as f:
                    f.write(doc['content'])
                
                # Upload file
                with open(temp_filename, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=doc['filename'])
                    
                    async with session.post(f"{self.base_url}/upload", data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            document_id = result.get('document_id')
                            category = result.get('category')
                            confidence = result.get('confidence', 0)
                            
                            document_ids.append(document_id)
                            
                            print(f"✅ Uploaded {doc['filename']}")
                            print(f"   Category: {category} (confidence: {confidence:.2f})")
                            print(f"   Expected: {doc['category']}")
                            
                            # Check if classification is correct
                            if category == doc['category']:
                                print("   ✅ Classification correct!")
                            else:
                                print("   ⚠️ Classification mismatch")
                        else:
                            print(f"❌ Upload failed for {doc['filename']}: {response.status}")
                
                # Clean up temp file
                import os
                os.remove(temp_filename)
        
        return document_ids
    
    async def _demo_document_embedding(self, document_ids: List[str]):
        """Demo document embedding"""
        async with aiohttp.ClientSession() as session:
            for doc_id in document_ids:
                async with session.post(f"{self.base_url}/embed", json={
                    "document_id": doc_id,
                    "namespace": "default"
                }) as response:
                    if response.status == 200:
                        result = await response.json()
                        chunks = result.get('chunks_processed', 0)
                        category = result.get('category', 'unknown')
                        
                        print(f"✅ Embedded document {doc_id[:8]}...")
                        print(f"   Category: {category}")
                        print(f"   Chunks processed: {chunks}")
                    else:
                        print(f"❌ Embedding failed for {doc_id[:8]}...: {response.status}")
    
    async def _demo_query_processing(self):
        """Demo query processing and routing"""
        async with aiohttp.ClientSession() as session:
            for query_info in self.demo_queries:
                query = query_info['query']
                expected_category = query_info['expected_category']
                
                async with session.post(f"{self.base_url}/query", json={
                    "query": query,
                    "namespace": "default",
                    "max_results": 3
                }) as response:
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get('answer', '')
                        category = result.get('category', 'unknown')
                        sources = result.get('sources', 0)
                        processing_time = result.get('processing_time_ms', 0)
                        
                        print(f"✅ Query: {query}")
                        print(f"   Routed to: {category} (expected: {expected_category})")
                        print(f"   Sources found: {sources}")
                        print(f"   Processing time: {processing_time}ms")
                        print(f"   Answer: {answer[:100]}...")
                        
                        # Check if routing is correct
                        if category == expected_category:
                            print("   ✅ Routing correct!")
                        else:
                            print("   ⚠️ Routing mismatch")
                    else:
                        print(f"❌ Query failed: {response.status}")
    
    async def _demo_system_statistics(self):
        """Demo system statistics"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print("✅ System Statistics:")
                    print(f"   Total documents: {data.get('total_documents', 0)}")
                    print(f"   Total chunks: {data.get('total_chunks', 0)}")
                    
                    categories = data.get('categories', {})
                    print("   Categories:")
                    for category, count in categories.items():
                        print(f"     {category}: {count} documents")
                    
                    cache_stats = data.get('cache_stats', {})
                    if cache_stats:
                        print("   Cache Statistics:")
                        for level, stats in cache_stats.items():
                            hit_rate = stats.get('hit_rate', 0)
                            print(f"     {level}: {hit_rate:.2f} hit rate")
                else:
                    print(f"❌ Stats failed: {response.status}")
    
    async def _demo_cache_performance(self):
        """Demo cache performance"""
        async with aiohttp.ClientSession() as session:
            # First query (cache miss)
            start_time = time.time()
            async with session.post(f"{self.base_url}/query", json={
                "query": "What are the software license terms?",
                "namespace": "default"
            }) as response:
                first_duration = (time.time() - start_time) * 1000
            
            # Second query (cache hit)
            start_time = time.time()
            async with session.post(f"{self.base_url}/query", json={
                "query": "What are the software license terms?",
                "namespace": "default"
            }) as response:
                second_duration = (time.time() - start_time) * 1000
            
            print("✅ Cache Performance Test:")
            print(f"   First query (cache miss): {first_duration:.1f}ms")
            print(f"   Second query (cache hit): {second_duration:.1f}ms")
            
            if second_duration < first_duration:
                improvement = ((first_duration - second_duration) / first_duration) * 100
                print(f"   ✅ Cache improvement: {improvement:.1f}%")
            else:
                print("   ⚠️ No cache improvement detected")

async def main():
    """Main demo function"""
    demo = RAGFlowDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
