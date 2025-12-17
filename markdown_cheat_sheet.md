---
title: "Markdown Cheat Sheet"
---

Here’s the updated **Markdown Helper Reference Cheat Sheet** with a new section on links to external web pages, internal wiki pages, and images:

---

# 📑 Markdown Cheat Sheet

## Headings
{% raw %}
```markdown
# H1
## H2
### H3
#### H4
```
{% endraw %}

---

## Text Formatting
{% raw %}
```markdown
**Bold**
*Italic*
~~Strikethrough~~
`Inline code`
```
{% endraw %}

---

## Lists
**Unordered:**
{% raw %}
```markdown
- Item
  - Subitem
```
{% endraw %}

**Ordered:**
{% raw %}
```markdown
1. First
2. Second
```
{% endraw %}

---

## Links & Images

### External Web Pages
{% raw %}
```markdown
[Link Text](https://example.com)
```
{% endraw %}
➡️ Opens a link to an external website.

### Internal Wiki Pages
{% raw %}
```markdown
[Wiki Page](../docs/Getting-Started.md)
```
{% endraw %}
➡️ Links to another page in your documentation/wiki.

### Images
{% raw %}
```markdown
![Alt Text](https://example.com/image.png)
```
{% endraw %}
➡️ Displays an image with alternative text.

---

## Blockquotes
{% raw %}
```markdown
> Quoted text
```
{% endraw %}

---

## Code Blocks
{% raw %}
```markdown
```language
Your code here
```
{% endraw %}
{% raw %}
```

---

## Tables
```
{% endraw %}markdown
| Col1 | Col2 |
|------|------|
| A    | B    |
{% raw %}
```

---

## Callouts
```
{% endraw %}markdown
> [!NOTE]
> Useful information that users should know, even when skimming content.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.
```

