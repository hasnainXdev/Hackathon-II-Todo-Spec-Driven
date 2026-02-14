from typing import List, Optional
import re


def sanitize_and_validate_tags(tags: Optional[List[str]]) -> List[str]:
    """
    Sanitize and validate tags according to the requirements:
    - Each tag must be 2-20 characters
    - Only alphanumeric characters, hyphens, and underscores allowed
    - Converted to lowercase
    - Duplicates removed
    - Maximum 10 tags
    """
    if not tags:
        return []

    # Limit to 10 tags
    if len(tags) > 10:
        raise ValueError(f"Maximum 10 tags allowed, got {len(tags)} tags")

    sanitized_tags = []
    for tag in tags:
        if not isinstance(tag, str):
            raise ValueError(f"All tags must be strings, got {type(tag)}")

        # Validate length
        if len(tag) < 2 or len(tag) > 20:
            raise ValueError(f"Each tag must be 2-20 characters, got '{tag}' with length {len(tag)}")

        # Sanitize: convert to lowercase and keep only allowed characters
        sanitized_tag = re.sub(r'[^a-z0-9_-]', '', tag.lower())

        # Check if the sanitized tag is empty after cleaning
        if len(sanitized_tag) < 2:
            raise ValueError(f"Tag '{tag}' becomes invalid after sanitization: '{sanitized_tag}'")

        # Add to list if not already present (to avoid duplicates)
        if sanitized_tag not in sanitized_tags:
            sanitized_tags.append(sanitized_tag)

    return sanitized_tags


def validate_priority(priority: Optional[str]) -> Optional[str]:
    """
    Validate priority is one of the allowed values: low, medium, high
    """
    if priority is None:
        return priority
    
    priority_lower = priority.lower()
    if priority_lower not in ['low', 'medium', 'high']:
        raise ValueError(f"Priority must be one of 'low', 'medium', 'high', got '{priority}'")
    
    return priority_lower