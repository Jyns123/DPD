# DS3022 - Desarrollo de Producto de Datos

## Universidad de Ingeniería y Tecnología

## Prof. Germain Garcia-Zanabria

#### Data Science Program

#### Final Project Guidelines

#### <u>DS3022-DPD Final Project Guidelines</u>

## 1 Project Overview

The final project will offer practical experience in the design, implementation, and deployment of a data product. Your project should address a concrete challenge and propose a novel and creative data-driven solution. The final product will take the form of an interactive platform or an application.

### 1.1 Overall mechanism and infraestructure

**TeamWork.** You will work on this project in your “assigned” teams. As a team, you will use a shared GitHub repository to coordinate your work. I expect that team members will have different backgrounds and different amounts of experience with machine learning and software engineering – this is intentional. As a team members I hope you will fill missing gaps in background knowledge, and teach each other about tools and practices that are effective for this task. I expect that all team members make every effort to be a good team citizen (attend meetings, prepared and cooperative, respect for other team members, work on assigned and agreed tasks by agreed deadlines, reaching out to team members when delays are expected, etc). For this edition of Data Product Development, each project team should consist of **4 members** (A group with 3 members). **Topic:** The topic for this semester’s final project is **OPEN**. Consider how a data product could help optimize or achieve the company’s objectives. Your project must be based on one or more datasets (publicly available or private). You are free to choose any specific domain of interest. There are many interesting topics including health, transportation, economic development, climate, migration, humanitarian aid, legislative voting records, and scientific research. If using publicly available datasets, identify a target audience, which can be general (residents, voters) or specialized (scientists, policymakers). If using private datasets, provide documentation (emails, letters, photos, etc.) demonstrating authorization for data use. Each group will be responsible for presenting their results. During the last week (Week

15), there will be a public exhibition where you can share your work with peers and special guests.
## 2 Project Milestones

The project will be developed from Week 4 through Week 15. Each milestone is a checkpoint intended to provide evidence of progress and enable formative feedback. Unless otherwise announced, all milestone deliverables are due on the specified Wednesday through the course platform. This semester, the project includes two major graded submissions: **Delivery 1 (Week**

**7)** and **Delivery 2 (Week 15)**. All teams must maintain a shared GitHub or GitLab repository throughout the project. Each milestone must be stored in a folder following the naming convention deliveries/weekXX/. Depending on the milestone, submissions may include reports, presentations, data files, source code, diagrams, model artifacts, prototypes, videos, and supporting documentation.

#### Week 4: Topic, Team, and Dataset Selection (September 2, 2026)

Each team must define an initial project topic, form a team, and identify one or more candidate datasets. The objective is to demonstrate that the data are accessible, sufficiently rich, and potentially useful for developing a Data Product. **Deliverable:** A repository folder named deliveries/week04/ containing:

- README.md: team members, tentative product name, initial problem or oppor- tunity, target domain, and dataset source;
- data/: the available dataset in CSV format whenever possible;
- data/sample.csv: a representative sample when the complete dataset is too large, restricted, obtained through an API, or distributed in another format;
- data_dictionary.csv: attribute name, description, data type, format or unit, possible values, and missing-value codes;
- acquisition.md or an acquisition script describing how the complete data can be obtained;
- a brief data-quality note describing missing values, duplicate records, incon- sistent data types, suspicious values, and known limitations.
Do not upload private, confidential, personally identifiable, copyrighted, or otherwise restricted data to a public repository. When necessary, provide a legally shareable sample and document the corresponding access restrictions.

#### Week 5: Project Proposal, Data Product Canvas, and Requirements

#### (September 9, 2026)

Each team must define the proposed Data Product more precisely. The proposal should present a descriptive product name, abstract, background, problem statement, target users, expected value, and initial product scope. Teams must also complete an initial **Data Product Canvas** and conduct a requirements elicitation activity based on the concepts introduced in *Guía 3*. The requirements should identify stakeholders, user needs, functional requirements, non-functional requirements, assumptions, constraints, and acceptance criteria. **Deliverable:** A repository folder named deliveries/week05/ containing:

- ProjectProposal.pdf: a concise project proposal;
- the editable proposal source in .tex, .docx, or an equivalent source format;
- DataProductCanvas.pdf: the completed Data Product Canvas;
- Requirements.pdf or Requirements.md: stakeholders, user needs, functional requirements, non-functional requirements, constraints, and acceptance criteria;
- PresentationWeek05.pptx or PresentationWeek05.pdf;
- an updated README.md containing the working title, team members, responsibilities, repository structure, and relevant links.

