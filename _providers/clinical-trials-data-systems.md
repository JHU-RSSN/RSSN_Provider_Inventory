---
# SAMPLE LISTING: fictional team and contact, kept to demonstrate the directory.
# Delete this file once real listings cover the same ground.
#
# HOW TO EDIT THIS LISTING
#   Every answer choice from the questionnaire is listed below. A line that starts with
#   "# " is NOT selected; a line without it IS selected.
#   - CHOOSE ALL THAT APPLY: delete the "# " in front of a line to select it; type "# "
#     in front of it to unselect it. Leave the spaces before the "# " alone.
#   - CHOOSE ONE: exactly one line for the question should be missing its "# ".
#   - SERVICES: after each service, write one of: not offered, offered, strength
#     (strength = offered and an area of strength; no more than five).
#   - Keep the quotation marks and spelling of every answer exactly as they are.
#     Write-in ("Other") answers go in the matching _other line, inside the quotes.
#   - Update the "updated:" date to today when you change anything.
#   Allowed values: _data/taxonomy.yml. Reviewers can run scripts/check_listings.py.

sample: true

# Q9. Team or service name, as researchers should see it
title: "Clinical Trials Data Systems"

# Q7. Institution. CHOOSE ONE.
# institution: "JHU"
institution: "JHHS"
# institution: "Joint JHU/JHHS"

# Q8. School, division, or central office. CHOOSE ONE, or if yours isn't listed,
# write it on its own line the same way. Listed ones get a colored card accent.
# school: "Whiting School of Engineering"
school: "School of Medicine"
# school: "Bloomberg School of Public Health"
# school: "Sheridan Libraries"
# school: "Office of Research"
# school: "Johns Hopkins IT"
# Department or unit within that school (free text)
unit: "Office of Clinical Research Informatics"

# Q10. Website or service information URL (optional)
website: ""

# Q3-4. Primary contact, shown on the public site
contact:
  name: "Grace Feldman"
  email: "grace.feldman@example.edu"

# Date this listing was last reviewed (YYYY-MM-DD)
updated:

# ===== Who you support =====

# Q11. Team type. CHOOSE ONE.
# team_type: "Research support service"
# team_type: "Research group sharing expertise"
team_type: "IT service with research support"
# Q11. "Other" write-in answer, if any
team_type_other: ""

# Q12. Available to. CHOOSE ONE.
# availability: "Hopkins-wide"
# availability: "JHU only"
availability: "JHHS only"
# availability: "Certain schools/divisions"
# availability: "Own department/unit only"
# availability: "It's complicated"

# Q13. Availability details (free text; Markdown is fine)
availability_details: ""

# Q14. Who can engage this team. CHOOSE ALL THAT APPLY.
eligible:
  # - "Cross-institution JHU/JHHS projects"
  - "JHHS faculty"
  - "JHHS staff"
  # - "JHU faculty"
  # - "JHU staff"
  # - "JHU students/trainees working on sponsored research"
  # - "Johns Hopkins research centers/institutes"
  # - "Other Hopkins-affiliated groups"
  # - "Projects involving external research collaborators"
# Q14. "Other" write-in answer, if any
eligible_other: ""

# ===== Services & expertise =====

# Q15-18. Services. After each service write: not offered, offered, or strength.
# strength = offered AND an area of strength. No more than 5 strengths in all.
services:
  # Software Development & Engineering
  "AI-Assisted Coding":                           not offered
  "Python or R Package Development":              not offered
  "UX, Accessibility & Software Quality":         not offered
  "Version Control & Collaboration":              not offered
  "Web & Application Development":                not offered
  # Data, AI & Analytics
  "Data Pipeline Automation":                     not offered
  "Databases":                                    strength
  "Machine Learning Operations":                  not offered
  "Machine Learning/AI Development":              not offered
  "Reproducible Research Workflows":              not offered
  # Computing & Infrastructure
  "Containerization & Cloud Computing":           not offered
  "DevOps & Infrastructure Operations":           not offered
  "High-Performance/Parallel Computing":          not offered
  "IT Security & Compliance":                     strength
  # Consulting, Training & Sustainability
  "Domain/Subject-Matter Expertise":              not offered
  "Open Source Licensing & Sustainability":       not offered
  "Technical Consulting & Solution Architecture": not offered
  "Technical Documentation & Training":           offered

