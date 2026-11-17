import plotly.graph_objects as go

DARK, LIGHT, INK, RED = "#2F5D50", "#A5D17A", "#2B2F2E", "#E5534B"
FONT = dict(family="Plus Jakarta Sans, sans-serif", color="#5F6D68", size=12)

def sparkline(vals, color="#fff") -> str:
    lo, hi = min(vals), max(vals)
    pts = " ".join(f"{i * 92 / (len(vals) - 1):.1f},{32 - (v - lo) / ((hi - lo) or 1) * 28:.1f}" for i, v in enumerate(vals))
    return f"<svg viewBox='0 0 92 34'><polyline points='{pts}' fill='none' stroke='{color}' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/></svg>"

def kpi(cls, title, value, sub, spark):
    return f"<div class='kpi {cls}'><div class='t'>{title}</div><div class='v'>{value}</div><div class='d'>{sub}</div>{spark}</div>"

def trend_chart(years, values, f_years=None, f_values=None, height=330):
    fig = go.Figure()
    fig.add_scatter(x=years, y=values, name="Aktual", mode="lines+markers", line=dict(color=DARK, width=3, shape="spline"), marker=dict(size=7))
    if f_years is not None:
        fig.add_scatter(x=[years[-1], *f_years], y=[values[-1], *f_values], name="Prediksi", mode="lines+markers",
                        line=dict(color=LIGHT, width=3, dash="dash", shape="spline"), marker=dict(size=8, symbol="diamond"))
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0), font=FONT, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", y=1.1, x=0), hovermode="x unified")
    fig.update_xaxes(showgrid=False, linecolor="#E3E8E4")
    fig.update_yaxes(gridcolor="#EDF1EE", zeroline=False)
    return fig

def donut(labels, values, center, height=200):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=.68, marker=dict(colors=[DARK, LIGHT]), textinfo="none", sort=False))
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font=FONT,
                      annotations=[dict(text=center, showarrow=False, font=dict(size=15, color="#1F2A27"))])
    return fig
