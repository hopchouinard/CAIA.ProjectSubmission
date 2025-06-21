# GitHub Copilot Agent Mode: Multi-Provider AI Service Refactoring

## Project Context
You are working on a Flask application called "Évaluateur de Projets d'Investissement" (Investment Project Evaluator) that currently uses only OpenAI for AI-powered project evaluation. The application evaluates investment projects using 6 weighted criteria and provides improvement suggestions in formal Quebec French.

## Current Architecture Overview
- Flask web application with SQLAlchemy
- Single OpenAI service in `services/openai_service.py`
- Hard-coded prompts in Python code
- SQLite database with Project and Evaluation models
- French Quebec localization throughout

## Refactoring Objective
Transform the application to support multiple AI providers (OpenAI, Anthropic, Google, Azure OpenAI, Databricks) with configurable models and externalized YAML prompts, while maintaining all existing functionality and French localization.

## Required Architecture Changes

### 1. New Service Architecture
Create a new multi-provider service architecture replacing the current `services/openai_service.py`:

```
services/
├── ai_service.py           # Main service interface (replaces openai_service.py)
├── providers/
│   ├── __init__.py
│   ├── base_provider.py    # Abstract base class
│   ├── openai_provider.py  # OpenAI implementation
│   ├── anthropic_provider.py
│   ├── google_provider.py
│   ├── azure_provider.py
│   └── databricks_provider.py
├── prompt_manager.py       # YAML prompt loading/management
└── provider_manager.py     # Provider selection/fallback logic
```

### 2. YAML Prompt Externalization
Create hierarchical prompt structure:

```
prompts/
├── openai/
│   ├── gpt-4.1/
│   │   ├── evaluation.yaml
│   │   └── improvement.yaml
│   ├── gpt-4.1-mini/
│   │   ├── evaluation.yaml
│   │   └── improvement.yaml
│   ├── o3/ # Thinking model - special handling needed
│   │   ├── evaluation.yaml
│   │   └── improvement.yaml
│   └── o4-mini/
│       ├── evaluation.yaml
│       └── improvement.yaml
├── anthropic/
│   ├── claude-4-sonnet/
│   │   ├── evaluation.yaml
│   │   └── improvement.yaml
│   ├── claude-3.5-haiku/
│   │   ├── evaluation.yaml
│   │   └── improvement.yaml
│   └── claude-4-opus/
│       ├── evaluation.yaml
│       └── improvement.yaml
├── google/
│   ├── gemini-2.5-pro/
│   │   ├── evaluation.yaml
│   │   └── improvement.yaml
│   └── gemini-2.5-flash/
│       ├── evaluation.yaml
│       └── improvement.yaml
├── azure/
│   └── gpt-4o/
│       ├── evaluation.yaml
│       └── improvement.yaml
└── databricks/
    └── meta-llama/
        ├── evaluation.yaml
        └── improvement.yaml
```

### 3. Configuration System
Create `config/providers.yaml` with provider definitions and add database model for runtime configuration:

```python
class AIProviderConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 4. Environment Variables
Update `.env.example` to support multiple providers with prefixed API keys:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key
OPENAI_ORG_ID=optional-org-id

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Google Configuration
GOOGLE_API_KEY=your-google-api-key
GOOGLE_PROJECT_ID=your-project-id

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Databricks Configuration
DATABRICKS_TOKEN=your-databricks-token
DATABRICKS_HOST=your-databricks-host

# Default Provider Configuration
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=gpt-4o
ENABLE_PROVIDER_FALLBACK=true
```

## Implementation Requirements

### Core Functionality Preservation
- **CRITICAL**: All existing functionality must remain identical
- Same API endpoints and responses
- Same user interface behavior
- Same evaluation criteria and scoring
- Same French Quebec localization
- No breaking changes to existing projects

### Provider-Specific Features
Handle model-specific requirements:
- **OpenAI o3/o4-mini**: No system messages, no temperature parameter, thinking models
- **OpenAI standard models**: Full parameter support
- **Anthropic Claude**: Different API structure and parameters
- **Google Gemini**: Different API endpoints and authentication
- **Azure OpenAI**: Different base URLs and authentication
- **Databricks**: Custom endpoints and token authentication

### YAML Prompt Structure
Each prompt file should include:
```yaml
metadata:
  provider: "openai"
  model: "gpt-4.1"
  prompt_type: "evaluation"
  version: "1.0"
  language: "fr-CA"

system_message: |
  [System message content in formal Quebec French]

user_prompt_template: |
  [User prompt template with {variable} placeholders]

parameters:
  temperature: 0.7
  max_tokens: 2000
  top_p: 1.0
```

### Fallback Strategy
Implement provider fallback logic:
1. Try primary configured provider
2. Try secondary providers in priority order
3. Return detailed French error message if all fail
4. Maintain fallback evaluation for complete failures

### Database Integration
- Add migration for new AIProviderConfig model
- Implement runtime provider switching
- Allow per-user or per-project provider preferences
- Maintain provider usage statistics

## Technical Specifications

### Base Provider Interface
Create abstract base class all providers must implement:
- `evaluate_project(project_data, prompt_template) -> Dict[str, Any]`
- `improve_field(field_name, field_content, project_context, prompt_template) -> str`
- `supports_feature(feature) -> bool`
- `get_available_models() -> List[str]`

### Error Handling
- Provider-specific exception handling
- Detailed logging for debugging
- User-friendly French error messages
- Graceful degradation when providers fail

### Performance Considerations
- Cache loaded YAML prompts
- Efficient provider selection
- Connection reuse where possible
- Async support for multiple provider attempts

### Dependencies to Add
Update `requirements.txt`:
```
anthropic>=0.52.2
google-genai>=1.21.1
databricks-sdk>=0.57.0
PyYAML>=6.0
```

## Migration Strategy

### Code Changes Required
1. Replace all imports of `OpenAIService` with new `AIService`
2. Update `routes/main.py` and `routes/api.py` to use new service
3. Migrate existing hard-coded prompts to YAML files
4. Add database migration for new model
5. Update configuration loading in `config.py`

### Backward Compatibility
- Existing projects must continue to work
- Existing API responses must remain identical
- Current evaluation scoring must be preserved
- French localization must be maintained

### Testing Requirements
- Test each provider implementation
- Test fallback mechanisms
- Test prompt loading and variable substitution
- Test provider switching
- Test model-specific feature handling
- Verify French localization preserved

## Deliverables Expected

1. **Complete provider abstraction layer** with base class and all provider implementations
2. **All YAML prompt templates** for each provider/model combination
3. **Updated configuration system** with providers.yaml and database model
4. **Database migration script** for new AIProviderConfig table
5. **Updated routes and services** to use new architecture
6. **Updated requirements.txt** with new dependencies
7. **Updated .env.example** with all provider configurations
8. **Documentation** explaining how to add new providers
9. **Migration guide** for existing installations

## Success Criteria

- Application functions identically to current version
- Can switch providers via configuration
- Prompts are externalized and easily editable
- All supported providers work correctly
- Fallback system functions properly
- French localization maintained throughout
- No performance degradation
- Easy to add new providers in the future

## Important Notes

- **Preserve French Quebec localization**: All user-facing text must remain in formal Quebec French
- **Maintain evaluation criteria**: The 6 criteria and their weights must remain identical
- **Keep scoring system**: The priority classification system must be preserved
- **No UI changes**: The user interface should remain identical
- **API compatibility**: All existing API endpoints must work unchanged

Start by creating the base provider architecture, then implement each provider, create the YAML prompt templates, and finally integrate everything while ensuring complete backward compatibility.