# Q19. Other services or expertise (free text; Markdown is fine)
services_other: ""

# Q20. Example projects (free text; Markdown is fine)
examples: ""

# ===== Technical capabilities =====

# Q22. Does hands-on technical work. CHOOSE ONE.
hands_on: "Yes"
# hands_on: "No"

# Q23. Languages and development technologies. CHOOSE ALL THAT APPLY (leave all unselected if Q22 is "No").
languages:
  # - "Angular"
  # - "C / C++"
  # - "C# / .NET"
  - "Java"
  # - "JavaScript / TypeScript"
  # - "Kotlin / Android"
  # - "MATLAB"
  # - "Node.js"
  # - "PHP"
  # - "PowerShell"
  # - "Python"
  # - "R"
  # - "React"
  # - "Ruby"
  # - "SAS"
  - "SQL"
  # - "Stata"
  # - "Swift / iOS"
  # - "Vue"
  # - "Not applicable"
# Q23. "Other" write-in answer, if any
languages_other: ""

# Q24. Databases. CHOOSE ALL THAT APPLY (leave all unselected if Q22 is "No").
databases:
  # - "Azure SQL"
  # - "Cloud-native databases"
  - "Microsoft SQL Server"
  # - "MongoDB"
  # - "MySQL/MariaDB"
  # - "NoSQL databases (other)"
  - "Oracle"
  # - "PostgreSQL"
  # - "Not applicable"
# Q24. "Other" write-in answer, if any
databases_other: ""

# Q25. Infrastructure and DevOps. CHOOSE ALL THAT APPLY (leave all unselected if Q22 is "No").
devops:
  # - "Amazon EKS"
  # - "Azure DevOps"
  # - "Azure Kubernetes Service (AKS)"
  # - "Docker"
  # - "GitHub"
  # - "GitHub Actions"
  # - "Jenkins"
  # - "Kubernetes"
  - "Monitoring/logging platforms"
  # - "Singularity/Apptainer"
  # - "Terraform"
  # - "Other Infrastructure as Code"
  # - "Not applicable"
# Q25. "Other" write-in answer, if any
devops_other: ""

# Q26. Computing and hosting environments. CHOOSE ALL THAT APPLY (leave all unselected if Q22 is "No").
hosting:
  # - "Amazon Web Services (AWS)"
  # - "Containerized environments"
  # - "High-performance computing (HPC)"
  # - "Hybrid cloud/on-premises environments"
  - "Johns Hopkins-managed infrastructure"
  # - "Microsoft Azure"
  # - "On-premises servers"
  - "Vendor/SaaS platforms"
  # - "Not applicable"
# Q26. "Other" write-in answer, if any
hosting_other: ""

# ===== Research experience =====

# Q27. Research areas. CHOOSE ALL THAT APPLY.
research_areas:
  # - "Basic science"
  - "Biomedical research"
  - "Clinical research"
  # - "Computational science"
  # - "Data science"
  # - "Education research"
  # - "Engineering"
  # - "Genomics/bioinformatics"
  # - "Humanities"
  # - "Imaging"
  # - "Multidisciplinary research"
  # - "Population health"
  # - "Public health"
  # - "Social sciences"
  # - "General/research area independent"
# Q27. "Other" write-in answer, if any
research_areas_other: ""

