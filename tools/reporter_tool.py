"""
Reporter Tool - Generates PDF reports from validation results
"""
import json
import os
from datetime import datetime
from typing import Dict, Any
from crewai.tools import BaseTool
from jinja2 import Environment, FileSystemLoader

# Try to import weasyprint, fall back to HTML-only if not available
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"WARNING: WeasyPrint not available - will generate HTML reports instead of PDF")
    print(f"Reason: {str(e)[:80]}...")


class ReporterTool(BaseTool):
    name: str = "PDF Report Generator"
    description: str = (
        "Generates comprehensive PDF reports from validation results. "
        "Creates professional, formatted reports with summary statistics, "
        "detailed violation listings, and pass/fail status for each panel. "
        "Saves output to results directory."
    )

    def _run(self, panel_data_json: str, violations_json: str,
             output_dir: str = "results", report_name: str = "report.pdf") -> str:
        """
        Generate PDF report from validation results

        Args:
            panel_data_json: JSON string with panel data
            violations_json: JSON string with validation results
            output_dir: Directory to save output files
            report_name: Name of the PDF report file

        Returns:
            JSON string with path to generated report
        """
        try:
            panel_data = json.loads(panel_data_json)
            violations_data = json.loads(violations_json)

            if panel_data.get("status") == "error":
                return json.dumps({
                    "status": "error",
                    "message": "Cannot generate report - panel data contains errors"
                })

            if violations_data.get("status") == "error":
                return json.dumps({
                    "status": "error",
                    "message": "Cannot generate report - violations data contains errors"
                })

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Prepare report data
            report_data = self._prepare_report_data(panel_data, violations_data)

            # Generate HTML from template
            html_content = self._generate_html(report_data)

            # Convert HTML to PDF
            output_path = os.path.join(output_dir, report_name)
            self._generate_pdf(html_content, output_path)

            result = {
                "status": "success",
                "report_path": output_path,
                "report_name": report_name,
                "pass_status": report_data["pass_status"],
                "total_violations": report_data["total_violations"]
            }

            return json.dumps(result, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON input: {str(e)}"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Report generation error: {str(e)}"
            })

    def _prepare_report_data(self, panel_data: Dict[str, Any],
                            violations_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for report template"""

        panels = panel_data.get("panels", [])
        violations_list = violations_data.get("violations", [])
        summary = violations_data.get("summary", {})

        # Create violation lookup by panel_id
        violations_by_panel = {v["panel_id"]: v["violations"] for v in violations_list}

        # Prepare panel data with violations
        panels_with_violations = []
        for panel in panels:
            panel_id = panel["panel_id"]
            panel_violations = violations_by_panel.get(panel_id, [])

            panels_with_violations.append({
                "panel_id": panel_id,
                "name": panel["name"],
                "dimensions": panel["dimensions"],
                "violations": panel_violations,
                "pass": len(panel_violations) == 0
            })

        report_data = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_panels": len(panels),
            "panels_with_violations": violations_data.get("panels_with_violations", 0),
            "total_violations": summary.get("total_violations", 0),
            "pass_status": violations_data.get("pass", False),
            "violations_by_type": summary.get("by_type", {}),
            "violations_by_severity": summary.get("by_severity", {}),
            "panels": panels_with_violations
        }

        return report_data

    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML from Jinja2 template"""
        # Set up Jinja2 environment
        template_dir = os.path.join('config', 'templates')
        jinja_env = Environment(loader=FileSystemLoader(template_dir))

        template = jinja_env.get_template('report_template.html')
        html_content = template.render(**report_data)
        return html_content

    def _generate_pdf(self, html_content: str, output_path: str):
        """Convert HTML to PDF using WeasyPrint, or save as HTML if not available"""
        if not WEASYPRINT_AVAILABLE:
            # WeasyPrint not available, save as HTML
            html_path = output_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML report saved to: {html_path}")
            print("NOTE: For PDF support, install GTK+ libraries (see LLM_SETUP.md)")
            return

        try:
            # Generate PDF
            weasyprint.HTML(string=html_content).write_pdf(output_path)
            print(f"PDF report saved to: {output_path}")
        except Exception as e:
            # If WeasyPrint fails, save as HTML instead
            html_path = output_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"WARNING: PDF generation failed: {str(e)[:100]}...")
            print(f"HTML report saved to: {html_path}")
            print("NOTE: For PDF support, install GTK+ libraries (see LLM_SETUP.md)")
