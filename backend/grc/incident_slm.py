import json
import re
try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: langchain_ollama not available, falling back to mock analysis")
import random
import traceback

def analyze_incident_comprehensive(incident_title, incident_description):
    """
    Comprehensive incident analysis for GRC banking system with extensive banking-specific analysis.
    
    Args:
        incident_title (str): Title of the incident
        incident_description (str): Detailed description of the incident
    
    Returns:
        dict: JSON object containing comprehensive incident analysis
    """
    try:
        # Check if Ollama is available
        if not OLLAMA_AVAILABLE:
            print("Ollama not available, using fallback analysis")
            return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
        # Initialize the local SLM model with increased timeout
        llm = OllamaLLM(model="llama3.2:3b", temperature=0.7, request_timeout=60.0)
       
        prompt_template = PromptTemplate.from_template("""
        You are a senior cybersecurity analyst and risk management expert specializing in banking GRC (Governance, Risk, and Compliance) systems with 15+ years of experience in financial services security, regulatory compliance, and operational risk management.
        
        Analyze the following security incident and provide a comprehensive, detailed assessment in JSON format. Each field must contain extensive, banking-specific information, not generic responses.

        DETAILED FIELD REQUIREMENTS:

        1. "riskPriority": 
           - P0: Immediate threat to critical banking operations (online banking down, core banking system compromised, payment processing halted, customer data breach affecting >10,000 customers, regulatory violation with potential >$1M penalty)
           - P1: Significant impact (ATM network issues, trading system disruption, moderate data exposure 1,000-10,000 customers, compliance violation with $100K-$1M penalty)
           - P2: Limited impact (branch system slowdown, non-critical application issues, internal policy violations, <1,000 customers affected)
           - P3: Minor impact (single workstation compromise, minor policy deviation, no customer impact)

        2. "criticality": Consider banking-specific factors:
           - Critical: Core banking systems, payment rails, customer-facing applications, regulatory reporting systems
           - High: Trading platforms, loan origination systems, risk management systems, fraud detection
           - Medium: Internal applications, non-customer facing systems, administrative tools
           - Low: Development environments, isolated systems, non-production environments

        3. "costOfIncident": Provide detailed cost breakdown as STRING including:
           - Direct incident response costs (security teams, external consultants, forensics)
           - Regulatory fines (FFIEC: $25K-$1M, OCC: $100K-$50M, State regulators: $10K-$500K)
           - Business disruption (hourly revenue loss, operational costs)
           - Customer notification costs ($2-5 per customer affected)
           - Credit monitoring services ($150-300 per affected customer annually)
           - Legal and litigation expenses
           - Reputational damage and customer attrition
           - System remediation and security improvements
           - Compliance audit costs
           Format as detailed range: "$X - $Y including $Z in regulatory fines, $A in operational costs, $B in customer remediation"

        4. "possibleDamage": Provide comprehensive analysis covering:
           - Immediate operational impact on banking services
           - Customer service disruption and potential customer loss
           - Financial transaction integrity issues
           - Regulatory compliance violations and potential penalties
           - Reputational damage in financial services sector
           - Market confidence and stock price impact
           - Third-party vendor and correspondent bank relationships
           - Credit rating agency implications
           - Competitive disadvantage scenarios
           - Long-term business continuity risks

        5. "systemsInvolved": List specific banking systems (not generic IT systems):
           - Core Banking Systems (CBS): Temenos, FIS, Jack Henry, Fiserv
           - Payment Processing: ACH, wire transfer, card processing, real-time payments
           - Digital Banking: Online banking, mobile apps, API gateways
           - Trading Systems: Fixed income, equities, derivatives, treasury
           - Risk Management: Credit risk, market risk, operational risk platforms
           - Regulatory Reporting: FFIEC, OCC, Fed reporting systems
           - Anti-Money Laundering: Transaction monitoring, sanctions screening
           - Customer Data: CRM, KYC systems, customer onboarding
           - Infrastructure: Network segmentation, firewalls, SIEM, endpoints

        6. "initialImpactAssessment": Detailed technical and business impact including:
           - Specific systems compromised and their business functions
           - Data types potentially exposed (PII, financial data, payment information)
           - Number of customers potentially affected
           - Geographic scope of impact
           - Operational capabilities currently degraded
           - Regulatory notifications required and timelines
           - Immediate business continuity concerns
           - Third-party and vendor impact assessment

        7. "mitigationSteps": Comprehensive banking-specific response plan:
           - Immediate containment actions specific to banking environment
           - Customer communication strategy and regulatory notifications
           - Business continuity and disaster recovery activation
           - Forensic investigation procedures for financial services
           - Regulatory compliance and reporting requirements
           - Third-party vendor coordination and supply chain security
           - Customer protection measures and fraud monitoring
           - System recovery and service restoration procedures
           - Evidence preservation for regulatory examination
           - Post-incident strengthening of controls

        8. "comments": Expert analysis including:
           - Banking industry context and sector-specific implications
           - Regulatory landscape considerations
           - Comparison to similar incidents in banking sector
           - Industry best practices for similar scenarios
           - Lessons from regulatory guidance and enforcement actions
           - Risk management framework implications
           - Board and senior management considerations
           - External stakeholder impact (regulators, auditors, customers)

        9. "violatedPolicies": Specific banking policies and regulations:
           - Information Security Policy and data classification standards
           - Access Control and Privileged Access Management policies
           - Incident Response and Business Continuity policies
           - Third-Party Risk Management and vendor oversight
           - Customer Data Protection and Privacy policies
           - Regulatory Compliance Framework violations
           - Operational Risk Management procedures
           - Change Management and System Development policies
           - Physical Security and Environmental Controls
           - Employee Code of Conduct and insider threat policies

        10. "procedureControlFailures": Detailed control breakdowns:
            - Identity and Access Management (IAM) control failures
            - Network Security Controls (firewalls, segmentation, monitoring)
            - Endpoint Detection and Response (EDR) control gaps
            - Security Information and Event Management (SIEM) failures
            - Data Loss Prevention (DLP) control bypasses
            - Vulnerability Management and Patch Management failures
            - Security Awareness Training and Human Controls
            - Third-Party Security Assessment and Monitoring
            - Backup and Recovery Control inadequacies
            - Regulatory Compliance Monitoring failures

        11. "lessonsLearned": Comprehensive improvement recommendations:
            - Specific security control enhancements with implementation timelines
            - Governance and risk management process improvements
            - Regulatory compliance program strengthening
            - Technology architecture and security design improvements
            - Incident response and business continuity enhancements
            - Third-party risk management program updates
            - Security awareness and training program improvements
            - Metrics and monitoring capability enhancements
            - Board and executive reporting process improvements
            - Industry collaboration and information sharing enhancements

        BANKING REGULATORY CONTEXT TO CONSIDER:
        - Federal Financial Institutions Examination Council (FFIEC) guidelines
        - Office of the Comptroller of the Currency (OCC) regulations
        - Federal Reserve Board (FRB) supervisory guidance
        - Federal Deposit Insurance Corporation (FDIC) requirements
        - Consumer Financial Protection Bureau (CFPB) oversight
        - Gramm-Leach-Bliley Act (GLBA) privacy requirements
        - Bank Secrecy Act (BSA) and Anti-Money Laundering (AML) compliance
        - Sarbanes-Oxley Act (SOX) financial reporting requirements
        - Payment Card Industry Data Security Standard (PCI DSS)
        - New York Department of Financial Services (NYDFS) Cybersecurity Regulation
        - European Banking Authority (EBA) guidelines for international banks
        - Basel III operational risk framework
        - SWIFT Customer Security Programme (CSP) requirements

        CRITICAL BANKING SYSTEM CATEGORIES:
        - Core Banking Systems (deposit, lending, customer management)
        - Payment and Settlement Systems (ACH, wire, card processing)
        - Trading and Capital Markets Systems (securities, derivatives, treasury)
        - Risk Management Systems (credit, market, operational, liquidity risk)
        - Regulatory Reporting Systems (prudential, AML, consumer protection)
        - Customer Channels (online banking, mobile, ATM, branch systems)
        - Anti-Money Laundering and Sanctions Screening Systems
        - Credit Decision and Loan Origination Systems
        - Fraud Detection and Prevention Systems
        - Data Analytics and Business Intelligence Platforms

        RESPONSE REQUIREMENTS:
        - Each field must contain detailed, banking-specific information
        - Avoid generic IT security responses
        - Include specific regulatory implications and requirements
        - Reference actual banking systems and technologies
        - Provide quantitative estimates where possible
        - Consider both immediate and long-term impacts
        - Include specific timelines and deadlines
        - Reference industry standards and best practices

        Incident Title: {title}
        Incident Description: {description}

        Respond ONLY with a valid JSON object containing all fields above with comprehensive, banking-specific analysis. No additional text or formatting.
        """)
       
        chain = LLMChain(llm=llm, prompt=prompt_template)
       
        # Process the incident
        print(f"Analyzing incident: {incident_title}")
        print(f"Description: {incident_description}")
        response = chain.invoke({"title": incident_title, "description": incident_description})["text"]
        print(f"Raw AI response: {response}")
       
        # Clean and parse the JSON from the response
        try:
            # Remove any extra text before or after the JSON
            json_text = response.strip()
            
            # Handle different response formats
            if json_text.startswith("```json") and json_text.endswith("```"):
                json_text = json_text[7:-3].strip()
            elif json_text.startswith("```") and json_text.endswith("```"):
                json_text = json_text[3:-3].strip()
            elif "```json" in json_text:
                # Extract JSON from markdown code block
                start_idx = json_text.find("```json") + 7
                end_idx = json_text.find("```", start_idx)
                if end_idx != -1:
                    json_text = json_text[start_idx:end_idx].strip()
            elif "{" in json_text and "}" in json_text:
                # Extract JSON object from response
                start_idx = json_text.find("{")
                end_idx = json_text.rfind("}") + 1
                json_text = json_text[start_idx:end_idx]
            
            print(f"Cleaned JSON text: {json_text}")
            
            try:
                # First attempt: Try to parse the JSON directly
                incident_analysis = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"Initial JSON parsing failed: {e}")
                
                # Try to fix the JSON by removing problematic backslashes
                try:
                    # Fix the specific issue with escaped backslashes
                    fixed_json = json_text.replace('\"', '"')
                    
                    # Try to parse the fixed JSON
                    try:
                        incident_analysis = json.loads(fixed_json)
                        print("Successfully parsed JSON after fixing backslashes")
                    except json.JSONDecodeError:
                        # If still failing, try a more aggressive approach
                        print("Still having JSON parsing issues, trying more aggressive fix")
                        
                        # Recreate the JSON from scratch with banking-specific defaults
                        import ast
                        try:
                            # Extract the raw data using regex patterns
                            risk_priority = re.search(r'"riskPriority":\s*"([^"]+)"', json_text)
                            criticality = re.search(r'"criticality":\s*"([^"]+)"', json_text)
                            cost = re.search(r'"costOfIncident":\s*"([^"]+)"', json_text)
                            damage = re.search(r'"possibleDamage":\s*"([^"]+)"', json_text)
                            impact = re.search(r'"initialImpactAssessment":\s*"([^"]+)"', json_text)
                            comments = re.search(r'"comments":\s*"([^"]+)"', json_text)
                            
                            # Create a new clean JSON structure with banking-specific defaults
                            incident_analysis = {
                                "riskPriority": risk_priority.group(1) if risk_priority else "P1",
                                "criticality": criticality.group(1) if criticality else "High",
                                "costOfIncident": cost.group(1) if cost else "$250,000 - $1,500,000 including $500,000 in regulatory fines, $300,000 in operational costs, $200,000 in customer remediation",
                                "possibleDamage": damage.group(1) if damage else "Potential compromise of core banking systems affecting customer transaction processing, regulatory compliance violations under FFIEC guidelines, customer data exposure requiring notification under GLBA, operational disruption to payment processing systems, reputational damage affecting market confidence and customer trust in banking services",
                                "systemsInvolved": [
                                    "Core Banking System (CBS)",
                                    "Online Banking Platform",
                                    "Payment Processing System",
                                    "Customer Database",
                                    "Network Infrastructure",
                                    "SIEM and Security Monitoring",
                                    "ATM Network",
                                    "Mobile Banking Application"
                                ],
                                "initialImpactAssessment": impact.group(1) if impact else "Immediate assessment indicates potential compromise of customer-facing banking systems with possible exposure of personally identifiable information (PII) and financial data. Approximately 5,000-15,000 customers potentially affected. Core banking operations remain functional but monitoring systems detected anomalous activity. Regulatory notification requirements under FFIEC guidelines triggered within 72 hours. Business continuity measures activated.",
                                "mitigationSteps": [
                                    "Immediately isolate affected banking systems and network segments",
                                    "Activate incident response team including CISO, CRO, and legal counsel",
                                    "Notify primary regulators (OCC, Fed, FDIC) within 72 hours per FFIEC requirements",
                                    "Conduct forensic analysis of compromised systems using banking-certified forensics team",
                                    "Implement enhanced fraud monitoring on all customer accounts",
                                    "Prepare customer notification strategy in compliance with GLBA privacy requirements",
                                    "Activate business continuity plan for critical banking operations",
                                    "Coordinate with cyber insurance provider and external legal counsel",
                                    "Implement temporary access controls and enhanced monitoring",
                                    "Prepare regulatory examination response and documentation"
                                ],
                                "comments": comments.group(1) if comments else "This incident represents a significant operational risk event for the banking institution requiring immediate regulatory notification and comprehensive response. The incident demonstrates potential weaknesses in the bank's cybersecurity framework and may trigger enhanced regulatory scrutiny. Given the banking sector's interconnected nature, this incident could impact correspondent banking relationships and third-party service providers. The institution should prepare for potential regulatory examination and enforcement action.",
                                "violatedPolicies": [
                                    "Information Security Policy - Data Classification and Protection Standards",
                                    "Access Control Policy - Privileged Access Management",
                                    "Incident Response Policy - Escalation and Notification Procedures",
                                    "Customer Data Protection Policy - GLBA Privacy Requirements",
                                    "Third-Party Risk Management Policy - Vendor Security Oversight",
                                    "Network Security Policy - Segmentation and Monitoring",
                                    "Business Continuity Policy - Disaster Recovery Procedures",
                                    "Regulatory Compliance Framework - FFIEC Cybersecurity Guidelines"
                                ],
                                "procedureControlFailures": [
                                    "Identity and Access Management (IAM) - Inadequate privileged access controls",
                                    "Network Security Controls - Insufficient network segmentation between banking zones",
                                    "Security Information and Event Management (SIEM) - Delayed threat detection and response",
                                    "Endpoint Detection and Response (EDR) - Inadequate monitoring of banking workstations",
                                    "Data Loss Prevention (DLP) - Failed to prevent sensitive data exfiltration",
                                    "Vulnerability Management - Unpatched systems in critical banking infrastructure",
                                    "Security Awareness Training - Inadequate phishing and social engineering awareness",
                                    "Third-Party Security Assessment - Insufficient vendor risk management",
                                    "Backup and Recovery Controls - Inadequate recovery procedures for banking systems",
                                    "Regulatory Compliance Monitoring - Failed to meet FFIEC cybersecurity requirements"
                                ],
                                "lessonsLearned": [
                                    "Implement enhanced network segmentation separating core banking systems from general IT infrastructure with specific focus on payment processing isolation",
                                    "Strengthen privileged access management with multi-factor authentication and just-in-time access for all banking system administrators",
                                    "Deploy advanced threat detection capabilities specifically tuned for banking sector threats including insider trading and financial fraud patterns",
                                    "Enhance incident response procedures with specific regulatory notification workflows for banking regulators (OCC, Fed, FDIC, CFPB)",
                                    "Implement comprehensive security awareness training program focused on banking-specific threats including business email compromise and wire fraud",
                                    "Establish dedicated cybersecurity governance committee with board-level oversight and regular reporting to banking regulators",
                                    "Develop enhanced third-party risk management program with continuous monitoring of critical banking service providers",
                                    "Implement real-time fraud detection and prevention systems integrated with core banking platforms",
                                    "Establish cyber threat intelligence sharing with banking industry consortiums and federal banking agencies",
                                    "Create comprehensive cyber resilience testing program including tabletop exercises simulating banking-specific cyber scenarios"
                                ]
                            }
                            print("Created comprehensive banking-specific JSON structure from regex extraction")
                        except Exception as regex_error:
                            print(f"Regex extraction failed: {regex_error}")
                            # If all else fails, use the fallback
                            return generate_comprehensive_fallback_analysis(incident_title, incident_description)
                except Exception as fix_error:
                    print(f"Failed to fix JSON: {fix_error}")
                    # If parsing still fails, fall back to the generated response
                    print("Falling back to generated analysis")
                    return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
            # Validate that we have the required fields
            required_fields = ['riskPriority', 'criticality', 'costOfIncident', 'possibleDamage', 
                             'systemsInvolved', 'initialImpactAssessment', 'mitigationSteps', 
                             'comments', 'violatedPolicies', 'procedureControlFailures', 'lessonsLearned']
            missing_fields = [field for field in required_fields if field not in incident_analysis]
            
            if missing_fields:
                print(f"Missing required fields in AI response: {missing_fields}")
                print("Falling back to generated analysis")
                return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
            print(f"Successfully parsed comprehensive banking GRC incident analysis: {incident_analysis}")
            return incident_analysis
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
            print(f"Failed to parse JSON from: {json_text}")
            # If JSON parsing fails, fall back to the generated response
            return generate_comprehensive_fallback_analysis(incident_title, incident_description)
            
    except Exception as e:
        print(f"Error using Ollama model: {e}")
        traceback.print_exc()
        # Fall back to a generated response if the model fails
        return generate_comprehensive_fallback_analysis(incident_title, incident_description)


