You are an expert Python Flask developer. I want to create a complete web application for managing and automatically evaluating investment projects using OpenAI GPT-4o.

## **Context and Objective**

Create a Flask application that allows users from an investment firm to submit projects that will be automatically evaluated by AI according to 6 weighted criteria. The application must classify projects into 3 priority levels and provide improvement suggestions. **All user-facing content must be in formal Quebec French.**

## **Required Technical Architecture**

### Technology Stack
- Backend: Python Flask with SQLAlchemy
- Database: SQLite
- Frontend: Angular
- AI: OpenAI GPT-4o
- Charts: Chart.js for radar chart

### Project Structure
```
project-evaluator/
├── app.py                 # Flask entry point
├── config.py             # Configuration and environment variables
├── models.py             # SQLAlchemy models
├── routes/               # Routes organized by functionality
├── services/             # Services (OpenAI, scoring, etc.)
├── templates/            # Jinja2 templates
├── static/               # CSS, JS, images
├── requirements.txt      # Python dependencies
└── .env.example         # Configuration example
```

## **Data Models**

### Project Table
- id (PK)
- titre (string, 200 chars max)
- pvp (string, department)
- contexte (text)
- objectifs (text)
- fonctionnalites (text)
- defis_techniques (text, AI-generated)
- duree_estimee (integer in days, AI-generated)
- timestamps (created_at, updated_at)

### Evaluation Table
- id (PK)
- project_id (FK)
- valeur_business (float 1-10)
- faisabilite_technique (float 1-10)
- effort_requis (float 1-10, inverted: 10 = low effort)
- niveau_risque (float 1-10, inverted: 10 = low risk)
- urgence (float 1-10)
- alignement_strategique (float 1-10)
- score_final (float, calculated)
- ai_suggestions (JSON, suggestions per criterion)
- created_at (timestamp)

## **Scoring System**

### Criteria and Weighting
| Criterion | Weight | Description | Note |
|-----------|--------|-------------|------|
| Business Value | 25% | Company impact and ROI | Higher = better |
| Technical Feasibility | 20% | Complexity and technological maturity | Higher = more feasible |
| Required Effort | 15% | Resources and time needed | Higher = less effort |
| Risk Level | 15% | Technical, legal, ethical risks | Higher = less risky |
| Urgency | 15% | Time pressure and opportunity | Higher = more urgent |
| Strategic Alignment | 10% | Consistency with objectives | Higher = better aligned |

### Calculation Formula
```
Final Score = (Value × 0.25) + (Feasibility × 0.20) + (Effort × 0.15) + 
              (Risk × 0.15) + (Urgency × 0.15) + (Alignment × 0.10)
```

### Priority Classification
- **High Priority** (≥ 7.0): Red badge, "Lancement immédiat"
- **Medium Priority** (4.0 - 6.9): Orange badge, "Planification court terme"
- **Low Priority** (< 4.0): Green badge, "Évaluation future"

## **Features to Implement**

### 1. Home Page (/)
- List of all projects sorted by descending score
- Table with: Title, PVP, Final Score, Priority, Date
- Click on row → project details
- Prominent "Nouveau Projet" button

### 2. Creation Form (/projects/new)
- **Static fields** (no evaluation):
  - Titre du projet (text input, max 200 chars)
  - PVP (dropdown with predefined departments)

- **Evaluable fields** (with "Évaluer" button):
  - Contexte d'affaires (textarea, min 100 chars)
  - Objectifs du projet (textarea, min 100 chars)
  - Fonctionnalités principales (textarea, min 100 chars)

- **Evaluation behavior**:
  - "Évaluer" button next to each evaluable field
  - On click: API call to get improvement suggestion
  - Display suggestion with "Accepter" or "Ignorer" options
  - If accepted: replace text and show confirmation

- **Final submission**:
  - "Soumettre pour évaluation complète" button
  - Automatically generates technical challenges and estimated duration
  - Calculates all scores and redirects to detail page

### 3. Detail Page (/projects/<id>)
- **Main section** (left column):
  - Title and PVP
  - Final score with priority badge
  - All project fields
  - Technical challenges (AI-generated list)
  - Estimated duration in days

