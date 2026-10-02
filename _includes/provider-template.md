---
# RSSN provider listing. Each field matches a question on the RSSN Research IT Provider Questionnaire.
# For lists, delete the lines that don't apply and keep the spelling of the rest exactly as written.
# For single answers, pick one of the values listed in the comment above the field.
# Anything that doesn't fit a listed value goes in the matching "_other" field as plain text.
# Leave a field empty ("" or []) if the questionnaire skipped it for your team.

# Q7. Team or service name, as researchers should see it
title: "Your Team or Service Name"

# Q5. One of: JHU, JHHS, Joint JHU/JHHS
institution: "JHU"

# Q6. School, division, or central office. These get a colored card accent:
#   Whiting School of Engineering; School of Medicine; Bloomberg School of Public Health; Sheridan Libraries; Office of Research; Johns Hopkins IT
school: "Whiting School of Engineering"

# Q6. Department or organizational unit within that school
unit: "Department of Example Studies"

# Q8. Website or service information URL (optional; leave "" if none)
website: ""

# Q1-4. Primary point of contact
contact:
  name: "First Last"
  email: "name@jhu.edu"

# Date this listing was last reviewed (YYYY-MM-DD)
updated: 2026-01-01

# ===== Who you support =====

# Q9. Team type. One of:
#   Research support service | Research group sharing expertise | IT service with research support
team_type: "Research support service"

# Q10. Available to. One of:
#   Hopkins-wide | JHU only | JHHS only | Certain schools/divisions | Own department/unit only | It's complicated
availability: "Hopkins-wide"

# Q11. Who can engage this team
eligible:
  - "Cross-institution JHU/JHHS projects"
  - "JHHS faculty"
  - "JHHS staff"
  - "JHU faculty"
  - "JHU staff"
  - "JHU students/trainees working on sponsored research"
  - "Johns Hopkins research centers/institutes"
  - "Other Hopkins-affiliated groups"
  - "Projects involving external research collaborators"
eligible_other: ""

# ===== Services & expertise =====

# Q12-15. Services you offer (Offered or Area of strength in the grids), by group
services:
  # Software Development & Engineering
  - "AI-Assisted Coding"
  - "Python or R Package Development"
  - "UX, Accessibility & Software Quality"
  - "Version Control & Collaboration"
  - "Web & Application Development"
  # Data, AI & Analytics
  - "Data Pipeline Automation"
  - "Databases"
  - "Machine Learning Operations"
  - "Machine Learning/AI Development"
  - "Reproducible Research Workflows"
  # Computing & Infrastructure
  - "Containerization & Cloud Computing"
  - "DevOps & Infrastructure Operations"
  - "High-Performance/Parallel Computing"
  - "IT Security & Compliance"
  # Consulting, Training & Sustainability
  - "Domain/Subject-Matter Expertise"
  - "Open Source Licensing & Sustainability"
  - "Technical Consulting & Solution Architecture"
  - "Technical Documentation & Training"

# Q12-15. Areas of strength: up to five of the services above
strengths:
  - "AI-Assisted Coding"
  - "Python or R Package Development"
  # ...add up to three more

# Q16. Other services or expertise (optional; Markdown is fine)
services_other: ""

# Q17. Example projects (optional; Markdown is fine)
examples: ""

# ===== Technical capabilities =====

# Q19. Does hands-on technical work. One of:
#   Yes | No
hands_on: "Yes"

# Q20. Languages and development technologies
languages:
  - "Angular"
  - "C / C++"
  - "C# / .NET"
  - "Java"
  - "JavaScript / TypeScript"
  - "Kotlin / Android"
  - "MATLAB"
  - "Node.js"
  - "PHP"
  - "PowerShell"
  - "Python"
  - "R"
  - "React"
  - "Ruby"
  - "SAS"
  - "SQL"
  - "Stata"
  - "Swift / iOS"
  - "Vue"
  - "Not applicable"
