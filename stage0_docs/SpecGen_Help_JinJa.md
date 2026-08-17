# Using Variables in Documents with Jinja2 Templates

## Purpose

Jinja2 is a templating system that allows you to add variables, repeated sections, and conditional text into documents. It is useful when you want one source document to produce many versions of an output by filling in values automatically.

For an electrical engineer, this is useful for things like:

* Test reports
* Design summaries
* Requirements documents
* BOM summaries
* Manufacturing notes
* Configuration files
* Calibration reports
* HTML reports
* CSV exports

Instead of manually editing the same document over and over, you can define placeholders once and let software replace them with project-specific data.

---

## Basic Concept

A Jinja2 template is a normal document that contains special placeholders.

Example:

```jinja2
Project Name: {{ project_name }}
Board Revision: {{ board_revision }}
Nominal Voltage: {{ nominal_voltage }} V
Maximum Current: {{ max_current }} A
```

When the template is processed with data, the variables are replaced.

Example data:

```yaml
project_name: Battery Monitor Board
board_revision: Rev B
nominal_voltage: 48
max_current: 12
```

Rendered output:

```text
Project Name: Battery Monitor Board
Board Revision: Rev B
Nominal Voltage: 48 V
Maximum Current: 12 A
```

---

## Variable Syntax

Variables are written using double curly braces:

```jinja2
{{ variable_name }}
```

Common examples:

```jinja2
{{ project_name }}
{{ document_number }}
{{ revision }}
{{ engineer_name }}
{{ voltage_limit }}
{{ current_limit }}
{{ temperature_range }}
```

Variable names should usually be:

* Lowercase
* Descriptive
* Written with underscores instead of spaces
* Consistent across all templates

Good:

```jinja2
{{ max_cell_voltage }}
```

Avoid:

```jinja2
{{ Max Cell Voltage }}
{{ V }}
{{ thing1 }}
```

---

## Repeating Sections

Jinja2 can repeat content using loops. This is useful for tables, BOM items, test points, connector pins, or measurement results.

Example:

```jinja2
| Signal | Pin | Description |
|---|---:|---|
{% for pin in connector_pins %}
| {{ pin.signal }} | {{ pin.number }} | {{ pin.description }} |
{% endfor %}
```

Example data:

```yaml
connector_pins:
  - signal: VIN
    number: 1
    description: Input voltage
  - signal: GND
    number: 2
    description: Ground reference
  - signal: TEMP_SENSE
    number: 3
    description: Temperature sensor input
```

Rendered output:

```markdown
| Signal | Pin | Description |
|---|---:|---|
| VIN | 1 | Input voltage |
| GND | 2 | Ground reference |
| TEMP_SENSE | 3 | Temperature sensor input |
```

---

## Conditional Text

Jinja2 can include or exclude content based on a value.

Example:

```jinja2
{% if include_safety_warning %}
## Safety Warning

This circuit may contain hazardous voltages. Follow appropriate lab safety procedures.
{% endif %}
```

If `include_safety_warning` is true, the warning appears. If it is false, the warning is omitted.

This is useful for optional sections such as:

* Safety warnings
* Regulatory notes
* Manufacturing instructions
* Debug-only content
* Customer-specific sections
* Prototype versus production notes

---

## File Types Where This Is Appropriate

Jinja2-style templating is appropriate for many document and data formats.

### Text Files

Plain text files are one of the simplest places to use Jinja2.

Examples:

```text
Part Number: {{ part_number }}
Revision: {{ revision }}
Engineer: {{ engineer_name }}
```

Useful for:

* Notes
* Configuration files
* Logs
* Readme files
* Simple reports

---

### Markdown Files

Markdown works very well with Jinja2 because Markdown is plain text.

Example:

```jinja2
# {{ project_name }} Test Report

## Test Conditions

- Input Voltage: {{ input_voltage }} V
- Load Current: {{ load_current }} A
- Ambient Temperature: {{ ambient_temperature }} °C
```

Useful for:

* Engineering reports
* Design documentation
* Git-tracked documentation
* Automated project summaries
* Test result reports

---

### Word Documents

Jinja2-style variables can also be used in Word documents, usually through a DOCX-aware templating tool.

Example placeholder inside a Word document:

```jinja2
{{ project_name }}
```

Useful for:

* Formal reports
* Customer-facing documents
* Controlled document templates
* Engineering release packages

