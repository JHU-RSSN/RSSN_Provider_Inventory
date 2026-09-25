---
# RSSN provider listing. Each field matches a question on the RSSN Research IT Provider Questionnaire.
# For lists, delete the lines that don't apply and keep the spelling of the rest exactly as written.
# For single answers, pick one of the values listed in the comment above the field.
# Anything that doesn't fit a listed value goes in the matching "_other" field as plain text.

# Q7. Team or service name, as researchers should see it
title: "Your Team or Service Name"

# Q5. One of: JHU, JHHS, Joint JHU/JHHS
institution: "JHU"

# Q6. School, division, or central office. These get a colored card accent:
#   Whiting School of Engineering; School of Medicine; Bloomberg School of Public Health; Sheridan Libraries; Office of Research; Johns Hopkins IT
school: "Whiting School of Engineering"

# Q6. Department or organizational unit within that school
unit: "Department of Example Studies"

# Q9. Website or service information URL (optional; leave "" if none)
website: ""

# Q3-4. Primary point of contact
contact:
  name: "First Last"
  email: "name@jhu.edu"

# Date this listing was last reviewed (YYYY-MM-DD)
updated: 2026-01-01

# Q10. Available to. One of:
#   Hopkins-wide | JHU only | JHHS only | Certain schools/divisions | Other criteria | Own department/unit only | Not outside own unit (other)
availability: "Hopkins-wide"

# Q11. Who can engage this team
eligible:
  - "JHU faculty"
  - "JHU staff"
  - "JHU students/trainees working on sponsored research"
  - "JHHS faculty"
  - "JHHS staff"
  - "Johns Hopkins research centers/institutes"
  - "Cross-institution JHU/JHHS projects"
  - "Projects involving external research collaborators"
  - "Other Hopkins-affiliated groups"
eligible_other: ""

# Q13. Services
services:
  - "AI-Assisted Coding"
  - "Containerization and Cloud Computing"
  - "Data Pipeline Automation"
  - "Databases"
  - "DevOps & Infrastructure Operations"
  - "High-Performance/Parallel Computing"
  - "IT Security & Compliance"
  - "Machine Learning Operations"
  - "Machine Learning/AI Development"
  - "Python or R Package Development"
  - "Reproducible Research Workflows"
  - "Technical Consulting & Solution Architecture"
  - "Technical Documentation & Training"
  - "UX, Accessibility & Software Quality"
  - "Version Control and Collaboration"
  - "Web Development"
services_other: ""

# Q42. Areas of strength (choose up to 5)
strengths:
  - "AI-Assisted Coding"
  - "Containerization and Cloud Computing"
  - "Data Pipeline Automation"
  - "Databases"
  - "DevOps & Infrastructure Operations"
  - "High-Performance/Parallel Computing"
  - "IT Security & Compliance"
  - "Machine Learning Operations"
  - "Machine Learning/AI Development"
  - "Python or R Package Development"
  - "Reproducible Research Workflows"
  - "Technical Consulting & Solution Architecture"
  - "Technical Documentation & Training"
  - "UX, Accessibility & Software Quality"
  - "Version Control and Collaboration"
  - "Web Development"
strengths_other: ""

# Q14. Languages and development technologies
languages:
  - "Python"
  - "R"
  - "SQL"
  - "SAS"
  - "Stata"
  - "MATLAB"
  - "Java"
  - "C# / .NET"
  - "C / C++"
  - "JavaScript / TypeScript"
  - "Node.js"
  - "Angular"
  - "React"
  - "Vue"
  - "Swift / iOS"
  - "Kotlin / Android"
  - "PHP"
  - "Ruby"
  - "PowerShell"
  - "Not applicable"
languages_other: ""

# Q15. Databases
databases:
  - "Microsoft SQL Server"
  - "PostgreSQL"
  - "MySQL/MariaDB"
  - "Oracle"
  - "Azure SQL"
  - "NoSQL databases"
  - "MongoDB"
  - "Cloud-native databases"
  - "Not applicable"
databases_other: ""

# Q16. Infrastructure and DevOps
devops:
  - "GitHub"
  - "GitHub Actions"
  - "Azure DevOps"
  - "Jenkins"
  - "Docker"
  - "Kubernetes"
  - "Azure Kubernetes Service (AKS)"
  - "Amazon EKS"
  - "Terraform"
  - "Other Infrastructure as Code"
  - "Monitoring/logging platforms"
  - "Not applicable"
devops_other: ""

# Q17. Computing and hosting environments
hosting:
  - "Microsoft Azure"
  - "Amazon Web Services (AWS)"
  - "Johns Hopkins-managed infrastructure"
  - "On-premises servers"
  - "High-performance computing (HPC)"
  - "Containerized environments"
  - "Vendor/SaaS platforms"
  - "Hybrid cloud/on-premises environments"
  - "Not applicable"
hosting_other: ""

# Q18. Research focus. One of:
#   Research is our primary focus | Frequently | Occasionally | Rarely | We do not currently support research projects
research_frequency: "Research is our primary focus"

# Q19. Research areas
research_areas:
  - "Clinical research"
  - "Biomedical research"
  - "Basic science"
  - "Public health"
  - "Population health"
  - "Engineering"
  - "Data science"
  - "Computational science"
  - "Social sciences"
  - "Education research"
  - "Humanities"
  - "Imaging"
  - "Genomics/bioinformatics"
  - "Multidisciplinary research"
  - "General/research area independent"
