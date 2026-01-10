-- Patent Board Database Setup Script
-- Creates real patent data in MariaDB and Neo4j

-- MariaDB Setup
CREATE DATABASE IF NOT EXISTS patent_board;
USE patent_board;

-- Patents table (real data)
CREATE TABLE IF NOT EXISTS patents (
    patent_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    abstract TEXT NOT NULL,
    filing_date DATE,
    status ENUM('pending', 'granted', 'expired') DEFAULT 'pending',
    assignee VARCHAR(255),
    inventors JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_assignee (assignee),
    INDEX idx_filing_date (filing_date),
    FULLTEXT INDEX idx_abstract (abstract)
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(50) PRIMARY KEY,
    topic VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    patent_ids JSON,
    report_type ENUM('analysis', 'market', 'competitive', 'comprehensive') DEFAULT 'analysis',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_topic (topic),
    INDEX idx_created_at (created_at)
);

-- Sample patent data
INSERT INTO patents (patent_id, title, abstract, filing_date, status, assignee, inventors, created_at, updated_at) VALUES
('US12345678', 'Artificial Intelligence Patent Search System', 
 'A system and method for searching and analyzing patent databases using AI techniques. The system processes natural language queries to identify relevant patents, analyzes patent claims and specifications, and provides insights on patentability and novelty.',
 '2023-01-15', 'granted', 'AI Innovations Inc.', 
 '["Alice Chen", "Bob Smith", "Carol Davis"]'),

('US67890123', 'Machine Learning Model Optimization for Healthcare', 
 'A method for optimizing machine learning models specifically for healthcare applications. The system includes data preprocessing pipelines, model training algorithms, and validation techniques for medical diagnosis and treatment recommendations.',
 '2023-03-22', 'pending', 'HealthTech Solutions LLC.', 
 '["David Lee", "Emma Wilson"]'),

('US98765432', 'Natural Language Processing for Legal Documents', 
 'An automated system for analyzing legal documents including patents, contracts, and regulations. The system uses NLP techniques to extract key terms, identify relationships between documents, and generate summaries for legal professionals.',
 '2023-05-10', 'granted', 'LegalTech AI Corp.', 
 '["Frank Johnson", "Grace Kim"]'),

('US112233445', 'Blockchain-Based Patent Management System', 
 'A decentralized system using blockchain technology for managing patent applications, examinations, and ownership records. The system provides smart contracts for automated patent workflows and ensures immutability of patent records.',
 '2023-07-18', 'pending', 'BlockPatent Inc.', 
 '["Henry Zhang", "Isabella Rodriguez"]'),

('US556677889', 'Drug Delivery System Using Microneedles', 
 'A drug delivery system comprising microneedles for targeted drug administration. The system includes sensing mechanisms, control electronics, and biocompatible materials for precise drug release.', '2023-09-05', 'granted', 'MediTech Innovations', 
 '["Michael Brown", "Sarah Anderson"]'),

('US998877665', 'Smart Grid Energy Management System', 
 'An intelligent energy management system for smart grids that optimizes energy distribution, integrates renewable energy sources, and provides real-time monitoring and control of energy consumption and production.',
 '2023-11-20', 'pending', 'GreenEnergy Systems Inc.', 
 '["Robert Taylor", "Lisa Wang"]');

-- Sample report data
INSERT INTO reports (id, topic, content, patent_ids, report_type, created_at) VALUES
('ai_healthcare_analysis', 
'Artificial Intelligence in Healthcare Patent Analysis

Executive Summary
The analysis of AI-related patents in healthcare reveals significant innovation in diagnostic tools, treatment planning, and patient monitoring systems. Major technology companies are actively patenting machine learning applications for medical diagnosis and personalized treatment recommendations.

Key Findings
• Machine learning is revolutionizing healthcare diagnostics with accuracy improvements of 15-20% over traditional methods
• Patent activity in AI healthcare has increased 300% over the past five years
• Major technology companies including IBM, Google, and Microsoft hold significant patent portfolios in healthcare AI
• Natural language processing for medical records is a rapidly growing field with high innovation potential

Technical Analysis
The patents analyzed demonstrate advanced AI techniques including deep learning, neural networks, and natural language processing specifically adapted for medical applications. Key technical areas include:
- Diagnostic algorithms using imaging analysis
- Predictive analytics for disease identification
- Treatment recommendation systems
- Patient monitoring and alert systems

Market Landscape
The global AI healthcare market is projected to reach $50 billion by 2025, with a CAGR of 37.2% from 2023. The patent landscape indicates strong competitive positioning in core AI technologies for healthcare applications.

Strategic Recommendations
Based on the patent analysis and market assessment, the following strategic recommendations are provided:
1. Focus on diagnostic AI applications with proven clinical validation
2. Develop partnerships with healthcare providers for real-world testing
3. Invest in natural language processing capabilities for medical record analysis
4. Consider patent licensing opportunities in emerging healthcare AI markets
5. Monitor competitor patent activities and identify whitespace opportunities

Conclusion
The AI healthcare patent landscape presents significant opportunities for innovation and market entry. The combination of strong technical capabilities and strategic market positioning can lead to competitive advantages in this rapidly growing sector.',
 '["US12345678", "US67890123", "US98765432"], 'comprehensive', '2024-01-15'),

('patent_trends_report', 
'Blockchain Patent Technology Trends Analysis

Executive Summary
This report analyzes patent filings in blockchain technology over the past decade, revealing key trends and innovation patterns in distributed ledger systems and smart contract applications.

Key Findings
• Blockchain patent filings have grown 4000% since 2018
• Smart contracts represent 35% of all blockchain patents
• Financial applications lead in enterprise blockchain adoption
• Supply chain management patents show increasing activity
• Cross-industry collaboration patents are emerging

Technical Analysis
The patent portfolio demonstrates innovation in:
- Consensus mechanisms for distributed systems
- Smart contract automation and execution
- Privacy-preserving transaction systems
- Supply chain transparency and tracking
- Digital identity verification systems

Market Analysis
The blockchain technology market is experiencing rapid growth with enterprise adoption driving patent activity in financial services, supply chain management, and digital identity sectors.

Strategic Recommendations
1. Focus on enterprise blockchain solutions with proven ROI
2. Develop partnerships with financial institutions for adoption
3. Invest in scalability solutions for high-volume transaction processing
4. Consider privacy-enhancing technologies for competitive advantage
5. Monitor regulatory developments affecting blockchain patents

Conclusion
Blockchain technology patents represent a significant opportunity for innovation in distributed systems and smart contract applications. Strategic focus on enterprise solutions and privacy-enhancing features can provide competitive advantages in this growing technology sector.',
 '["US998877665", "US112233445"], 'market', '2024-02-20');

-- Sample chat history (for future use)
INSERT INTO chat_history (id, user_message, bot_response, patent_ids, timestamp) VALUES
('chat_001', 
'What are the latest AI patents in healthcare?', 
'Based on recent patent analysis, the latest AI patents in healthcare focus on diagnostic AI applications, treatment planning systems, and patient monitoring. Major companies like IBM, Google, and Microsoft are actively patenting machine learning for medical diagnosis. The most innovative areas include deep learning for medical imaging and natural language processing for clinical documentation.', 
'["US12345678", "US67890123", "US98765432"], '2024-01-10T10:30:00Z');