import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta


def generate_calorie_graph(entries, selected_date):
    """
    Given a list of calorie entries and a selected date string (YYYY-MM-DD),
    returns a base64-encoded PNG bar chart of the last 7 days.
    """
    end_date = datetime.strptime(selected_date, '%Y-%m-%d')
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    labels = [(end_date - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]

    calories_by_date = {d: 0 for d in dates}
    for entry in entries:
        raw = str(entry['date'])
        try:
            date_str = datetime.strptime(raw, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
        except ValueError:
            date_str = raw[:10]
        if date_str in calories_by_date:
            calories_by_date[date_str] += entry['calories']

    calorie_values = [calories_by_date[d] for d in dates]
    max_val = max(calorie_values + [100])

    fig, ax = plt.subplots(figsize=(9, 3.5))
    bars = ax.bar(labels, calorie_values, color='#4a90d9', width=0.6, zorder=3, linewidth=0)

    # Value labels on top of each bar
    for bar, val in zip(bars, calorie_values):
        if val > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_val * 0.02,
                str(val),
                ha='center', va='bottom', fontsize=9, color='#444444'
            )

    ax.set_ylim(0, max_val * 1.2)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_alpha(0.2)
    ax.tick_params(axis='y', left=False, labelsize=9, labelcolor='#888888')
    ax.tick_params(axis='x', labelsize=10, labelcolor='#444444')
    ax.set_ylabel('')

    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return img_base64
