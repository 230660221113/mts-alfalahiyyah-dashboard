import plotly.graph_objects as go

DARK, LIGHT, RED = "#2F5D50", "#A5D17A", "#E5534B"
INK, MUTED, GRID = "#1F2A27", "#6B7A75", "#EEF2EF"
FONT = dict(family="Plus Jakarta Sans, sans-serif", color=MUTED, size=12)

def sparkline(vals, color="#fff") -> str:
    lo, hi = min(vals), max(vals)
    pts = " ".join(f"{i * 92 / (len(vals) - 1):.1f},{32 - (v - lo) / ((hi - lo) or 1) * 28:.1f}" for i, v in enumerate(vals))
    return f"<svg viewBox='0 0 92 34'><polyline points='{pts}' fill='none' stroke='{color}' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/></svg>"

def kpi(cls, title, value, sub, spark):
    return f"<div class='kpi {cls}'><div class='t'>{title}</div><div class='v'>{value}</div><div class='d'>{sub}</div>{spark}</div>"

def trend_chart(years, values, f_years=None, f_values=None, height=330):
    fig = go.Figure()
    fig.add_scatter(x=years, y=values, name="Aktual", mode="lines+markers", fill="tozeroy", fillcolor="rgba(47,93,80,.07)",
                    line=dict(color=DARK, width=3, shape="spline"), marker=dict(size=8, color="#fff", line=dict(color=DARK, width=2.5)),
                    hovertemplate="%{y:,.0f} siswa<extra>Aktual</extra>")
    allv = list(values)
    if f_years is not None:
        allv += list(f_values)
        fig.add_scatter(x=[years[-1], *f_years], y=[values[-1], *f_values], name="Prediksi", mode="lines+markers",
                        line=dict(color="#7FB84E", width=3, dash="dash", shape="spline"), marker=dict(size=9, symbol="diamond", color=LIGHT, line=dict(color="#7FB84E", width=2)),
                        hovertemplate="%{y:,.0f} siswa<extra>Prediksi</extra>")
    lo, hi = min(allv), max(allv)
    fig.update_layout(height=height, margin=dict(l=0, r=8, t=8, b=0), font=FONT, template="plotly_white", paper_bgcolor="#fff", plot_bgcolor="#fff",
                      legend=dict(orientation="h", y=1.12, x=0, font=dict(color=INK)), hovermode="x unified",
                      hoverlabel=dict(bgcolor="#fff", bordercolor="#E6EBE8", font=dict(color=INK)))
    fig.update_xaxes(showgrid=False, linecolor="#E6EBE8", tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED), range=[lo * 0.85, hi * 1.06], tickformat=",.0f")
    return fig

def donut(labels, values, total, height=190):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=.7, marker=dict(colors=[DARK, LIGHT], line=dict(color="#fff", width=2)), textinfo="none", sort=False,
                           hovertemplate="%{label}: %{value} siswa<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), showlegend=False, paper_bgcolor="#fff", font=FONT,
                      annotations=[dict(text=f"<b>{total}</b><br><span style='font-size:11px;color:{MUTED}'>siswa</span>", showarrow=False, font=dict(size=22, color=INK))])
    return fig


def bar_chart(years, values, f_years=None, f_values=None, height=300):
    short = lambda y: f"{y[2:4]}/{y[7:9]}"
    fig = go.Figure()
    fig.add_bar(x=years, y=values, name="Aktual", marker=dict(color=DARK), hovertemplate="%{y:,.0f} siswa<extra>Aktual</extra>")
    cats = list(years)
    if f_years:
        cats += list(f_years)
        fig.add_bar(x=f_years, y=[round(v) for v in f_values], name="Prediksi", marker=dict(color="#DDEFC9", line=dict(color="#6FA83A", width=1.5)),
                    hovertemplate="%{y:,.0f} siswa<extra>Prediksi</extra>")
    fig.update_layout(height=height, bargap=.35, showlegend=False, margin=dict(l=0, r=0, t=8, b=0), font=FONT, template="plotly_white",
                      paper_bgcolor="#fff", plot_bgcolor="#fff", hoverlabel=dict(bgcolor="#fff", bordercolor="#E6EBE8", font=dict(color=INK)))
    fig.update_xaxes(tickmode="array", tickvals=cats, ticktext=[short(c) for c in cats], showgrid=False, linecolor="#DCE6E0", tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, rangemode="tozero", tickfont=dict(color=MUTED), tickformat=",.0f")
    try:
        fig.update_traces(marker_cornerradius=7)
    except Exception:
        pass
    return fig
