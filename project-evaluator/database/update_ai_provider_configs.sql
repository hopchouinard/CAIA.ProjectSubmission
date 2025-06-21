-- Update AI Provider Configs Table with Supported Models
-- Based on the models listed in anthropic_provider.py, google_provider.py, and openai_provider.py

-- First, let's update existing records to match the actual supported models

-- Update OpenAI models (keep gpt-4o active, update o3-mini to o4-mini)
UPDATE ai_provider_configs 
SET model = 'o4-mini', 
    config_data = '{"description": "OpenAI o4-mini thinking model", "supports_system_messages": false, "supports_temperature": false, "supports_thinking_mode": true}',
    updated_at = datetime('now')
WHERE provider = 'openai' AND model = 'o3-mini';

-- Insert missing OpenAI models
INSERT INTO ai_provider_configs (provider, model, is_active, priority, created_at, updated_at, config_data)
VALUES 
('openai', 'gpt-4.1', 0, 7, datetime('now'), datetime('now'), 
 '{"description": "OpenAI GPT-4.1 model", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}'),
('openai', 'gpt-4.1-mini', 0, 8, datetime('now'), datetime('now'), 
 '{"description": "OpenAI GPT-4.1 Mini model", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}'),
('openai', 'o3', 0, 9, datetime('now'), datetime('now'), 
 '{"description": "OpenAI o3 thinking model", "supports_system_messages": false, "supports_temperature": false, "supports_thinking_mode": true}');

-- Insert missing Anthropic models
INSERT INTO ai_provider_configs (provider, model, is_active, priority, created_at, updated_at, config_data)
VALUES 
('anthropic', 'claude-3-5-haiku', 0, 10, datetime('now'), datetime('now'), 
 '{"description": "Anthropic Claude 3.5 Haiku", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}'),
('anthropic', 'claude-4-opus', 0, 11, datetime('now'), datetime('now'), 
 '{"description": "Anthropic Claude 4 Opus", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}'),
('anthropic', 'claude-4-sonnet', 0, 12, datetime('now'), datetime('now'), 
 '{"description": "Anthropic Claude 4 Sonnet", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}');

-- Update existing Google model and insert missing Google models
UPDATE ai_provider_configs 
SET model = 'gemini-2.5-flash', 
    config_data = '{"description": "Google Gemini 2.5 Flash", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}',
    updated_at = datetime('now')
WHERE provider = 'google' AND model = 'gemini-2.0-flash-exp';

INSERT INTO ai_provider_configs (provider, model, is_active, priority, created_at, updated_at, config_data)
VALUES 
('google', 'gemini-2.5-pro', 0, 13, datetime('now'), datetime('now'), 
 '{"description": "Google Gemini 2.5 Pro", "supports_system_messages": true, "supports_temperature": true, "supports_thinking_mode": false}');

-- Optional: Remove any models that are no longer supported or outdated
-- DELETE FROM ai_provider_configs WHERE provider = 'openai' AND model = 'gpt-4o' AND id != 1;

-- Verify the updates
SELECT provider, model, is_active, priority, config_data 
FROM ai_provider_configs 
ORDER BY provider, priority;
