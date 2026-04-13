import gradio as gr
import matplotlib.pyplot as plt


# MERGE SORT


def merge(left, right, key, frames):
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):

        # Capture comparison state for animation
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

        # Capture state after moving an item
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": None,
            "message": "Moved item into merged list"
        })

    # Add leftovers (no comparisons)
    merged.extend(left[i:])
    merged.extend(right[j:])

    # Final snapshot of this merge step
    frames.append({
        "data": merged.copy(),
        "highlight": None,
        "message": "Merged section complete"
    })

    return merged


def merge_sort(arr, key, frames):
    # Base case for recursion
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2

    # Recursively collect frames from both halves
    left = merge_sort(arr[:mid], key, frames)
    right = merge_sort(arr[mid:], key, frames)

    return merge(left, right, key, frames)


# FRAME VISUALIZATION


def plot_frame(frame, key):
    # Convert frame data into bar chart
    data = frame["data"]
    highlight = frame["highlight"]

    values = [item[key] for item in data]
    labels = [item["title"] for item in data]

    fig, ax = plt.subplots(figsize=(8, 4))  # FIX: use fig instead of plt
    bars = ax.bar(labels, values)

    # Highlight only the items being compared
    if highlight:
        for bar, item in zip(bars, data):
            # FIX: safer comparison using object identity
            if item is highlight[0] or item is highlight[1]:
                bar.set_color("red")

    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_title(f"Sorting by {key}")
    plt.tight_layout()

    plt.close(fig)  # FIX: prevent memory leaks in animation
    return fig      # FIX: return figure, not plt


# SORT + ANIMATION


def safe_int(x):  # FIX: prevent crashes on bad input
    try:
        return int(x)
    except:
        return 0


def sort_playlist(titles, artists, energies, durations, sort_key):
    # Hugging Face crashes if lists are mismatched — check early
    if not (len(titles) == len(artists) == len(energies) == len(durations)):
        yield "Error: All lists must have the same number of items.", None
        return

    # Build structured playlist objects
    playlist = []
    for t, a, e, d in zip(titles, artists, energies, durations):
        playlist.append({
            "title": t,
            "artist": a,
            "energy": safe_int(e),     # FIX: safer parsing
            "duration": safe_int(d)    # FIX: safer parsing
        })

    frames = []
    sorted_list = merge_sort(playlist, sort_key, frames)

    # Yield each animation frame
    for frame in frames:
        plt_frame = plot_frame(frame, sort_key)
        yield frame["message"], plt_frame
        # FIX: removed time.sleep() (breaks Gradio streaming)

    # Build final sorted playlist text
    final_text = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    final_plot = plot_frame({"data": sorted_list, "highlight": None}, sort_key)

    # Final UI update
    yield final_text, final_plot


# GRADIO UI


def parse_csv(text):
    # Ensures clean list even with extra spaces
    return [x.strip() for x in text.split(",") if x.strip()]


def run_sort(t, a, e, d, key):
    # Generator returned directly to Gradio for streaming
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
