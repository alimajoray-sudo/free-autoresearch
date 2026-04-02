# Skill Trigger Accuracy Optimization

## Goal
Improve skill description texts so that user queries trigger the correct skill more often.
Each skill has a description in YAML frontmatter. Better descriptions = better routing.

## Metric  
Keyword match accuracy: for each test query, the correct skill's description should contain
keywords that would be matched by a similarity search.

## Constraints
- Keep each skill description under 200 chars
- Must accurately represent what the skill does
- Include common trigger phrases users would use
- Don't add false triggers that would cause wrong routing
- Preserve the skill name exactly
