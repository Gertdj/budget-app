# Django Template Formatting Rules

## ⚠️ CRITICAL RULE: Single-Line Template Variables

### The Problem
When Django template variables (like `{{ variable }}`) or template tags span multiple lines within HTML tags, Django **preserves ALL whitespace** including newlines. This causes the rendered output to display across multiple lines, breaking the UI.

### ❌ WRONG - Multi-line Template Code
```html
<!-- This will render with line breaks! -->
<button class="btn">{{ active_date|date:"F Y"
    }}</button>

<a href="?year={{ year }}&month={{ month }}"
    class="btn">Link</a>
```

### ✅ CORRECT - Single-Line Template Code
```html
<!-- This renders correctly on one line -->
<button class="btn">{{ active_date|date:"F Y" }}</button>

<a href="?year={{ year }}&month={{ month }}" class="btn">Link</a>
```

## The Rule

**ALWAYS keep Django template variables and HTML attributes on the SAME LINE.**

- Template variables: `{{ variable }}`, `{{ variable|filter }}`
- Template tags: `{% tag %}`, `{% url 'name' %}`
- HTML attributes with template variables must stay on one line

## Common Violations

1. **Split template variables**
   ```html
   <!-- WRONG -->
   <div>{{ long_variable_name
       }}</div>
   
   <!-- CORRECT -->
   <div>{{ long_variable_name }}</div>
   ```

2. **Split href attributes**
   ```html
   <!-- WRONG -->
   <a href="?param={{ value }}"
       class="link">Text</a>
   
   <!-- CORRECT -->
   <a href="?param={{ value }}" class="link">Text</a>
   ```

3. **Split data attributes**
   ```html
   <!-- WRONG -->
   <div data-id="{{ item.id }}"
        data-name="{{ item.name }}">
   
   <!-- CORRECT -->
   <div data-id="{{ item.id }}" data-name="{{ item.name }}">
   ```

## Why This Happens

Django's template engine processes templates character-by-character. When it encounters:
```html
{{ variable
}}
```

It outputs: `value\n` (with the newline preserved)

## How to Fix Existing Issues

1. **Find split template code:**
   ```bash
   grep -n "{{.*$" templates/**/*.html | grep -v "}}"
   ```

2. **Fix manually:** Consolidate split lines into single lines

3. **Verify:** Check the rendered HTML in browser

## Prevention

- Use a linter or formatter that enforces single-line template variables
- Code review checklist: "Are all template variables on single lines?"
- When in doubt, keep it on one line!

## This Fix Applied To

- `/Users/gert/projects/Budget/finance/templates/finance/dashboard.html`
  - Lines 8-10: Month selector buttons (Previous, Current Month, Next)

## Date Fixed
2025-11-28

---

**Remember: Template variables spanning multiple lines = Multi-line rendering bugs!**