#### Week 6: Exploratory Data Analysis and Model Selection (September 16,

#### 2026)

Each team must conduct an exploratory analysis of the selected data and propose the analytical or modeling component of the Data Product. The exploratory analysis should describe the structure and quality of the data, preprocessing decisions, relevant distributions and relationships, initial findings, potential biases, and the main data-related challenges. The modeling proposal should identify the expected inputs and outputs, justify the selected analytical method, define at least one baseline alternative, and describe the preliminary evaluation strategy. A complex machine-learning model is not required when a simpler analytical method is more appropriate for the product. **Deliverable:** A repository folder named deliveries/week06/ containing:

- DataAnalysis.pdf or DataAnalysis.md: data understanding, preprocessing, exploratory analysis, findings, and limitations;
- ModelSelection.pdf or ModelSelection.md: proposed method, baseline al- ternatives, expected inputs and outputs, justification, and evaluation criteria;
- PresentationWeek06.pptx or PresentationWeek06.pdf;
- data/processed/: the processed CSV or JSON files used in the analysis;
- code/: scripts or notebooks used for cleaning, transformation, analysis, and preliminary modeling;
- an updated data dictionary and reproducibility instructions.
#### Week 7: Delivery 1 – Integrated Project Definition (September 23, 2026)

Delivery 1 consolidates the first phase of the project. It must demonstrate that the team has defined a relevant Data Product, understood the available data, identified its users and requirements, selected an appropriate analytical approach, and designed an initial product concept. The submission should include:

- the revised problem definition, background, and value proposition;
- the final first-phase Data Product Canvas;
- target users, stakeholders, user needs, and requirements;
- the dataset description, data dictionary, preprocessing process, and exploratory analysis;
- the selected analytical or modeling approach and baseline;
- an initial product architecture, workflow, or system diagram;
- interface sketches, wireframes, or a low-fidelity prototype;
- a prioritized implementation plan and division of responsibilities through Week
15.
**Deliverable:** A repository folder named deliveries/week07/ containing:

- Delivery1Report.pdf and its editable source;
- PresentationWeek07.pptx or PresentationWeek07.pdf;
- DataProductCanvas.pdf;
- Requirements.pdf or Requirements.md;
- the processed data in CSV or JSON format;
- all preprocessing, analysis, and preliminary modeling code;
- architecture diagrams, workflows, sketches, and wireframes in PDF or PNG format;
- an updated root README.md with responsibilities, repository structure, execution instructions, and project schedule.
#### Week 8: No Project Deliverable

Week 8 has no project deliverable due to the Midterm Exam. Teams should use the feedback received during Delivery 1 to refine the project scope and prepare the implementation phase. **Week 10: Functional Prototype (October 14, 2026)** Each team must present an initial functional version of the Data Product. The prototype should integrate the principal workflow, interface, data-processing pipeline, and analytical or modeling component. The prototype does not need to have final styling or complete functionality, but the main product flow must be demonstrable using real or representative project data. **Deliverable:** A repository folder named deliveries/week10/ containing:

- the complete prototype source code;
- the current processed data in CSV or JSON format;
- serialized model files or other analytical artifacts when applicable;
- PrototypeReport.pdf or PrototypeReport.md: implemented features, system architecture, known limitations, technical challenges, and remaining work;
- PresentationWeek10.pptx or PresentationWeek10.pdf;
- screenshots or a short demonstration video;
- a deployed prototype URL when publication is technically and legally possible;
- README.md with setup, execution, dependencies, and deployment instructions.
#### Week 12: Refined Prototype, Evaluation, and Case Studies (October 28,

#### 2026)

Each team must present a substantially refined version of the Data Product. The product should integrate its major components and demonstrate improved functionality, usability, reliability, and consistency. Teams must also present their evaluation strategy, selected metrics, validation results, and at least one realistic case study showing how a target user would use the product. **Deliverable:** A repository folder named deliveries/week12/ containing:

- the refined product source code and updated deployment link;
- the final-candidate processed data and reproduction scripts;
- EvaluationReport.pdf or EvaluationReport.md: metrics, validation strategy, baseline comparison, results, limitations, and case studies;
- PresentationWeek12.pptx or PresentationWeek12.pdf;
- updated architecture, workflow, and interface documentation;
- evidence of testing, such as test cases, metric outputs, usability observations, or error analyses;
- an updated README.md;
- a final task and responsibility plan for the remaining three weeks.
#### Week 15: Final Presentation (November 18, 2026)

Each team will give a final public presentation of the complete Data Product. The presentation must explain the problem, target users, value proposition, data, requirements, product architecture, analytical approach, evaluation results, case studies, limitations, and final product demonstration. The duration and presentation order will be announced by the instructor.