research_areas_other: ""

# Q20. Project stages
stages:
  - "Early consultation / feasibility"
  - "Grant proposal development"
  - "Technical architecture/design"
  - "Grant budgeting / cost estimates"
  - "Prototype/proof of concept"
  - "Software development"
  - "Research data collection"
  - "Research data processing/analysis"
  - "Production deployment"
  - "Ongoing maintenance/support"
  - "Project closeout"
  - "Data/software archiving"
  - "Transition from grant-funding to long-term sustainability"
stages_other: ""

# Q21. Technical estimates for grant proposals. One of:
#   Yes | Yes, on a case-by-case basis | No
grant_estimates: "Yes"

# Q22. Consults before funding is awarded. One of:
#   Yes | Yes, on a limited basis | Depends on the project | No
pre_award: "Yes"

# Q23. Data types supported
data_types:
  - "Public data"
  - "Non-sensitive research data"
  - "Personally identifiable information (PII)"
  - "Protected health information (PHI)"
  - "De-identified health information"
  - "Human-subject research data"
  - "Genomic data"
  - "Proprietary/confidential research data"
  - "Restricted data"
  - "Data under NIST 800-171 controls"
  - "Depends on the hosting/environment"
  - "Unsure / requires review"
data_types_other: ""

# Q24. Requirements and reviews supported
compliance:
  - "HIPAA"
  - "IRB / human-subject research"
  - "Johns Hopkins IT Risk/Security review"
  - "Data Use Agreements (DUAs)"
  - "Business Associate Agreements (BAAs)"
  - "Research involving external collaborators"
  - "Restricted-access research data"
  - "Accessibility requirements"
  - "None of the above"
compliance_other: ""

# Q25. Security and compliance approach. One of:
#   Our team can lead the technical security/compliance process | Our team can assist the researcher with the process | The researcher/project team is primarily responsible | Another Hopkins group handles this for us | Varies by project | Not applicable
security_approach: "Our team can lead the technical security/compliance process"

# Q26. Engagement types
engagement_types:
  - "Technical consultation/advisory services"
  - "Full project delivery"
  - "Staff augmentation"
  - "Embedded technical staff"
  - "Joint/co-development with a research team"
  - "Prototype/proof-of-concept development"
  - "Ongoing maintenance/support"
  - "Production operations"
  - "Short-term troubleshooting"
engagement_types_other: ""

# Q27. Project sizes
project_sizes:
  - "Less than 40 hours"
  - "40-200 hours"
  - "201-500 hours"
  - "501-1,000 hours"
  - "More than 1,000 hours"
  - "Ongoing/long-term engagements"
  - "No typical project size"
project_sizes_other: ""

# Q28. Engagement duration
durations:
  - "One-time consultation"
  - "Less than 1 month"
  - "1-3 months"
  - "3-6 months"
  - "6-12 months"
  - "More than 1 year"
  - "Ongoing support"
  - "Funding dependent"
  - "Varies significantly"
durations_other: ""

# Q29. Takes over software from other teams. One of:
#   Yes | Yes, following a technical assessment | Case-by-case | No
takeover: "Yes"

# Q30. Works with the project's technical staff. One of:
#   Yes | Yes, on a case-by-case basis | No
collaborate: "Yes"

# Q31. How services are funded
funding:
  - "No direct charge to researchers"
  - "Centrally funded"
  - "Fee-for-service"
  - "Internal cost recovery"
  - "Grant-funded"
  - "Department-funded"
  - "Combination of funding models"
funding_other: ""

# Q32. How charges are calculated
charges:
  - "Hourly"
  - "Fixed project price"
  - "Monthly fee"
  - "Annual fee"
  - "Generally based on FTE"
  - "Hosting/infrastructure usage"
  - "Software/license costs"
  - "Cloud consumption"
  - "Not applicable"
charges_other: ""

# Q33. Minimum commitment. One of:
#   No minimum | Less than $5,000 | $5,000-$10,000 | $10,001-$25,000 | More than $25,000 | Varies by project | Not applicable
minimum: "No minimum"

# Q34. Lead time to start. One of:
#   Less than 1 week | 1-2 weeks | 3-4 weeks | 1-2 months | More than 2 months | Varies based on project | Currently not accepting new work
lead_time: "Less than 1 week"

# Q35. Production support after launch. One of:
#   Yes | Yes, for applications developed by our team | Yes, on a separate support agreement | Case-by-case | No
production_support: "Yes"

# Q36. Support coverage
support_coverage:
  - "Standard Hopkins business hours"
  - "Extended-hours support"
  - "After-hours/on-call support"
  - "24x7 production support"
  - "Best-effort support"
  - "Project-specific support arrangements"
  - "Not applicable"
support_coverage_other: ""

# Q37. Supports public or open source release. One of:
#   Yes | Yes, on a case-by-case basis | No | Unsure
open_source: "Yes"

# Q38. Hands off code and documentation. One of:
#   Yes | Yes, depending on the engagement | No | Not applicable
handoff_docs: "Yes"

# Q39. Long-term maintenance. One of:
#   Yes | Yes, for systems developed by our team | Case-by-case | No
maintenance: "Yes"

# Q40. Example projects (optional; Markdown is fine)
examples: ""

# Q41. Good to know (optional; Markdown is fine)
notes: ""
---
Describe your team in 300-500 characters (2-3 sentences): who you support, your core services or specialty, and what makes your team a good fit.