languages_other: ""

# Q21. Databases
databases:
  - "Azure SQL"
  - "Cloud-native databases"
  - "Microsoft SQL Server"
  - "MongoDB"
  - "MySQL/MariaDB"
  - "NoSQL databases (other)"
  - "Oracle"
  - "PostgreSQL"
  - "Not applicable"
databases_other: ""

# Q22. Infrastructure and DevOps
devops:
  - "Amazon EKS"
  - "Azure DevOps"
  - "Azure Kubernetes Service (AKS)"
  - "Docker"
  - "GitHub"
  - "GitHub Actions"
  - "Jenkins"
  - "Kubernetes"
  - "Monitoring/logging platforms"
  - "Singularity/Apptainer"
  - "Terraform"
  - "Other Infrastructure as Code"
  - "Not applicable"
devops_other: ""

# Q23. Computing and hosting environments
hosting:
  - "Amazon Web Services (AWS)"
  - "Containerized environments"
  - "High-performance computing (HPC)"
  - "Hybrid cloud/on-premises environments"
  - "Johns Hopkins-managed infrastructure"
  - "Microsoft Azure"
  - "On-premises servers"
  - "Vendor/SaaS platforms"
  - "Not applicable"
hosting_other: ""

# ===== Research experience =====

# Q24. Research areas
research_areas:
  - "Basic science"
  - "Biomedical research"
  - "Clinical research"
  - "Computational science"
  - "Data science"
  - "Education research"
  - "Engineering"
  - "Genomics/bioinformatics"
  - "Humanities"
  - "Imaging"
  - "Multidisciplinary research"
  - "Population health"
  - "Public health"
  - "Social sciences"
  - "General/research area independent"
research_areas_other: ""

# Q25. Project stages
stages:
  - "Early consultation / feasibility"
  - "Grant proposal development"
  - "Grant budgeting / cost estimates"
  - "Technical architecture/design"
  - "Prototype/proof of concept"
  - "Software development"
  - "Research data collection"
  - "Research data processing/analysis"
  - "Production deployment"
  - "Ongoing maintenance/support"
  - "Project closeout"
  - "Data/software archiving"
stages_other: ""

# Q26. Technical estimates for grant proposals. One of:
#   Yes | Yes, on a case-by-case basis | No
grant_estimates: "Yes"

# Q27. Consults before funding is awarded. One of:
#   Yes | Yes, on a limited basis | Depends on the project | No
pre_award: "Yes"

# Q28. Initial or pre-award consultation. One of:
#   A brief conversation (about an hour or less) | A few meetings or a short written assessment (up to about 10 hours) | Scoped case by case
consult_scope: "A brief conversation (about an hour or less)"

# ===== Research data, security & compliance =====

# Q29. Data types supported
data_types:
  - "Data under NIST 800-171 controls"
  - "De-identified health information"
  - "Genomic data"
  - "Human-subject research data"
  - "Non-sensitive research data"
  - "Personally identifiable information (PII)"
  - "Proprietary/confidential research data"
  - "Protected health information (PHI)"
  - "Public data"
  - "Restricted data"
  - "Depends on the hosting/environment"
  - "Unsure / requires review"
data_types_other: ""

# Q30. Requirements and reviews supported
compliance:
  - "Accessibility requirements"
  - "Business Associate Agreements (BAAs)"
  - "Data Use Agreements (DUAs)"
  - "HIPAA"
  - "IRB / human-subject research"
  - "Johns Hopkins IT Risk/Security review"
  - "Research involving external collaborators"
  - "Restricted-access research data"
  - "None of the above"
compliance_other: ""

# Q31. Security and compliance approach. One of:
#   Our team can lead the technical security/compliance process | Our team can assist the researcher with the process | The researcher/project team is primarily responsible | Another Hopkins group handles this for us | Varies by project | Not applicable
security_approach: "Our team can lead the technical security/compliance process"

