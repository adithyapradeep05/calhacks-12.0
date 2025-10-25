#!/usr/bin/env python3
"""
Create a test PDF file for RAGFlow testing.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_test_pdf():
    """Create a test PDF file."""
    filename = "test-document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    
    # Content
    content = [
        Paragraph("RAGFlow: Advanced Document Processing System", title_style),
        Spacer(1, 12),
        
        Paragraph("Overview", styles['Heading2']),
        Paragraph("RAGFlow is a cutting-edge document processing system that combines the power of vector databases with large language models to create an intelligent document search and question-answering platform.", styles['Normal']),
        Spacer(1, 12),
        
        Paragraph("Key Features", styles['Heading2']),
        Paragraph("• Vector-based document search using OpenAI embeddings", styles['Normal']),
        Paragraph("• Intelligent text chunking with overlap for better context", styles['Normal']),
        Paragraph("• Deduplication to prevent redundant content", styles['Normal']),
        Paragraph("• Caching system for faster processing", styles['Normal']),
        Paragraph("• MMR (Maximum Marginal Relevance) reranking for diverse results", styles['Normal']),
        Paragraph("• Support for PDF, TXT, and Markdown files", styles['Normal']),
        Paragraph("• Real-time chat interface for document queries", styles['Normal']),
        Spacer(1, 12),
        
        Paragraph("Technical Architecture", styles['Heading2']),
        Paragraph("The system uses ChromaDB as the vector database, OpenAI's text-embedding-3-small model for generating embeddings, and Claude for generating human-like responses. Documents are automatically chunked into manageable pieces with configurable overlap to maintain context across boundaries.", styles['Normal']),
        Spacer(1, 12),
        
        Paragraph("Use Cases", styles['Heading2']),
        Paragraph("• Research document analysis", styles['Normal']),
        Paragraph("• Knowledge base management", styles['Normal']),
        Paragraph("• Customer support automation", styles['Normal']),
        Paragraph("• Educational content processing", styles['Normal']),
        Paragraph("• Legal document review", styles['Normal']),
        Paragraph("• Technical documentation search", styles['Normal']),
        Spacer(1, 12),
        
        Paragraph("Conclusion", styles['Heading2']),
        Paragraph("The system is designed to handle large documents efficiently while maintaining high accuracy in retrieval and generation tasks.", styles['Normal']),
    ]
    
    doc.build(content)
    print(f"Created {filename}")
    return filename

if __name__ == "__main__":
    create_test_pdf()
