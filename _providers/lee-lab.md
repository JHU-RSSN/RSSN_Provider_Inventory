---
# RSSN provider listing, from the RSSN Service Provider Inventory questionnaire (2026 Qualtrics version).
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

# Links this listing to its questionnaire response. Please don't change it.
form_response_id: "R_6p35ZRCBwjl17l7"

# Q10. Team or service name, as researchers should see it
title: "Lee Lab"

# Q8. Institution. CHOOSE ONE.
institution: "JHU"
# institution: "JHHS"
# institution: "Joint JHU/JHHS"

# Q9. School, division, or central office. CHOOSE ONE, or if yours isn't listed,
# write it on its own line the same way. Listed ones get a colored card accent.
# school: "Academic and Business Centers"
# school: "Applied Physics Laboratory"
# school: "Bloomberg School of Public Health"
# school: "Carey Business School"
# school: "Johns Hopkins IT"
# school: "JHTV"
school: "Krieger School of Arts and Sciences"
# school: "University Libraries and Museums"
# school: "Peabody Institute"
# school: "School of Advanced International Studies"
# school: "School of Education"
# school: "School of Government and Policy"
# school: "School of Medicine"
# school: "School of Nursing"
# school: "University Administration"
# school: "University Student Services"
# school: "Whiting School of Engineering"
# Department or unit within that school (free text)
unit: "Krieger School of Arts & Sciences, Mind/Brain Institute"

# Q11. Website or service information URL (optional)
website: "https://sites.krieger.jhu.edu/daeyeol-lee-lab https://github.com/leelab"

# Q4-5. Primary contact, shown on the public site
contact:
  name: "Daniel Mittler"
  email: "dmittle2@jh.edu"

# Date this listing was last reviewed (YYYY-MM-DD)
updated: 2026-10-22

# ===== Who you support =====

# Q12. Team type. CHOOSE ONE.
# team_type: "Research support service"
team_type: "Research group sharing expertise"
# team_type: "IT service with research support"
# Q12. "Other" write-in answer, if any
team_type_other: ""

# Q13. Available to. CHOOSE ONE.
# availability: "Hopkins-wide"
# availability: "JHU only"
# availability: "JHHS only"
# availability: "Certain schools/divisions"
availability: "Own department/unit only"
# availability: "It's complicated"

# Q20. Availability details (free text; Markdown is fine)
availability_details: ""

# Q14. Who can engage this team. CHOOSE ALL THAT APPLY.
eligible:
  # - "Cross-institution JHU/JHHS projects"
  # - "JHHS faculty"
  # - "JHHS staff"
  # - "JHU faculty"
  # - "JHU staff"
  # - "JHU students/trainees working on sponsored research"
  # - "Johns Hopkins research centers/institutes"
  # - "Other Johns Hopkins-affiliated groups"
  # - "Projects involving external research collaborators"
# Q14. "Other" write-in answer, if any
eligible_other: ""

# ===== Services & expertise =====

# Q16-19. Services. After each service write: not offered, offered, or strength.
# strength = offered AND an area of strength. No more than 5 strengths in all.
services:
  # Software Development and Engineering
  "AI-Assisted Coding":                                    offered
  "Python or R Package Development":                       offered
  "UX, Accessibility & Software Quality":                  not offered
  "Version Control & Collaboration":                       strength
  "Web & Application Development":                         not offered
  # Data, AI, and Analytics
  "Data Pipeline Automation":                              strength
  "Databases":                                             offered
  "Machine Learning Operations":                           not offered
  "Machine Learning/AI Development":                       not offered
  "Reproducible Research Workflows":                       offered
  # Computing and Infrastructure
  "Containerization & Cloud Computing":                    not offered
  "DevOps & Infrastructure Operations":                    not offered
  "High-performance computing (HPC) / Parallel computing": offered
  "IT Security & Compliance":                              offered
  # Consulting, Training, and Sustainability
  "Domain/Subject-Matter Expertise":                       not offered
  "Open Source Licensing & Sustainability":                offered
  "Technical Consulting & Solution Architecture":          not offered
  "Technical Documentation & Training":                    offered

# Q21. Other services or expertise (free text; Markdown is fine)
services_other: ""

# Q22. Example projects (free text; Markdown is fine)
examples: |
  I maintain Picto, a software suite for behavioral experiments with non-human primates.

  https://github.com/leelab/picto-public

# ===== Technical capabilities =====

# Q24. Does hands-on technical work. CHOOSE ONE.
hands_on: "Yes"
# hands_on: "No"

# Q25. Languages and development technologies. CHOOSE ALL THAT APPLY (leave all unselected if Q24 is "No").
languages:
  # - "Angular"
  # - "C / C++"
  # - "C# / .NET"
  # - "Java"
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
  # - "SQL"
  # - "Stata"
  # - "Swift / iOS"
  # - "Vue"
  # - "Not applicable"
# Q25. "Other" write-in answer, if any
languages_other: "C / C++,MATLAB,Python"