# ===== Engagement model =====

# Q32. Engagement types
engagement_types:
  - "Embedded technical staff"
  - "Full project delivery"
  - "Joint/co-development with a research team"
  - "Ongoing maintenance/support"
  - "Production operations"
  - "Prototype/proof-of-concept development"
  - "Short-term troubleshooting"
  - "Staff augmentation"
  - "Technical consultation/advisory services"
engagement_types_other: ""

# Q33. Project sizes
project_sizes:
  - "Less than 40 hours"
  - "40-200 hours"
  - "201-500 hours"
  - "501-1,000 hours"
  - "More than 1,000 hours"
  - "Ongoing/long-term engagements"
  - "No typical project size"
project_sizes_other: ""

# Q34. Engagement duration
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

# Q35. Takes over software from other teams. One of:
#   Yes | Yes, following a technical assessment | Case-by-case | No
takeover: "Yes"

# Q36. Works with the project's technical staff. One of:
#   Yes | Yes, on a case-by-case basis | No
collaborate: "Yes"

# ===== Cost & funding =====

# Q37. Cost to researchers. One of:
#   No cost | Free initial help, then charged | Charged
cost: "No cost"

# Q38. Where no-cost help ends (one line; leave "" if it doesn't apply)
free_limit: ""

# Q39. How charges are calculated
charges:
  - "Annual fee"
  - "Cloud consumption"
  - "Fixed project price"
  - "Hosting/infrastructure usage"
  - "Hourly"
  - "Monthly fee"
  - "Percent effort / FTE on the project budget"
  - "Software/license costs"
charges_other: ""

# Q40. Minimum commitment. One of:
#   No minimum | Less than $5,000 | $5,000-$10,000 | $10,001-$25,000 | More than $25,000 | Varies by project
minimum: "No minimum"

# Q41. How the team is funded
funding:
  - "Centrally funded"
  - "Department-funded"
  - "Fee-for-service"
  - "Grant-funded"
  - "Internal cost recovery"
funding_other: ""

# ===== Availability & support =====

# Q42. Accepting new work. One of:
#   Yes | Yes, with limited capacity | Not at this time
accepting: "Yes"

# Q43. Lead time to start. One of:
#   Less than 1 week | 1-2 weeks | 3-4 weeks | 1-2 months | More than 2 months | Varies based on project
lead_time: "Less than 1 week"

# Q44. Production support after launch. One of:
#   Yes | Yes, for applications developed by our team | Yes, on a separate support agreement | Yes, but only for a limited time | Case-by-case | No
production_support: "Yes"

# Q45. Support coverage
support_coverage:
  - "Standard Hopkins business hours"
  - "Extended-hours support"
  - "After-hours/on-call support"
  - "24x7 production support"
  - "Best-effort support"
  - "Project-specific support arrangements"
  - "Not applicable"
support_coverage_other: ""

# ===== Open source, software ownership & sustainability =====

# Q46. Open source support
open_source:
  - "Contribute to existing open source projects"
  - "Develop new open source software"
  - "Prepare software for public release"
  - "Advise on licensing, governance, or community"
  - "Maintain software after public release"
  - "Cannot currently support open source work"
  - "Unsure"
open_source_other: ""

# Q47. Hands off code and documentation. One of:
#   Yes | Yes, depending on the engagement | No | Not applicable
handoff_docs: "Yes"

# Q48. Long-term maintenance. One of:
#   Yes | Yes, for systems developed by our team | Case-by-case | No
maintenance: "Yes"

# ===== Additional information =====

# Q49. Good to know (optional; Markdown is fine)
notes: ""
---
Q18 (optional). A short paragraph shown beneath the summary RSSN builds from your answers:
your team's size, what sets you apart, unique tools or resources, or the projects you're best
suited for. About 500 characters. Delete this text if you don't want a paragraph.
