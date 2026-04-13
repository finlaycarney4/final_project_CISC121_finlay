import gradio as gr
import matplotlib.pyplot as plt


# =========================
# MERGE SORT (ANIMATED)
# =========================

def merge(left, right, key, frames):
    merged = []
    i = j = 0

    # Merge while comparing
    while i < len(left) and j < len(right):

        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": (left[i], right[j]),
            "message": f"Comparing {left[i]['title']} and {right[j]['title']}"
        })

        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": None,
            "message": "Moved item into merged list"
        })

    # Add leftovers
    merged.extend(left[i:])
    merged.extend(right[j:])

    frames.append({
        "data": merged.copy(),
        "highlight": None,
        "message": "Merged section complete"
    })

    return merged


def merge_sort(arr, key, frames):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, frames)
    right = merge_sort(arr[mid:], key, frames)

    return merge(left, right, key, frames)


# =========================
# FRAME VISUALIZATION
# =========================

def plot_frame(frame, key):
    data = frame["data"]
    highlight = frame["highlight"]

    # Handle empty data safely
    if not data:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No data to display", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        plt.close(fig)
        return fig

    values = [item[key] for item in data]
    labels = [item["title"] for item in data]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(labels, values)

    # Highlight compared items
    if highlight:
        for bar, item in zip(bars, data):
            if item is highlight[0] or item is highlight[1]:
                bar.set_color("red")

    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_title(f"Sorting by {key}")
    plt.tight_layout()

    plt.close(fig)
    return fig


# =========================
# SORT + ANIMATION
# =========================

def safe_int(x):
    try:
        return int(x)
    except:
        return 0


def sort_playlist(titles, artists, energies, durations, sort_key):

    # Check list lengths
    if not (len(titles) == len(artists) == len(energies) == len(durations)):
        yield "Error: All lists must have the same number of items.", None
        return

    # Build playlist objects
    playlist = []
    for t, a, e, d in zip(titles, artists, energies, durations):
        playlist.append({
            "title": t,
            "artist": a,
            "energy": safe_int(e),
            "duration": safe_int(d)
        })

    # Handle empty playlist
    if len(playlist) == 0:
        yield "Playlist is empty — nothing to sort.", None
        return

    frames = []
    sorted_list = merge_sort(playlist, sort_key, frames)

    # Stream animation frames
    for frame in frames:
        fig = plot_frame(frame, sort_key)
        yield frame["message"], fig

    # Final sorted output
    final_text = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    final_plot = plot_frame({"data": sorted_list, "highlight": None}, sort_key)

    yield final_text, final_plot


# =========================
# GRADIO UI
# =========================

def parse_csv(text):
    return [x.strip() for x in text.split(",") if x.strip()]


def run_sort(t, a, e, d, key):
    return sort_playlist(
        parse_csv(t),
        parse_csv(a),
        parse_csv(e),
        parse_csv(d),
        key
    )


with gr.Blocks() as demo:
    gr.Markdown("# 🎵 Playlist Vibe Builder\n### Watch Merge Sort Animate Your Playlist!")

    with gr.Row():
        titles = gr.Textbox(label="Song Titles (comma-separated)")
        artists = gr.Textbox(label="Artists (comma-separated)")

    with gr.Row():
        energies = gr.Textbox(label="Energy Scores 0–100 (comma-separated)")
        durations = gr.Textbox(label="Durations in seconds (comma-separated)")

    sort_key = gr.Radio(["energy", "duration"], label="Sort By", value="energy")
    sort_button = gr.Button("Sort Playlist")

    final_output = gr.Textbox(label="Sorted Playlist", lines=10)
    plot_output = gr.Plot(label="Sorting Visualization")

    sort_button.click(
        run_sort,
        inputs=[titles, artists, energies, durations, sort_key],
        outputs=[final_output, plot_output],
    )

demo.launch()
