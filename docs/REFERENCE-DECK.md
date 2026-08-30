# Organizer Reference Deck

This file records source facts from the organizer-provided **UC Admissions Data
Challenge Slides** deck (16 slides, reviewed 2026-08-30). It is a reference
for agents and teammates, not a replacement for the challenge brief or the
organizer's live instructions.

## Source facts

### Event shape

- The event schedule shown is 11:15 start, 12:30 speech and Q&A, 1:00–2:00
  lunch, and 4:30 submission and presentation.
- The Question Sprint and Dashboard are each listed as 50% of the score.
- The deck recommends Streamlit for the dashboard and permits AI tools, while
  requiring teams to accurately present their work.
- Submissions are described as GitHub repository links in Major League
  Hacking submissions.

### Question Sprint

- The sprint consists of ten specific questions about GPA, UC campuses, and
  high schools; each answer is numeric and auto-graded.
- The deck recommends Pandas or SQL and directs teams to the datasets' README
  to select the relevant file.
- The deck's workflow is: reason through a formula, locate the CSV, work in
  Google Colab with a new code cell per problem, submit one team form, and
  preserve an `.ipynb` in the sprint repository.
- Our team records Phase 1 as complete. The answer ledger remains evidence to
  preserve and independently check, not active sprint work.

### Dashboard Construction

The deck requires or recommends the following workflow:

1. Develop a question answerable by the provided data. The question must have
   a specific time window, population of interest, and metric being measured.
2. Locate and download the relevant CSV files.
3. Answer the question in Google Colab first, using Python/Pandas, rather than
   discovering the answer inside the dashboard.
4. Build the interactive dashboard with Streamlit in a GitHub `app.py` file.
5. Deploy through `share.streamlit.io` early enough to allow for deployment
   time.
6. The deck then directs teams to create the dashboard repository, include a
   half-page `README.md` explaining methodology, submit its link through Major
   League Hacking, and prepare to present.

The deck's numbering jumps from step 5 to step 7; this record does not invent a
missing step.

### Dashboard rubric

The visible rubric lists five criteria, scored on a 1–5 scale:

1. Question: time window, population, metric
2. Finding: concise and justifiable
3. Rigor: nuanced and mature methodology
4. Dashboard: accurate and reliable
5. Presentation: well-understood and conveyed

The deck includes a slide titled “best use of gemini award,” but it does not
show detailed Gemini judging criteria. We therefore keep Gemini as a meaningful
feature target without claiming a rubric requirement that is not documented.

## Team decisions informed by the deck

- Keep the shared repository as the collaboration and evidence surface because
  the team already established it for all three tracks.
- Treat the completed Question Sprint as a separate evidence path even if the
  dashboard and Gemini feature share one Streamlit application.
- Make the final dashboard's question, time window, population, and metric
  visible on the first screen.
- Compute and verify the answer in a reproducible notebook or script before
  wiring the result into the dashboard.
- Deploy a minimal app early, then iterate on analysis and presentation.
- Use the five rubric rows as the final human review checklist.

## Still not specified by this deck

The deck does not define the final Phase 2 question, Gemini API requirements,
numeric tolerances, presentation length, deployment credentials, or whether the
organizers require separate repository links for each track. Those remain open
until confirmed by the organizers or the submission form.