# Q28. Project stages. CHOOSE ALL THAT APPLY.
stages:
  # - "Early consultation / feasibility"
  # - "Grant proposal development"
  # - "Grant budgeting / cost estimates"
  - "Technical architecture/design"
  # - "Prototype/proof of concept"
  # - "Software development"
  - "Research data collection"
  # - "Research data processing/analysis"
  - "Production deployment"
  - "Ongoing maintenance/support"
  - "Project closeout"
  # - "Data/software archiving"
# Q28. "Other" write-in answer, if any
stages_other: ""

# Q29. Technical estimates for grant proposals. CHOOSE ONE.
# grant_estimates: "Yes"
grant_estimates: "Yes, on a case-by-case basis"
# grant_estimates: "No"

# Q30. Consults before funding is awarded. CHOOSE ONE.
# pre_award: "Yes"
pre_award: "Yes, on a limited basis"
# pre_award: "Depends on the project"
# pre_award: "No"

# Q31. Initial or pre-award consultation. CHOOSE ONE.
# consult_scope: "A brief conversation (about an hour or less)"
# consult_scope: "A few meetings or a short written assessment (up to about 10 hours)"
consult_scope: "Scoped case by case"
# Q31. "Other" write-in answer, if any
consult_scope_other: ""

# ===== Research data, security & compliance =====

# Q32. Data types supported. CHOOSE ALL THAT APPLY.
data_types:
  # - "Data under NIST 800-171 controls"
  # - "De-identified health information"
  # - "Genomic data"
  - "Human-subject research data"
  # - "Non-sensitive research data"
  - "Personally identifiable information (PII)"
  # - "Proprietary/confidential research data"
  - "Protected health information (PHI)"
  # - "Public data"
  # - "Restricted data"
  # - "Depends on the hosting/environment"
  # - "Unsure / requires review"
# Q32. "Other" write-in answer, if any
data_types_other: ""

# Q33. Requirements and reviews supported. CHOOSE ALL THAT APPLY.
compliance:
  # - "Accessibility requirements"
  - "Business Associate Agreements (BAAs)"
  # - "Data Use Agreements (DUAs)"
  - "HIPAA"
  - "IRB / human-subject research"
  - "Johns Hopkins IT Risk/Security review"
  # - "Research involving external collaborators"
  # - "Restricted-access research data"
  # - "None of the above"
# Q33. "Other" write-in answer, if any
compliance_other: ""

# Q34. Security and compliance approach. CHOOSE ONE.
security_approach: "Our team can lead the technical security/compliance process"
# security_approach: "Our team can assist the researcher with the process"
# security_approach: "The researcher/project team is primarily responsible"
# security_approach: "Another Hopkins group handles this for us"
# security_approach: "Varies by project"
# security_approach: "Not applicable"

# ===== Engagement model =====

# Q35. Engagement types. CHOOSE ALL THAT APPLY.
engagement_types:
  # - "Embedded technical staff"
  - "Full project delivery"
  # - "Joint/co-development with a research team"
  - "Ongoing maintenance/support"
  - "Production operations"
  # - "Prototype/proof-of-concept development"
  # - "Short-term troubleshooting"
  # - "Staff augmentation"
  # - "Technical consultation/advisory services"
# Q35. "Other" write-in answer, if any
engagement_types_other: ""

# Q36. Project sizes. CHOOSE ALL THAT APPLY.
project_sizes:
  # - "Less than 40 hours"
  # - "40-200 hours"
  - "201-500 hours"
  - "501-1,000 hours"
  # - "More than 1,000 hours"
  # - "Ongoing/long-term engagements"
  # - "No typical project size"

# Q37. Engagement duration. CHOOSE ALL THAT APPLY.
durations:
  # - "One-time consultation"
  # - "Less than 1 month"
  # - "1-3 months"
  # - "3-6 months"
  # - "6-12 months"
  - "More than 1 year"
  # - "Ongoing support"
  # - "Funding dependent"
  # - "Varies significantly"

# Q38. Takes over software from other teams. CHOOSE ONE.
# takeover: "Yes"
# takeover: "Yes, following a technical assessment"
takeover: "Case-by-case"
# takeover: "No"

