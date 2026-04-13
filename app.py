import gradio as gr
import matplotlib.pyplot as plt
import time


# MERGE SORT WITH FRAME CAPTURE


def merge(left, right, key, frames):
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        # Record comparison frame
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": (left[i], right[j])
        })

        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

        # Record after-move frame
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight": None
        })

    merged.extend(left[i:])
    merged.extend(right[j:])

    frames.append({"data": merged.copy(), "highlight": None})
    return merged


def merge_sort(arr, key, frames):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, frames)
    right = merge_sort(arr[mid:], key, frames)

    return merge(left, right, key, frames)



# VISUALIZATION FUNCTION


def plot_frame(frame, key):
    data = frame["data"]
    highlight = frame["highlight"]

    values = [item[key] for item in data]
    labels = [item["title"] for item in data]

    plt.figure(figsize=(8, 4))
    bars = plt.bar(labels, values)

    # Highlight compared bars
    if highlight:
        for bar, item in zip(bars, data):
            if item in highlight:
                bar.set_color("red")

    plt.xticks(rotation=45, ha="right")
    plt.title(f"Sorting by {key}")
    plt.tight_layout()
    return plt



# SORT + ANIMATION LOGIC


def sort_playlist(titles, artists, energies, durations, sort_key):
    playlist = []

    for t, a, e, d in zip(titles, artists, energies, durations):
        if t.strip() == "":
            continue
        playlist.append({
            "title": t,
            "artist": a,
            "energy": int(e),
            "duration": int(d)
        })

    if len(playlist) == 0:
        yield "No songs entered!", None

    frames = []
    sorted_list = merge_sort(playlist, sort_key, frames)

    # Animate frames
    for frame in frames:
        plt_frame = plot_frame(frame, sort_key)
        yield "Sorting...", plt_frame

    # Final sorted playlist text
    final_text = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    final_plot = plot_frame({"data": sorted_list, "highlight": None}, sort_key)
    yield final_text, final_plot



# GRADIO UI


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

    def parse_csv(text):
        return [x.strip() for x in text.split(",")]

    sort_button.click(
        sort_playlist,
        inputs=[titles, artists, energies, durations, sort_key],
        outputs=[final_output, plot_output]
    )

demo.launch()
