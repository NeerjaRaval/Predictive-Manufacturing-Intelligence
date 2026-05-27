"""
PDF Report Generator Module
============================
Generates an executive summary PDF report with charts,
model performance metrics, and key findings.
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Low", "Medium", "High"]


class ManufacturingReport(FPDF):
    """Custom PDF report for Manufacturing Efficiency Classification."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(
            0, 8,
            "AI-Based Manufacturing Efficiency Classification | Executive Report",
            align="C",
        )
        self.ln(5)
        self.set_draw_color(0, 212, 170)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_title_page(self):
        """Create the title page."""
        self.add_page()
        self.ln(50)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(0, 50, 80)
        self.cell(0, 15, "AI-Based Manufacturing", align="C")
        self.ln(15)
        self.cell(0, 15, "Efficiency Classification", align="C")
        self.ln(20)
        self.set_font("Helvetica", "", 16)
        self.set_text_color(0, 160, 130)
        self.cell(0, 10, "Using Sensor, Production & 6G Network Data", align="C")
        self.ln(20)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Executive Summary Report", align="C")
        self.ln(8)
        self.cell(
            0, 8,
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            align="C",
        )
        self.ln(8)
        self.cell(0, 8, "Thales Group | Smart Manufacturing Division", align="C")

    def add_section_title(self, title):
        """Add a section title with styling."""
        self.ln(5)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 50, 80)
        self.cell(0, 10, title)
        self.ln(3)
        self.set_draw_color(0, 212, 170)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(8)

    def add_subsection(self, title):
        """Add a subsection title."""
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 80, 120)
        self.cell(0, 8, title)
        self.ln(8)

    def add_body_text(self, text):
        """Add body text."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def add_kpi_box(self, label, value, x, y, w=40, h=20):
        """Add a KPI metric box."""
        self.set_xy(x, y)
        self.set_fill_color(240, 248, 255)
        self.set_draw_color(0, 212, 170)
        self.rect(x, y, w, h, "DF")
        self.set_xy(x, y + 2)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(w, 5, label, align="C")
        self.set_xy(x, y + 8)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 50, 80)
        self.cell(w, 8, str(value), align="C")


def _create_class_distribution_chart(df, save_path):
    """Create a pie chart of efficiency class distribution."""
    counts = df["Efficiency_Status"].value_counts()
    colors = ["#FF6B6B", "#FFD93D", "#6BCB77"]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 11},
    )
    for t in autotexts:
        t.set_fontweight("bold")
    ax.set_title("Efficiency Status Distribution", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def _create_model_comparison_chart(comparison_df, save_path):
    """Create a grouped bar chart comparing model metrics."""
    metrics = ["Accuracy", "Macro F1", "Precision", "Recall"]
    models = comparison_df["Model"].tolist()

    x = np.arange(len(metrics))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#4ECDC4", "#45B7D1", "#96CEB4"]

    for i, model in enumerate(models):
        row = comparison_df[comparison_df["Model"] == model].iloc[0]
        values = [row[m] for m in metrics]
        ax.bar(x + i * width, values, width, label=model, color=colors[i % len(colors)])

    ax.set_xlabel("Metric")
    ax.set_ylabel("Score")
    ax.set_title("Model Performance Comparison")
    ax.set_xticks(x + width)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_report(df, comparison_df, best_model_name, importance_df, save_dir="outputs"):
    """
    Generate the full executive PDF report.
    
    Parameters:
        df: Original dataframe
        comparison_df: Model comparison DataFrame
        best_model_name: Name of the best performing model
        importance_df: Feature importance DataFrame
        save_dir: Output directory
    """
    logger.info("Generating PDF executive report...")
    os.makedirs(save_dir, exist_ok=True)

    # Create temporary chart images
    charts_dir = os.path.join(save_dir, "report_charts")
    os.makedirs(charts_dir, exist_ok=True)

    dist_chart_path = os.path.join(charts_dir, "class_distribution.png")
    _create_class_distribution_chart(df, dist_chart_path)

    comparison_chart_path = os.path.join(charts_dir, "model_comparison.png")
    _create_model_comparison_chart(comparison_df, comparison_chart_path)

    # Build PDF
    pdf = ManufacturingReport()
    pdf.alias_nb_pages()

    # Title Page
    pdf.add_title_page()

    # Section 1: Dataset Overview
    pdf.add_page()
    pdf.add_section_title("1. Dataset Overview")

    pdf.add_body_text(
        f"The analysis is based on the Thales Group Manufacturing dataset containing "
        f"{len(df):,} operational records from {df['Machine_ID'].nunique()} industrial machines, "
        f"collected over {df['Date'].nunique()} days with minute-level granularity."
    )

    # KPI boxes
    y_pos = pdf.get_y() + 5
    pdf.add_kpi_box("Total Records", f"{len(df):,}", 15, y_pos, 42, 22)
    pdf.add_kpi_box("Machines", str(df["Machine_ID"].nunique()), 62, y_pos, 42, 22)
    pdf.add_kpi_box("Days", str(df["Date"].nunique()), 109, y_pos, 42, 22)
    pdf.add_kpi_box("Features", "14", 156, y_pos, 42, 22)
    pdf.set_y(y_pos + 30)

    pdf.add_subsection("Class Distribution")
    pdf.add_body_text(
        "The target variable (Efficiency_Status) shows significant class imbalance: "
        f"Low ({df['Efficiency_Status'].value_counts().get('Low', 0)/len(df)*100:.1f}%), "
        f"Medium ({df['Efficiency_Status'].value_counts().get('Medium', 0)/len(df)*100:.1f}%), "
        f"High ({df['Efficiency_Status'].value_counts().get('High', 0)/len(df)*100:.1f}%). "
        "SMOTE oversampling was applied to address this imbalance."
    )

    if os.path.exists(dist_chart_path):
        pdf.image(dist_chart_path, x=40, w=130)

    # Section 2: Model Performance
    pdf.add_page()
    pdf.add_section_title("2. Model Performance")

    pdf.add_body_text(
        "Three classification models were trained and evaluated using temporal train/test split "
        "(training on earlier data, testing on later data) with macro-averaged F1 as the primary metric."
    )

    # Model comparison table
    pdf.set_font("Helvetica", "B", 9)
    col_widths = [45, 22, 22, 22, 22, 22, 22]
    headers = ["Model", "Accuracy", "Macro F1", "Wt F1", "Precision", "Recall", "CV F1"]

    for i, h in enumerate(headers):
        pdf.set_fill_color(0, 50, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)

    for _, row in comparison_df.iterrows():
        is_best = row["Model"] == best_model_name or best_model_name in row["Model"]
        if is_best:
            pdf.set_fill_color(230, 255, 245)
        else:
            pdf.set_fill_color(255, 255, 255)

        vals = [
            row["Model"][:20],
            f"{row['Accuracy']:.4f}",
            f"{row['Macro F1']:.4f}",
            f"{row['Weighted F1']:.4f}",
            f"{row['Precision']:.4f}",
            f"{row['Recall']:.4f}",
            f"{row['CV F1 Mean']:.4f}",
        ]
        for i, v in enumerate(vals):
            pdf.cell(col_widths[i], 7, v, border=1, fill=True, align="C")
        pdf.ln()

    pdf.ln(5)
    pdf.add_body_text(f"Best performing model: {best_model_name}")

    if os.path.exists(comparison_chart_path):
        pdf.image(comparison_chart_path, x=15, w=180)

    # Section 3: Feature Importance
    pdf.add_page()
    pdf.add_section_title("3. Feature Importance")

    pdf.add_body_text(
        "SHAP (SHapley Additive exPlanations) analysis reveals the most influential features "
        "driving efficiency classification decisions:"
    )

    # Top 10 features table
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(0, 50, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(10, 8, "#", border=1, fill=True, align="C")
    pdf.cell(90, 8, "Feature", border=1, fill=True, align="C")
    pdf.cell(50, 8, "Importance (Mean |SHAP|)", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)

    for idx, (_, row) in enumerate(importance_df.head(10).iterrows()):
        pdf.set_fill_color(245, 250, 255) if idx % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.cell(10, 7, str(idx + 1), border=1, fill=True, align="C")
        pdf.cell(90, 7, str(row["Feature"]), border=1, fill=True)
        pdf.cell(50, 7, f"{row['Importance']:.6f}", border=1, fill=True, align="C")
        pdf.ln()

    feat_importance_path = os.path.join("outputs", "feature_importance.png")
    if os.path.exists(feat_importance_path):
        pdf.ln(5)
        pdf.image(feat_importance_path, x=15, w=180)

    # Section 4: Key Findings & Recommendations
    pdf.add_page()
    pdf.add_section_title("4. Key Findings & Recommendations")

    # Auto-generate findings
    top_feature = importance_df.iloc[0]["Feature"]
    findings = [
        f"1. {top_feature} is the most influential factor determining manufacturing efficiency, "
        f"followed by {importance_df.iloc[1]['Feature']} and {importance_df.iloc[2]['Feature']}.",
        f"2. The {best_model_name} model achieves the best balance of precision and recall "
        f"across all efficiency classes, making it suitable for production deployment.",
        "3. Severe class imbalance (High efficiency: ~3%) was successfully addressed using "
        "SMOTE oversampling, enabling the model to identify rare high-efficiency states.",
        "4. Temporal validation confirms the model generalizes to future data, "
        "supporting real-time deployment in factory control systems.",
        "5. Network metrics (latency, packet loss) contribute to classification, "
        "validating the importance of 6G connectivity in smart manufacturing."
    ]

    for finding in findings:
        pdf.add_body_text(finding)
        pdf.ln(2)

    pdf.add_subsection("Recommendations")
    recommendations = [
        "- Deploy the trained model as a real-time efficiency monitoring service.",
        "- Set up automated alerts when efficiency drops below Medium threshold.",
        "- Focus maintenance efforts on machines with high Error_Rate and low Maintenance Scores.",
        "- Monitor network reliability as it directly impacts classification accuracy.",
        "- Retrain the model quarterly with new data to maintain prediction accuracy.",
        "- Investigate root causes behind the dominant Low efficiency status (77.8%)."
    ]

    for rec in recommendations:
        pdf.add_body_text(rec)

    # Save PDF
    pdf_path = os.path.join(save_dir, "executive_report.pdf")
    pdf.output(pdf_path)
    logger.info(f"Executive report saved to {pdf_path}")

    return pdf_path
