"""
Chart utilities and Plotly theme styling for Employee Attrition Analysis.
Ensures cohesive warm cocoa, charcoal, copper, and warm ivory aesthetics.
"""
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from config.settings import THEME_COLORS


def apply_theme_layout(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """Apply unified enterprise theme styling to any Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=15, color=THEME_COLORS["text_primary"], family="Plus Jakarta Sans, sans-serif"),
            x=0.02,
            y=0.96
        ),
        paper_bgcolor=THEME_COLORS["card_bg"],
        plot_bgcolor="#1d1916",
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color=THEME_COLORS["text_secondary"],
            size=11
        ),
        margin=dict(l=40, r=30, t=50, b=40),
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=THEME_COLORS["text_secondary"])
        ),
        hoverlabel=dict(
            bgcolor="#2d2621",
            font_size=11,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color=THEME_COLORS["text_primary"]
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=THEME_COLORS["border"],
        tickfont=dict(color=THEME_COLORS["text_secondary"], size=10),
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=THEME_COLORS["border"],
        tickfont=dict(color=THEME_COLORS["text_secondary"], size=10),
        zeroline=False
    )
    return fig


def create_donut_chart(labels: List[str], values: List[float], title: str, colors: Optional[List[str]] = None) -> go.Figure:
    """Create a styled donut chart for distributions."""
    palette = colors or [THEME_COLORS["border"], THEME_COLORS["accent"]]
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=palette, line=dict(color=THEME_COLORS["card_bg"], width=2)),
        textinfo="percent+label",
        textfont=dict(color=THEME_COLORS["text_primary"], size=11)
    )])
    return apply_theme_layout(fig, title=title, height=320)


def create_horizontal_bar(y: List[str], x: List[float], title: str, x_label: str = "% Attrition", color: str = THEME_COLORS["accent"]) -> go.Figure:
    """Create a clean horizontal bar chart."""
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation="h",
        marker=dict(color=color, line=dict(color="#e08369", width=1)),
        text=[f"{v:.1f}%" for v in x],
        textposition="outside",
        textfont=dict(color=THEME_COLORS["text_primary"], size=10)
    ))
    fig.update_layout(xaxis_title=x_label)
    return apply_theme_layout(fig, title=title, height=max(320, len(y) * 28))