# Q26. Databases. CHOOSE ALL THAT APPLY (leave all unselected if Q24 is "No").
databases:
  # - "Azure SQL"
  # - "Cloud-native databases"
  # - "Microsoft SQL Server"
  # - "MongoDB"
  # - "MySQL / MariaDB"
  # - "Other NoSQL databases"
  # - "Oracle"
  # - "PostgreSQL"
  - "Not applicable"
# Q26. "Other" write-in answer, if any
databases_other: ""

# Q27. Infrastructure and DevOps. CHOOSE ALL THAT APPLY (leave all unselected if Q24 is "No").
devops:
  # - "Amazon Elastic Kubernetes Services (EKS)"
  # - "Azure DevOps"
  # - "Azure Kubernetes Service (AKS)"
  # - "Docker"
  - "GitHub"
  # - "GitHub Actions"
  # - "Jenkins"
  # - "Kubernetes"
  # - "Monitoring / logging platforms"
  # - "Singularity / Apptainer"
  # - "Terraform"
  # - "Other Infrastructure-as-Code tools"
  # - "Not applicable"
# Q27. "Other" write-in answer, if any
devops_other: ""

# Q28. Computing and hosting environments. CHOOSE ALL THAT APPLY (leave all unselected if Q24 is "No").
hosting:
  # - "Amazon Web Services (AWS)"
  # - "Containerized environments"
  - "High-performance computing (HPC) / Parallel computing"
  # - "Hybrid cloud / on-premises environments"
  # - "Johns Hopkins-managed infrastructure"
  # - "Microsoft Azure"
  # - "On-premises servers"
  # - "Vendor / SaaS platforms"
  # - "Not applicable"
# Q28. "Other" write-in answer, if any
hosting_other: ""

# ===== Research experience =====

# Q29. Research areas. CHOOSE ALL THAT APPLY.
research_areas:
  - "Basic science"
  # - "Biomedical research"
  # - "Clinical research"
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
  # - "General (not specific to a research area)"
# Q29. "Other" write-in answer, if any
research_areas_other: ""

# Q30. Project stages. CHOOSE ALL THAT APPLY.
stages:
  # - "Early consultation / feasibility"
  # - "Grant proposal development"
  # - "Grant budgeting / cost estimates"
  - "Technical architecture/design"
  # - "Prototype / proof-of-concept development"
  # - "Software development"
  # - "Research data collection"
  # - "Research data processing/analysis"
  # - "Production deployment"
  # - "Ongoing maintenance/support"
  # - "Project closeout"
  # - "Data/software archiving"
# Q30. "Other" write-in answer, if any
stages_other: ""

# Q31. Technical estimates for grant proposals. CHOOSE ONE.
# grant_estimates: "Yes"
# grant_estimates: "Yes, on a case-by-case basis"
grant_estimates: "No"

# Q32. Consults before funding is awarded. CHOOSE ONE.
# pre_award: "Yes"
# pre_award: "Yes, on a limited basis"
# pre_award: "Yes, on a case-by-case basis"
pre_award: "No"

# Q33. Initial or pre-award consultation. CHOOSE ONE.
# consult_scope: "A brief conversation (about an hour or less)"
# consult_scope: "A few meetings or a short written assessment (up to about 10 hours)"
# consult_scope: "Scoped case-by-case"
# Q33. "Other" write-in answer, if any
consult_scope_other: ""

# ===== Research data, security & compliance =====

# Q34. Data types supported. CHOOSE ALL THAT APPLY.
data_types:
  # - "Data under NIST 800-171 controls"
  # - "De-identified health information"
  # - "Genomic data"
  # - "Human-subject research data"
  - "Non-sensitive research data"
  # - "Personally identifiable information (PII)"
  # - "Proprietary / confidential research data"
  # - "Protected health information (PHI)"
  # - "Public data"
  # - "Restricted data"
  # - "Depends on the hosting / environment"
  # - "Unsure / requires review"
# Q34. "Other" write-in answer, if any
data_types_other: ""

# Q35. Requirements and reviews supported. CHOOSE ALL THAT APPLY.
compliance:
  # - "Accessibility requirements"
  # - "Business Associate Agreements (BAAs)"
  # - "Data Use Agreements (DUAs)"
  # - "HIPAA"
  # - "IRB / human-subject research"
  # - "Johns Hopkins IT Risk / Security review"
  - "Projects involving external collaborators"
  # - "Restricted-access research data"
  # - "None of the above"
# Q35. "Other" write-in answer, if any
compliance_other: ""

# Q36. Security and compliance approach. CHOOSE ONE.
# security_approach: "Our team can lead the technical security/compliance process"
# security_approach: "Our team can assist the researcher with the process"
# security_approach: "The researcher/project team is primarily responsible"
# security_approach: "Another Johns Hopkins group handles this for us"
# security_approach: "Varies by project"
security_approach: "Not applicable"

# ===== Engagement model =====