- **Side panel** (right column):
  - Progress bars for each criterion
  - Visual indication for inverted scores
  - Radar chart of 6 criteria
  - "Suggestions d'amélioration" section by criterion

### 4. OpenAI Service
Create a reusable service to:
- Evaluate a complete project (returns scores + suggestions + challenges + duration)
- Improve a specific field
- Handle errors and timeouts gracefully

### 5. API Endpoints
- `POST /api/projects` - Create and evaluate a project
- `POST /api/improve-field` - Get suggestion for a field
- `GET /api/projects/<id>/reevaluate` - Reevaluate an existing project

## **User Interface**

### Design System
- Primary colors: Green (#046B67), Blue (#9AC9D3), Navy (#232C55), White (#FFFFFF), Black (#000000)
- Background colors: Light green (#E1F1EF), Light blue (#E5F3FB), Light gray (#E3E3E3), Light beige (#F5F2EF)
- Accent colors: Orange (#DC6137), Yellow (#F8C16D), Purple (#9C4174), Steel Blue (#6B90AA)
- CSS Framework: Bootstrap 5
- Font: System font stack
- Spacing: Multiples of 8px
- Border radius: 4px (inputs), 8px (cards)

### Visual Components
- **Priority badges**: Red/Orange/Green with icons
- **Progress bars**: Animated, colored by score
- **Suggestion cards**: Colored left border, slide-in animation
- **Radar chart**: Chart.js, real-time updates

### States and Feedback
- Spinners during API calls
- Clear success/error messages in French
- Subtle animations (max 0.5s)
- Tooltips to explain criteria (in French)

## **AI Integration**

### Prompts to Implement
1. **Complete evaluation**: Analyze project and return structured JSON with scores, suggestions, challenges, and duration
2. **Field improvement**: Suggest an improved version of a specific field
3. **Response format**: Always in JSON for reliable parsing

### Error Handling
- Timeout after 30 seconds
- Error messages in French
- Fallback to default values on failure

## **Technical Considerations**

### Security
- Environment variables for API keys
- Server-side validation of all inputs
- CSRF protection for forms

### Performance
- Pagination for project list (if > 20)
- Cache evaluations (don't reevaluate if unchanged)
- Asynchronous loading of suggestions

### User Experience
- **Entire interface in formal Quebec French**
- Auto-save in sessionStorage during input
- Intuitive navigation with breadcrumbs
- Desktop responsive (min 1200px)

## **Expected Deliverables**

1. Complete and functional source code
2. Setup instructions in README.md
3. .env.example file with all necessary variables
4. SQLite database initialized with tables
5. At least 2-3 example projects for demonstration

## **Success Criteria**

- Application must allow creating, evaluating, and prioritizing projects
- OpenAI integration must work for all use cases
- Interface must be professional and intuitive
- Scoring and classification system must be accurate
- Improvement suggestions must be relevant and actionable
- All user-facing content must be in formal Quebec French

Start by creating the project structure and base models, then progressively implement each feature while testing as you go.

## **Important Language Requirements**

- All UI elements, labels, buttons, messages, tooltips, and error messages must be in formal Quebec French
- Use "vous" form throughout the application
- Number formatting: Space for thousands (1 000), comma for decimals (1,5)
- Currency format: 1 000,50 $ CAD
- Date format: AAAA-MM-JJ
- Professional business tone for all text

## **French UI Text Examples**

- Button labels: "Nouveau Projet", "Évaluer", "Soumettre", "Accepter", "Ignorer"
- Form labels: "Titre du projet", "Contexte d'affaires", "Objectifs du projet"
- Messages: "Évaluation en cours...", "Projet créé avec succès", "Erreur lors de l'évaluation"
- Priority levels: "Priorité Élevée", "Priorité Moyenne", "Priorité Faible"
- Table headers: "Titre", "Département", "Score Final", "Priorité", "Date de création"

Use all the tools at your disposal to create a robust, user-friendly application that meets the requirements outlined above. Ensure that the code is clean, well-documented, and follows best practices for Flask development.
