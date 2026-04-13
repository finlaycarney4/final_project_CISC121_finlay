import gradio as gr
import matplotlib.pyplot as plt
import time

# -----------------------------
# MERGE SORT WITH VISUAL OUTPUT
# -----------------------------

def merge(left, right, key, frames):
    merged = []
    i = j = 0

    # Merge while recording frames for visualization
    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

        # Save current state for visualization
        frames.append(merged + left[i:] + right[j:])

    # Add remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])

    # Save final merged state
    frames.append(merged.copy())

    return merged


def merge_sort(arr, key, frames):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, frames)
    right = merge_sort(arr[mid:], key, frames)

    return merge(left, right, key, frames)


# -----------------------------
# VISUALIZATION FUNCTION
# -----------------------------

def create_plot(data, key):
    # Create a bar chart showing current state of sorting
    values = [item[key] for item in data]
    labels = [item["title"] for item in data]

    plt.figure()
    plt.bar(labels, values)
    plt.xticks(rotation=45, ha="right")
    plt.title(f"Sorting by {key}")
    plt.tight_layout()

    return plt


# -----------------------------
# PLAYLIST SORTING LOGIC
# -----------------------------

def sort_playlist(titles, artists, energies, durations, sort_key):
    playlist = []

    # Build playlist dictionary
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
        return "No songs entered!", None

    # Store frames for animation
    frames = []

    # Perform merge sort
    sorted_list = merge_sort(playlist, sort_key, frames)

    # Final text output
    final_display = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    # Create final visualization (last frame)
    plot = create_plot(sorted_list, sort_key)

    return final_display, plot


# -----------------------------
# GRADIO UI
# -----------------------------

with gr.Blocks() as demo:
    gr.Markdown("# 🎵 Playlist Vibe Builder\nVisualize Merge Sort in action!")

    with gr.Row():
        titles = gr.Textbox(label="Song Titles (comma-separated)")
        artists = gr.Textbox(label="Artists (comma-separated)")

    with gr.Row():
        energies = gr.Textbox(label="Energy Scores 0–100 (comma-separated)")
        durations = gr.Textbox(label="Durations in seconds (comma-separated)")

    sort_key = gr.Radio(
        ["energy", "duration"],
        label="Sort By",
        value="energy"
    )

    sort_button = gr.Button("Sort Playlist")

    # Outputs
    final_output = gr.Textbox(label="Sorted Playlist", lines=10)
    plot_output = gr.Plot(label="Sorting Visualization")

    def parse_csv(text):
        return [x.strip() for x in text.split(",")]

    def run_sort(t, a, e, d, key):
        return sort_playlist(
            parse_csv(t),
            parse_csv(a),
            parse_csv(e),
            parse_csv(d),
            key
        )

    sort_button.click(
        run_sort,
        inputs=[titles, artists, energies, durations, sort_key],
        outputs=[final_output, plot_output]
    )

# Launch app
demo.launch(share=True)