#### Week 15: Delivery 2 – Final Submission (November 18, 2026)

Delivery 2 is the complete and reproducible final submission of the Data Product. **Deliverable:** The final repository and project page must include:

- the complete and functional Data Product;
- all source code required to build and run the product;
- final data files in CSV or JSON format, or legally compliant data acquisition instructions;
- preprocessing, analysis, training, inference, and evaluation scripts;
- model files or analytical artifacts when applicable;
- FinalReport.pdf and its editable source;
- PresentationFinal.pptx or PresentationFinal.pdf;
- a final demo video;
- the final Data Product Canvas;
- the final requirements specification;
- final architecture and workflow diagrams;
- evaluation results, baseline comparisons, and case studies;
- a project page containing the product description, team members, representative image, demonstration video, execution instructions, and relevant links;
- a complete README.md with installation, execution, dependencies, data sources, model information, deployment link, known limitations, and troubleshooting instructions;

- a contribution statement describing how the work was divided among team members;
- a brief reflection on the product development process.
The teaching team must be able to reproduce or run the submitted product by following the repository documentation. Do not include credentials, private keys, restricted data, or undocumented dependencies.

## 3 Final Presentation Structure

Your presentation should be given before a jury. Students may be as creative as they wish. Each team member must participate in the presentation. Suggested structure:

**Problem Statement**: Briefly describe the problem addressed, general motivation, and input/output of the problem. **Challenges**: Briefly describe why the problem is technically challenging. **Related Work**: Explain how previous works have addressed these challenges. **Your Approach and Results**: Describe your technical approach, innovations, and evaluation results (datasets and metrics). Highlight significant, interesting, or unexpected results and explain them compared to previous findings. **Broader Impact**: Describe the expected impact, lessons for others, applicability, limitations, and areas for future improvement.

## 4 Submission Requirements

The final submission must include the following components:

**Documentation and Report:** Provide complete project documentation in Mark- down format. The report must describe the problem, target users, data sources, data preparation, requirements, modeling or analytical approach, product design, prototyping process, evaluation, results, limitations, and conclusions. **Code and Repository:** Provide a link to a GitHub or GitLab repository containing all source code, scripts, configuration files, dependencies, and documentation required to reproduce, execute, and evaluate the project. The repository must include a complete README.md with installation and execution instructions. **Data and Reproducibility Materials:** Include the datasets used in the project, such as training, validation, and test sets when applicable, as well as metadata, data dictionaries, experimental results, evaluation outputs, and relevant logs. Include all scripts required to acquire, clean, transform, and partition the data. **Project Presentation:** Prepare the final presentation using PowerPoint, Keynote, or another compatible presentation tool. Submit both the editable presentation file and an exported PDF. Include the presentation files in the project repository and submit the corresponding link through Canvas.

**Demo Video:** Create a 5–7 minute video presenting the project and demonstrating the final Data Product. The video should explain the problem, target users, data, principal product features, analytical or modeling approach, evaluation results, and limitations. Upload the video to YouTube or another accessible platform and include the link in the report, project page, and repository.

**Team Contribution Statement:** Include a brief description of how the work was divided among the team members. The statement should identify each member’s principal contributions to the data, requirements, modeling, implementation, evaluation, documentation, and presentation.

**Reflection on teamwork:** Reflect on your team’s teamwork throughout this project. The following questions may guide your reflection: What went well or less well in the team assignments? What were some of the main challenges you faced in teamwork? If you had to do this over, what would you change? What lesson have you identified for future team projects? This reflection will be posted on Canvas.

## 5 Inspiration

The goal is for projects to improve each semester. Refer to the previous semester’s presentations provided by the instructor to inspire and observe progress made by past students.

video 1

video 2

Video 3

Folder 1

Folder 2

Folder 3

***Note*: These recordings are exclusively for use within the Data Product**

#### Development Course. Please use them responsibly.

## 6 Social Activities Bonus

I hope that the following can encourage some social interaction that goes beyond the technical parts of the team project. **This is entirely optional**. Team members can earn bonus points if they engage in a IN-PERSON social activity with their team that is not related to any coursework. This could just be an informal happy hour, playing a board game or computer game together, do a puzzle or trivia quiz, watch a movie, or whatever you like, as long as it is not course related. If you do, send evidence (selfie until the end of Friday of week 15) tagging all team members who participated (who should all be visible in the selfie). Just taking a selfie outside the classroom does not count; do some recognizable social activity. You can also join forces with other teams if you are looking for some friendly competition, no constraints.