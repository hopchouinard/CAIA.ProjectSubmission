# AI Questions and answers

## AI Questions

### Configuration Questions:

1. **Provider Configuration Method**: How would you prefer to configure the AI provider selection?
   - Environment variables (e.g., `AI_PROVIDER=openai`, `AI_MODEL=gpt-4o`)?
   - Configuration file (config.py or separate YAML)?
   - Database setting for runtime switching?
   - All of the above for flexibility?

2. **YAML Prompt Structure**: What structure do you envision for the prompt YAML files?
   - One file per prompt type (evaluation, improvement)?
   - One file per provider with provider-specific prompts?
   - Hierarchical structure (provider → model → prompt type)?

3. **Model-Specific Features**: How should we handle provider-specific features?
   - OpenAI thinking models (o1, o1-mini) have different parameters (no temperature, system messages)
   - Anthropic Claude models have different context windows and features
   - Should there be provider-specific prompt templates?

4. **Fallback Strategy**: What should happen if a provider fails?
   - Try next configured provider?
   - Fall back to hardcoded responses?
   - Return error to user?

5. **Existing Integration**: Should we:
   - Completely replace the current OpenAI service?
   - Create a new abstraction layer and keep OpenAI as one provider?
   - Maintain backward compatibility?

### Example Structure Questions:

Would you like something like this structure?
```
prompts/
  evaluation/
    default.yaml
    openai.yaml
    anthropic.yaml
    google.yaml
  improvement/
    default.yaml
    openai.yaml
    anthropic.yaml
config/
  providers.yaml  # Provider configurations
```

Or prefer a different organization?

6. **API Keys Management**: How should multiple API keys be handled?
   - All in .env file with different prefixes?
   - Separate config files?
   - Runtime selection?

Please let me know your preferences on these points, and I'll create a comprehensive GitHub Copilot prompt that addresses all your requirements while maintaining the application's functionality and French localization.

## AI Answers

### Configuration Answers

1. **Provider Configuration Method**
   - Support a configuration file (YAML) for easier management.
   - Allow runtime switching via database settings.
2. **YAML Prompt Structure**
   - Use a hierarchical structure for clarity: `prompts/{provider}/{model}/{prompt_type}.yaml`.
   - Each provider can have its own set of prompts.
3. **Model-Specific Features**
   - Implement provider-specific templates to handle unique features.
   - Use a common interface for prompts but allow customization per provider.
4. **Fallback Strategy**
   - Try next configured provider?
   - Return a detailed error message to the user if all else fails.
5. **Existing Integration**
   - Completely replace the current OpenAI service.
   - Create a new abstraction layer to support multiple providers.
6. **API Keys Management**
   - Use a single `.env` file with different prefixes for each provider.
   - Allow runtime selection of the active provider based on user preference or configuration.

### Example Structure

```yaml
prompts/
    openai/
        gpt-4o/
            evaluation.yaml
            improvement.yaml
        gpt-4o-mini/
            evaluation.yaml
            improvement.yaml
        o1/
            evaluation.yaml
            improvement.yaml
    anthropic/
        claude-3-5-sonnet/
            evaluation.yaml
            improvement.yaml
        claude-3-haiku/
            evaluation.yaml
            improvement.yaml
    google/
        gemini-pro/
            evaluation.yaml
            improvement.yaml
        gemini-flash/
            evaluation.yaml
            improvement.yaml
config/
    providers.yaml  # Provider configurations
```