def generate_comprehensive_fallback_analysis(incident_title, incident_description):
    """Generate a comprehensive fallback analysis when the AI model is unavailable."""
    # Extract some keywords from the incident for basic categorization
    description_lower = (incident_title + " " + incident_description).lower()
    
    # Default values
    risk_priority = "P1"
    criticality = "Medium"
    cost_estimate = "$50,000 - $250,000"
    systems = ["Core Banking System", "Network Infrastructure"]
    
    # Basic categorization based on keywords and assign appropriate values
    if any(word in description_lower for word in ["breach", "leak", "exposed", "data", "sensitive", "customer"]):
        risk_priority = "P0"
        criticality = "Critical"
        cost_estimate = "$500,000 - $5,000,000"
        systems = ["Core Banking System", "Customer Database", "Online Banking Platform", "Data Warehouse"]
        possible_damage = "Massive customer data exposure, regulatory penalties up to $50M, severe reputational damage, potential class-action lawsuits, loss of customer trust, and business continuity threats."
        violated_policies = ["Data Protection Policy", "Customer Privacy Policy", "Information Security Policy", "Incident Response Policy"]
        control_failures = ["Data encryption controls", "Access control mechanisms", "Data loss prevention systems", "Network segmentation controls"]
        
    elif any(word in description_lower for word in ["malware", "virus", "ransomware", "trojan", "attack"]):
        risk_priority = "P0"
        criticality = "Critical"
        cost_estimate = "$250,000 - $2,000,000"
        systems = ["Core Banking System", "ATM Network", "Payment Processing System", "Email System"]
        possible_damage = "System disruption, potential data encryption, business operations halt, customer service interruption, and recovery costs."
        violated_policies = ["Malware Protection Policy", "System Security Policy", "Business Continuity Policy"]
        control_failures = ["Antivirus protection", "Email filtering systems", "Network intrusion detection", "Endpoint protection controls"]
        
    elif any(word in description_lower for word in ["phish", "social engineering", "fraud", "impersonation"]):
        risk_priority = "P1"
        criticality = "High"
        cost_estimate = "$100,000 - $750,000"
        systems = ["Email System", "Online Banking Platform", "Employee Workstations", "Authentication System"]
        possible_damage = "Credential theft, unauthorized access to customer accounts, potential financial fraud, and employee security awareness gaps."
        violated_policies = ["Email Security Policy", "Authentication Policy", "Employee Training Policy", "Fraud Prevention Policy"]
        control_failures = ["Email security controls", "Multi-factor authentication", "User awareness training", "Fraud detection systems"]
        
    elif any(word in description_lower for word in ["unauthorized", "access", "privilege", "credential", "insider"]):
        risk_priority = "P1"
        criticality = "High"
        cost_estimate = "$150,000 - $1,000,000"
        systems = ["Core Banking System", "Privileged Access Management", "Active Directory", "Database Systems"]
        possible_damage = "Unauthorized access to sensitive data, privilege escalation, potential data theft, and insider threat materialization."
        violated_policies = ["Access Control Policy", "Privileged Access Policy", "Identity Management Policy", "Segregation of Duties Policy"]
        control_failures = ["Access control systems", "Privilege management controls", "User access reviews", "Segregation of duties controls"]
        
    elif any(word in description_lower for word in ["compliance", "regulatory", "audit", "violation"]):
        risk_priority = "P1"
        criticality = "High"
        cost_estimate = "$200,000 - $10,000,000"
        systems = ["Compliance Management System", "Audit Trail System", "Reporting System", "Document Management"]
        possible_damage = "Regulatory fines, enforcement actions, audit findings, reputational damage, and increased regulatory scrutiny."
        violated_policies = ["Regulatory Compliance Policy", "Audit Policy", "Documentation Policy", "Reporting Policy"]
        control_failures = ["Compliance monitoring controls", "Audit trail mechanisms", "Regulatory reporting controls", "Documentation controls"]
        
    else:
        # Default case
        possible_damage = "Potential operational disruption, security compromise, and moderate business impact requiring immediate attention."
        violated_policies = ["Information Security Policy", "Incident Response Policy", "Risk Management Policy"]
        control_failures = ["Security monitoring controls", "Incident detection systems", "Risk assessment procedures"]
    
    return {
        "riskPriority": risk_priority,
        "criticality": criticality,
        "costOfIncident": cost_estimate,
        "possibleDamage": possible_damage,
        "systemsInvolved": systems,
        "initialImpactAssessment": f"Incident '{incident_title}' has been identified with potential impact on critical banking operations. Immediate containment and investigation required to determine full scope and prevent escalation.",
        "mitigationSteps": [
            "Step 1: Activate incident response team and establish command center",
            "Step 2: Isolate affected systems to prevent further compromise or spread",
            "Step 3: Preserve evidence and maintain chain of custody for forensic analysis",
            "Step 4: Assess immediate business impact and implement business continuity measures",
            "Step 5: Notify key stakeholders including senior management and legal team",
            "Step 6: Conduct preliminary investigation to determine root cause and scope",
            "Step 7: Implement temporary controls and workarounds to restore operations",
            "Step 8: Engage external experts if specialized skills are required",
            "Step 9: Prepare regulatory notifications if required by compliance obligations",
            "Step 10: Document all actions taken and maintain incident timeline",
            "Step 11: Conduct post-incident review and implement lessons learned",
            "Step 12: Update security controls and procedures to prevent recurrence"
        ],
        "comments": f"This incident requires immediate attention due to its potential impact on banking operations. The analysis is based on the incident title '{incident_title}' and available description. Further investigation may reveal additional complexities requiring escalated response measures.",
        "violatedPolicies": violated_policies,
        "procedureControlFailures": control_failures,
        "lessonsLearned": [
            "Importance of rapid incident detection and response capabilities",
            "Need for regular security awareness training and testing",
            "Critical role of backup and recovery procedures in business continuity",
            "Value of comprehensive incident documentation for future reference",
            "Necessity of regular security control testing and validation",
            "Importance of clear communication channels during incident response",
            "Need for regular review and update of incident response procedures",
            "Critical importance of stakeholder notification and regulatory compliance"
        ]
    }
