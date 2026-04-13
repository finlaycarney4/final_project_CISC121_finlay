import gradio as gr
import matplotlib.pyplot as plt


# ============================================================
# MERGE SORT WITH FRAME CAPTURE
# ------------------------------------------------------------
# Each comparison and merge step produces a "frame" so the
# sorting process can be animated visually.
# ============================================================

def merge(left, right, key, frames):
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        # Capture comparison frame
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": (left[i], right[j]),
            "message": f"Comparing {left[i]['title']} and {right[j]['title']}"
        })

        # Standard merge logic
        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

        # Capture post‑move frame
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": None,
            "message": "Moved item into merged list"
        })

    # Append remaining items
    merged.extend(left[i:])
    merged.extend(right[j:])

    # Final frame for this merge step
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


# ============================================================
# FRAME VISUALIZATION
# ------------------------------------------------------------
# Converts a merge‑sort frame into a bar chart figure.
# Handles empty data safely.
# ============================================================

def plot_frame(frame, key):
    data = frame["data"]

    # Empty playlist → placeholder figure
    if not data:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No songs to sort!", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        plt.close(fig)
        return fig

    values = [item[key] for item in data]
    labels = [item["title"] for item in data]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(labels, values)

    # Highlight compared items
    if frame["highlight"]:
        a, b = frame["highlight"]
        for bar, item in zip(bars, data):
            if item is a or item is b:
                bar.set_color("red")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")

    ax.set_title(f"Sorting by {key}")
    plt.tight_layout()
    plt.close(fig)
    return fig


# ============================================================
# SORT PIPELINE (STREAMING GENERATOR)
# ------------------------------------------------------------
# IMPORTANT:
#   • This generator yields ONLY PLOTS.
#   • The final sorted playlist text is returned at the end.
# ============================================================

def safe_int(x):
    try:
        return int(x)
    except:
        return 0


def sort_playlist(titles, artists, energies, durations, sort_key):

    # Case 1: All lists empty → show "No songs to sort!"
    if len(titles) == len(artists) == len(energies) == len(durations) == 0:
        frame = {"data": [], "highlight": None}
        fig = plot_frame(frame, sort_key)
        yield fig
        return "No songs to sort!"

    # Case 2: Some lists empty → invalid input
    if not (len(titles) == len(artists) == len(energies) == len(durations)):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "Input error", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        plt.close(fig)
        yield fig
        return "Error: All lists must have the same number of items."

    # Build playlist objects
    playlist = []
    for t, a, e, d in zip(titles, artists, energies, durations):
        playlist.append({
            "title": t,
            "artist": a,
            "energy": safe_int(e),
            "duration": safe_int(d)
        })

    frames = []
    sorted_list = merge_sort(playlist, sort_key, frames)

    # Stream animation frames (plots only)
    for frame in frames:
        yield plot_frame(frame, sort_key)

    # Final sorted output text
    final_text = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    # Final plot
    final_plot = plot_frame({"data": sorted_list, "highlight": None}, sort_key)
    yield final_plot

    return final_text


# ============================================================
# GRADIO UI
# ------------------------------------------------------------
# Streaming output = plot
# Final output = text
# ============================================================

def parse_csv(text):
    return [x.strip() for x in text.split(",") if x.strip()]


def run_sort(t, a, e, d, key):
    titles = parse_csv(t)
    artists = parse_csv(a)
    energies = parse_csv(e)
    durations = parse_csv(d)

    gen = sort_playlist(titles, artists, energies, durations, key)

    final_text_holder = {"value": ""}

    # Wrapper generator that streams plots and captures final text
    def plot_stream():
        for result in gen:
            if isinstance(result, str):
                final_text_holder["value"] = result
            else:
                yield result

    return plot_stream(), final_text_holder["value"]


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

    plot_output = gr.Plot(label="Sorting Visualization")
    final_output = gr.Textbox(label="Sorted Playlist", lines=10)

    sort_button.click(
        run_sort,
        inputs=[titles, artists, energies, durations, sort_key],
        outputs=[plot_output, final_output]
    )

demo.launch()
