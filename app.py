
import gradio as gr

# -----------------------------
# MERGE SORT WITH VISUAL STEPS
# -----------------------------

def merge(left, right, key, steps):
    # Merge two sorted lists (left and right) based on the chosen key.
    # 'steps' collects snapshots of comparisons and merges for visualization.
    merged = []
    i = j = 0

    # Record the moment when two sublists are about to be compared.
    steps.append({
        "action": "compare",
        "left": left.copy(),   # Copy so later modifications don't affect stored step
        "right": right.copy()
    })

    # Standard merge loop: repeatedly compare the smallest remaining elements.
    while i < len(left) and j < len(right):
        # Compare values using the selected sorting key (energy or duration).
        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append any leftover elements from either list.
    # Only one of these will actually add items.
    merged.extend(left[i:])
    merged.extend(right[j:])

    # Record the result of this merge step for visualization.
    steps.append({
        "action": "merge",
        "result": merged.copy()
    })

    return merged


def merge_sort(arr, key, steps):
    # Base case: a list of length 0 or 1 is already sorted.
    if len(arr) <= 1:
        return arr

    # Split the list into two halves.
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, steps)   # Recursively sort left half
    right = merge_sort(arr[mid:], key, steps)  # Recursively sort right half

    # Merge the two sorted halves.
    return merge(left, right, key, steps)


# -----------------------------
# PLAYLIST SORTING LOGIC
# -----------------------------

def sort_playlist(titles, artists, energies, durations, sort_key):
    # Convert raw text inputs into a structured list of song dictionaries.
    playlist = []
    for t, a, e, d in zip(titles, artists, energies, durations):
        if t.strip() == "":
            continue  # Skip empty title entries (user may leave trailing commas)
        playlist.append({
            "title": t,
            "artist": a,
            "energy": int(e),      # Convert numeric fields to integers
            "duration": int(d)
        })

    # Handle case where user enters no valid songs.
    if len(playlist) == 0:
        return "No songs entered!", ""

    # List to store all comparison + merge steps for animation.
    steps = []

    # Perform merge sort using the selected key.
    sorted_list = merge_sort(playlist, sort_key, steps)

    # Format the final sorted playlist into readable text.
    final_display = "\n".join(
        [f"{s['title']} — {s['artist']} | Energy: {s['energy']} | Duration: {s['duration']}s"
         for s in sorted_list]
    )

    # Build a readable step-by-step log of the merge sort process.
    step_text = ""
    for i, step in enumerate(steps):
        if step["action"] == "compare":
            step_text += f"\n--- Step {i+1}: Comparing ---\n"
            step_text += f"Left: {step['left']}\nRight: {step['right']}\n"
        else:
            step_text += f"\n--- Step {i+1}: Merged ---\n"
            step_text += f"{step['result']}\n"

    return final_display, step_text


# -----------------------------
# GRADIO UI
# -----------------------------

with gr.Blocks() as demo:
    # Title + description for the app interface.
    gr.Markdown("# 🎵 Playlist Vibe Builder\nSort your playlist using **Merge Sort** and watch the algorithm work step-by-step!")

    # Input fields for song titles and artists.
    with gr.Row():
        titles = gr.Textbox(label="Song Titles (comma-separated)")
        artists = gr.Textbox(label="Artists (comma-separated)")

    # Input fields for numeric song attributes.
    with gr.Row():
        energies = gr.Textbox(label="Energy Scores 0–100 (comma-separated)")
        durations = gr.Textbox(label="Durations in seconds (comma-separated)")

    # User chooses which attribute to sort by.
    sort_key = gr.Radio(
        ["energy", "duration"],
        label="Sort By",
        value="energy"
    )

    # Button to trigger sorting.
    sort_button = gr.Button("Sort Playlist")

    # Output boxes for final sorted playlist and step-by-step merge sort log.
    final_output = gr.Textbox(label="Sorted Playlist", lines=10)
    steps_output = gr.Textbox(label="Merge Sort Steps", lines=20)

    # Helper function: convert comma-separated text into a list.
    def parse_csv(text):
        return [x.strip() for x in text.split(",")]

    # Wrapper function that prepares inputs and calls the sorting logic.
    def run_sort(t, a, e, d, key):
        return sort_playlist(
            parse_csv(t),
            parse_csv(a),
            parse_csv(e),
            parse_csv(d),
            key
        )

    # Connect button click to the sorting function.
    sort_button.click(
        run_sort,
        inputs=[titles, artists, energies, durations, sort_key],
        outputs=[final_output, steps_output]
    )

# Launch the Gradio interface.
demo.launch(share=True)


