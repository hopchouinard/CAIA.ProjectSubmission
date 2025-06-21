# OpenAI 401 Authentication Error - Fix Guide

## Problem
Your application logs show:
```
OpenAI API error: Error code: 401 - {'error': {'message': 'OpenAI-Organization header should match organization for API key', 'type': 'invalid_request_error', 'param': None, 'code': 'mismatched_organization'}}
```

## Root Cause
The organization ID in your configuration doesn't match the organization associated with your API key.

## Solution

### Option 1: Remove Organization ID (Recommended)
1. Open your `.env` file
2. Either comment out or remove the `OPENAI_ORG_ID` line:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   # OPENAI_ORG_ID=org-your-organization-id
   ```

### Option 2: Use Correct Organization ID
1. Log into your OpenAI account at https://platform.openai.com/
2. Go to Settings → Organization
3. Copy your Organization ID (starts with "org-")
4. Update your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   OPENAI_ORG_ID=org-your-actual-organization-id
   ```

### Option 3: Use Personal API Key
If you're using a personal OpenAI account (not part of an organization):
1. Use only the API key without organization:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   # Don't include OPENAI_ORG_ID at all
   ```

## Testing the Fix

1. Update your `.env` file with the correct configuration
2. Restart your Flask application
3. Try to evaluate a project
4. Check the logs - you should see successful OpenAI API calls

## Code Changes Made

I've updated the OpenAI provider to:
- Only include the organization header if it's explicitly provided
- Ignore placeholder values like "optional-org-id"
- Handle cases where no organization is needed

The provider will now work correctly whether you:
- Provide a valid organization ID
- Provide no organization ID
- Have an empty or placeholder organization ID

## Next Steps

1. Configure your `.env` file with valid OpenAI credentials
2. Restart the application
3. Test project evaluation
4. The fallback system will still work if OpenAI fails, but now it should succeed with proper credentials!
