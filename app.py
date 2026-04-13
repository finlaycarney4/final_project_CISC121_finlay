import gradio as gr
import matplotlib.pyplot as plt



# MERGE SORT WITH FRAME CAPTURE


def merge(left, right, key, frames):
    """
    Merge two sorted sublists into one sorted list, recording a
    frame before and after each comparison so the UI can replay it.

    Args:
        left:   Left sorted sublist (list of song dicts)
        right:  Right sorted sublist (list of song dicts)
        key:    The song field to sort by, e.g. "energy" or "duration"
        frames: Shared list that accumulates animation frames in-place
    """
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_idx  = len(merged)                     # next item from left half
        right_idx = len(merged) + (len(left) - i)   # next item from right half

        # snapshot the list at the moment of comparison, marking
        # the two candidates so the chart can colour them red.
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight_indices": [left_idx, right_idx],
            "message": f"Comparing {left[i]['title']} and {right[j]['title']}"
        })

        # Pick the smaller item and advance that half's pointer.
        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

        # snapshot again after the move so the viewer can see
        # which item was placed and where the list stands now.
        frames.append({
            "data": merged + left[i:] + right[j:],
            "highlight_indices": [],
            "message": "Moved item into merged list"
        })

    # One half is exhausted, append whatever remains from the other.
    merged.extend(left[i:])
    merged.extend(right[j:])

    frames.append({
        "data": merged.copy(),
        "highlight_indices": [],
        "message": "Merged section complete"
    })

    return merged


def merge_sort(arr, key, frames):
    """
    Recursively split the list in half, sort each half, then merge.
    Frames are accumulated into the shared `frames` list throughout
    so the full animation is available once sorting finishes.

    Base case: a list of 0 or 1 items is already sorted — return it.
    """
    if len(arr) <= 1:
        return arr

    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid], key, frames)   # sort left half
    right = merge_sort(arr[mid:], key, frames)   # sort right half
    return merge(left, right, key, frames)       # merge the two sorted halves



# FRAME VISUALIZATION

def plot_frame(frame, key):
    """
    Render one animation frame as a bar chart.

    Args:
        frame: A frame dict with "data" and "highlight_indices"
        key:   The field being sorted ("energy" or "duration"),
               used for bar heights and the chart title

    Returns:
        A matplotlib Figure (closed so it doesn't leak memory)
    """
    data = frame["data"]

    # Empty playlist — show a placeholder message instead of a blank chart.
    if not data:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No songs to sort!", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        plt.close(fig)
        return fig

    # Extract bar heights (numeric field) and labels (song titles).
    values = [item[key] for item in data]
    labels = [item["title"] for item in data]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(labels, values)

    # Colour the two bars currently being compared in red.
    # Uses stored integer indices rather than object identity
    # so this works correctly even if song dicts were copied.
    highlight_indices = frame.get("highlight_indices", [])
    for i, bar in enumerate(bars):
        if i in highlight_indices:
            bar.set_color("red")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_title(f"Sorting by {key}")
    plt.tight_layout()
    plt.close(fig)  # close the figure to free memory



# SORT PIPELINE


def safe_int(x):
    """
    Convert x to int, returning 0 if the conversion fails.
    Only catches expected conversion errors (bad string, wrong type)
    so unexpected exceptions still surface normally.
    """
    try:
        return int(x)
    except (ValueError, TypeError):
        return 0


def sort_playlist(titles, artists, energies, durations, sort_key):
    """
    Generator that drives the full sort-and-animate pipeline.

    Yields matplotlib Figures (animation frames) as the sort runs,
    then yields a final string — either the sorted playlist summary
    or an error message. The caller distinguishes them by type.

    Args:
        titles, artists, energies, durations: parallel lists from the UI
        sort_key: "energy" or "duration"
    """

    # all four fields came in empty — nothing to sort.
    if len(titles) == len(artists) == len(energies) == len(durations) == 0:
        frame = {"data": [], "highlight_indices": []}
        yield plot_frame(frame, sort_key)   # yield an empty chart
        yield "No songs to sort!"           # yield the message string, then stop
        return

    # the four lists have different lengths — user input is inconsistent.
    # Show an error chart and message
    if not (len(titles) == len(artists) == len(energies) == len(durations)):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "Input error", ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        plt.close(fig)
        yield fig
        yield "Error: All lists must have the same number of items."
        return

    # Build a list of song dictionaries from the parallel input lists.
    # safe_int handles non-numeric energy/duration values.
    playlist = []
    for t, a, e, d in zip(titles, artists, energies, durations):
        playlist.append({
            "title":    t,
            "artist":   a,
            "energy":   safe_int(e),
            "duration": safe_int(d)
        })

    # All animation frames are collected into `frames`
    # Sorting happens first, then the frames are streamed
    frames = []
    sorted_list = merge_sort(playlist, sort_key, frames)

    # Yield each captured frame as a bar chart so Gradio can stream
    # the animation one chart update at a time.
    for frame in frames:
        yield plot_frame(frame, sort_key)

    # Build the final readable summary of the sorted playlist.
    final_text = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    # Yield the final sorted-state chart, then the summary string.
    # The string signals that sorting is complete.
    final_plot = plot_frame({"data": sorted_list, "highlight_indices": []}, sort_key)
    yield final_plot
    yield final_text


# GRADIO INTERFACE


def parse_csv(text):
    """Split a comma-separated string into a stripped list, ignoring blanks."""
    return [x.strip() for x in text.split(",") if x.strip()]


def run_sort(t, a, e, d, key):
    """
    Gradio-facing generator. Bridges sort_playlist() — which yields
    mixed Figure/str values — to Gradio's streaming output format,
    which expects a (plot, text) tuple on every yield.

    Figures are forwarded immediately so the animation plays in real time.
    The text string is held until it arrives, then flushed on a final yield
    so the sorted playlist appears once the animation completes.
    """
    titles    = parse_csv(t)
    artists   = parse_csv(a)
    energies  = parse_csv(e)
    durations = parse_csv(d)

    gen = sort_playlist(titles, artists, energies, durations, key)

    final_text   = ""     # accumulates the summary string when it arrives
    current_plot = None   # tracks the most recent figure for the final flush

    for result in gen:
        if isinstance(result, str):
            final_text = result
        else:
            # Received an animation frame — streams to the UI.
            current_plot = result
            yield current_plot, final_text

    # pair the last plot with the now-complete summary text
    # so both outputs update together when the animation finishes.
    if current_plot is not None:
        yield current_plot, final_text


with gr.Blocks() as demo:
    gr.Markdown("# 🎵 Playlist Vibe Builder\n### Watch Merge Sort Animate Your Playlist!")

    with gr.Row():
        titles    = gr.Textbox(label="Song Titles (comma-separated)")
        artists   = gr.Textbox(label="Artists (comma-separated)")

    with gr.Row():
        energies  = gr.Textbox(label="Energy Scores 0–100 (comma-separated)")
        durations = gr.Textbox(label="Durations in seconds (comma-separated)")

    sort_key     = gr.Radio(["energy", "duration"], label="Sort By", value="energy")
    sort_button  = gr.Button("Sort Playlist")

    plot_output  = gr.Plot(label="Sorting Visualization")
    final_output = gr.Textbox(label="Sorted Playlist", lines=10)


    sort_button.click(
        run_sort,
        inputs=[titles, artists, energies, durations, sort_key],
        outputs=[plot_output, final_output]
    )

demo.launch()