Important note: a `.docx` file is not a simple plain text file. It is a structured document format. To use Jinja2 variables in Word documents, use a tool that understands Word/DOCX templates rather than treating the `.docx` file as raw text.

---

### HTML Files

HTML is another strong fit for Jinja2.

Example:

```jinja2
<h1>{{ project_name }} Test Summary</h1>

<table>
  <tr>
    <th>Test</th>
    <th>Result</th>
    <th>Status</th>
  </tr>
  {% for test in test_results %}
  <tr>
    <td>{{ test.name }}</td>
    <td>{{ test.result }}</td>
    <td>{{ test.status }}</td>
  </tr>
  {% endfor %}
</table>
```

Useful for:

* Web-based reports
* Internal dashboards
* Automated test summaries
* Design review pages

---

### CSV Files

CSV files can also be generated using Jinja2 templates.

Example:

```jinja2
Reference,Part Number,Description,Quantity
{% for item in bom_items %}
{{ item.reference }},{{ item.part_number }},{{ item.description }},{{ item.quantity }}
{% endfor %}
```

Useful for:

* BOM exports
* Test data summaries
* Manufacturing data
* Import files for other tools

Important note: CSV values that contain commas, quotes, or line breaks may need special handling or quoting. For simple CSV output, Jinja2 works well. For complex CSV files, it is often better to use a CSV-aware software library.

---

## Common Engineering Use Cases

Jinja2 variables are especially useful when generating repeated engineering documents from structured data.

Examples include:

| Use Case              | Example Variables                                              |
| --------------------- | -------------------------------------------------------------- |
| Test report           | `{{ test_name }}`, `{{ result }}`, `{{ pass_fail }}`           |
| Board summary         | `{{ board_name }}`, `{{ revision }}`, `{{ pcb_part_number }}`  |
| BOM report            | `{{ reference }}`, `{{ manufacturer }}`, `{{ quantity }}`      |
| Connector table       | `{{ pin_number }}`, `{{ signal_name }}`, `{{ voltage_level }}` |
| Requirements document | `{{ requirement_id }}`, `{{ requirement_text }}`               |
| Manufacturing notes   | `{{ assembly_revision }}`, `{{ torque_spec }}`                 |
| HTML report           | `{{ chart_title }}`, `{{ measurement_table }}`                 |
| CSV export            | `{{ column_value }}`, `{{ measurement_value }}`                |

---

## Recommended Pattern

A good workflow is:

1. Create a template document.
2. Add variables using `{{ variable_name }}`.
3. Store project data in a structured file such as YAML, JSON, or a spreadsheet.
4. Run a script or tool that combines the template with the data.
5. Generate the final output document.

Example structure:

```text
template.md
project_data.yaml
generate_report.py
output_report.md
```

---

## Simple Example

Template:

```jinja2
# {{ project_name }} Electrical Summary

## Board Information

- Board Name: {{ board_name }}
- Revision: {{ revision }}
- Engineer: {{ engineer_name }}

## Electrical Limits

- Minimum Input Voltage: {{ min_input_voltage }} V
- Maximum Input Voltage: {{ max_input_voltage }} V
- Maximum Current: {{ max_current }} A

## Notes

{{ design_notes }}
```

Data:

```yaml
project_name: DC Daughter Card
board_name: DCDC Interface Board
revision: Rev A
engineer_name: J. Smith
min_input_voltage: 36
max_input_voltage: 60
max_current: 15
design_notes: This board provides protected input power routing and measurement access.
```

Rendered output:

```markdown
# DC Daughter Card Electrical Summary

## Board Information

- Board Name: DCDC Interface Board
- Revision: Rev A
- Engineer: J. Smith

## Electrical Limits

- Minimum Input Voltage: 36 V
- Maximum Input Voltage: 60 V
- Maximum Current: 15 A

## Notes

This board provides protected input power routing and measurement access.
```

---

## Summary

Jinja2 lets engineers create reusable document templates with variables, loops, and conditional sections. It is appropriate for text files, Markdown files, Word documents, HTML files, and CSV files when used with the right supporting tools.

The main idea is simple:

```jinja2
Write the document once.
Use {{ variables }} where values should change.
Generate the final document automatically.
```

This reduces manual editing, improves consistency, and makes engineering documentation easier to maintain across projects, revisions, and customers.