# Q39. Works with the project's technical staff. CHOOSE ONE.
# collaborate: "Yes"
collaborate: "Yes, on a case-by-case basis"
# collaborate: "No"

# ===== Cost & funding =====

# Q40. Cost to researchers. CHOOSE ONE.
# cost: "No cost"
# cost: "Free initial help, then charged"
cost: "Charged"
# Q40. "Other" write-in answer, if any
cost_other: ""

# Q41. Where no-cost help ends (one line of free text)
free_limit: ""

# Q42. How charges are calculated. CHOOSE ALL THAT APPLY.
charges:
  - "Annual fee"
  # - "Cloud consumption"
  - "Fixed project price"
  # - "Hosting/infrastructure usage"
  # - "Hourly"
  # - "Monthly fee"
  # - "Percent effort / FTE on the project budget"
  # - "Software/license costs"
# Q42. "Other" write-in answer, if any
charges_other: ""

# Q43. Minimum commitment. CHOOSE ONE.
# minimum: "No minimum"
# minimum: "Less than $5,000"
minimum: "$5,000-$10,000"
# minimum: "$10,001-$25,000"
# minimum: "More than $25,000"
# minimum: "Varies by project"

# Q44. How the team is funded. CHOOSE ALL THAT APPLY.
funding:
  # - "Centrally funded"
  # - "Department-funded"
  # - "Fee-for-service"
  # - "Grant-funded"
  - "Internal cost recovery"
# Q44. "Other" write-in answer, if any
funding_other: ""

# ===== Availability & support =====

# Q45. Accepting new work. CHOOSE ONE.
accepting: "Yes"
# accepting: "Yes, with limited capacity"
# accepting: "Not at this time"

# Q46. Lead time to start. CHOOSE ONE.
# lead_time: "Less than 1 week"
# lead_time: "1-2 weeks"
# lead_time: "3-4 weeks"
lead_time: "1-2 months"
# lead_time: "More than 2 months"
# lead_time: "Varies based on project"

# Q47. Production support after launch. CHOOSE ONE.
# production_support: "Yes"
production_support: "Yes, for applications developed by our team"
# production_support: "Yes, on a separate support agreement"
# production_support: "Yes, but only for a limited time"
# production_support: "Case-by-case"
# production_support: "No"

# Q48. Support coverage. CHOOSE ALL THAT APPLY.
support_coverage:
  - "Standard Hopkins business hours"
  # - "Extended-hours support"
  - "After-hours/on-call support"
  # - "24x7 production support"
  # - "Best-effort support"
  # - "Project-specific support arrangements"
  # - "Not applicable"

# ===== Open source, software ownership & sustainability =====

# Q49. Open source support. CHOOSE ALL THAT APPLY.
open_source:
  # - "Contribute to existing open source projects"
  # - "Develop new open source software"
  # - "Prepare software for public release"
  # - "Advise on licensing, governance, or community"
  # - "Maintain software after public release"
  - "Cannot currently support open source work"
# Q49. "Other" write-in answer, if any
open_source_other: ""

# Q50. Hands off code and documentation. CHOOSE ONE.
# handoff_docs: "Yes"
handoff_docs: "Yes, depending on the engagement"
# handoff_docs: "No"
# handoff_docs: "Not applicable"

# Q51. Long-term maintenance. CHOOSE ONE.
# maintenance: "Yes"
maintenance: "Yes, for systems developed by our team"
# maintenance: "Case-by-case"
# maintenance: "No"

# ===== Additional information =====

# Q52. Good to know (free text; Markdown is fine)
notes: ""
---
We design and validate trial databases for investigator-initiated clinical trials, with HIPAA-compliant hosting and audit trails that meet FDA 21 CFR Part 11 expectations. We also train study coordinators on data entry and monitoring. Available to Johns Hopkins Health System investigators.