# Q37. Engagement types. CHOOSE ALL THAT APPLY.
engagement_types:
  # - "Embedded technical staff"
  - "Full project delivery"
  # - "Joint / co-development with a research team"
  # - "Ongoing maintenance/support"
  # - "Production operations"
  # - "Prototype / proof-of-concept development"
  # - "Short-term troubleshooting"
  # - "Staff augmentation"
  # - "Technical consultation / advisory services"
# Q37. "Other" write-in answer, if any
engagement_types_other: ""

# Q38. Project sizes. CHOOSE ALL THAT APPLY.
project_sizes:
  # - "Less than 40 hours"
  # - "40–200 hours"
  # - "201–500 hours"
  # - "501–1,000 hours"
  # - "More than 1,000 hours"
  - "Ongoing / long-term engagements"
  # - "No typical project size"

# Q39. Engagement duration. CHOOSE ALL THAT APPLY.
durations:
  # - "One-time consultation"
  # - "Less than 1 month"
  # - "1 to under 3 months"
  # - "3 to under 6 months"
  # - "6 to 12 months"
  # - "More than 1 year"
  - "Ongoing support"
  # - "Funding dependent"
  # - "Varies by project"

# Q40. Takes over software from other teams. CHOOSE ONE.
takeover: "Yes"
# takeover: "Yes, following a technical assessment"
# takeover: "Yes, on a case-by-case basis"
# takeover: "No"

# Q41. Works with the project's technical staff. CHOOSE ONE.
collaborate: "Yes"
# collaborate: "Yes, on a case-by-case basis"
# collaborate: "No"

# ===== Cost & funding =====

# Q42. Cost to researchers. CHOOSE ONE.
cost: "No cost"
# cost: "Free initial help, then charged"
# cost: "Charged"
# Q42. "Other" write-in answer, if any
cost_other: ""

# Q43. Where no-cost help ends (one line of free text)
free_limit: ""

# Q44. How charges are calculated. CHOOSE ALL THAT APPLY.
charges:
  # - "Annual fee"
  # - "Cloud consumption"
  # - "Fixed project price"
  # - "Hosting/infrastructure usage"
  # - "Hourly"
  # - "Monthly fee"
  # - "Percent effort / FTE on the project budget"
  # - "Software/license costs"
# Q44. "Other" write-in answer, if any
charges_other: ""

# Q45. Minimum commitment. CHOOSE ONE.
# minimum: "No minimum"
# minimum: "Less than $5,000"
# minimum: "$5,000–$10,000"
# minimum: "$10,001–$25,000"
# minimum: "More than $25,000"
# minimum: "Varies by project"

# Q46. How the team is funded. CHOOSE ALL THAT APPLY.
funding:
  # - "Centrally funded"
  # - "Department-funded"
  # - "Fee-for-service"
  # - "Grant-funded"
  # - "Internal cost recovery"
# Q46. "Other" write-in answer, if any
funding_other: "grants"

# ===== Availability & support =====

# Q47. Accepting new work. CHOOSE ONE.
# accepting: "Yes"
accepting: "Yes, with limited capacity"
# accepting: "Not at this time"

# Q48. Lead time to start. CHOOSE ONE.
# lead_time: "Less than 1 week"
# lead_time: "1–2 weeks"
# lead_time: "2–4 weeks"
# lead_time: "1–2 months"
# lead_time: "More than 2 months"
lead_time: "Varies by project"

# Q49. Production support after launch. CHOOSE ONE.
# production_support: "Yes"
production_support: "Yes, for applications developed by our team"
# production_support: "Yes, on a separate support agreement"
# production_support: "Yes, but only for a limited time"
# production_support: "Yes, on a case-by-case basis"
# production_support: "No"

# Q50. Support coverage. CHOOSE ALL THAT APPLY.
support_coverage:
  # - "Standard Johns Hopkins business hours"
  # - "Extended-hours support"
  # - "After-hours/on-call support"
  # - "24x7 production support"
  # - "Best-effort support"
  # - "Project-specific support arrangements"
  - "Not applicable"

# ===== Open source, software ownership & sustainability =====

# Q51. Open source support. CHOOSE ALL THAT APPLY.
open_source:
  - "Contribute to existing open source projects"
  # - "Develop new open source software"
  # - "Prepare software for public release"
  # - "Advise on licensing, governance, or community"
  # - "Maintain software after public release"
  # - "Cannot currently support open source work"
# Q51. "Other" write-in answer, if any
open_source_other: ""

# Q52. Hands off code and documentation. CHOOSE ONE.
# handoff_docs: "Yes"
# handoff_docs: "Yes, depending on the engagement"
# handoff_docs: "No"
handoff_docs: "Not applicable"

# Q53. Long-term maintenance. CHOOSE ONE.
maintenance: "Yes"
# maintenance: "Yes, depending on the engagement"
# maintenance: "No"
# maintenance: "Not applicable"

# ===== Additional information =====

# Q54. Good to know (free text; Markdown is fine)
notes: |
  I can only provide advice and limited help to anyone outside of my lab.
---
My "team" is just me.
