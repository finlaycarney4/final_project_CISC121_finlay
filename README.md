---
title: Playlist Vibe Builder
emoji: 🎵
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.12.0
python_version: '3.10'
app_file: app.py
pinned: false
---

final_project_finlay

I have chosen to create a playlist vibe builder.

I will be implementing a merge sort to make this app possible. Merge sorting is great for this app design because it has the same time complexity in the best and worst situations (nlogn). It also does not require any of the values (energy or duration) to be in order. It only requires the numbers be on a scale from 0 - 100. Lastly, merge sort is a stable sorting type.

DECOMPOSITION
This app requires multiple components in order to function properly. The first component is the input of the songs on the playlist, and their respective energy and duration values. The next component is the implementation of the merge sort that actually sorts the playlist based on the requested category. The output of the code should be an energy or duration sorted playlist. There is also the step of creating the visual aspects of the app, such as buttons and sliders that make the sorting an interactive experience and visually demonstrates the merge sort in action.

PATTERN RECOGNITION
The purpose of the merge sort is to continuously divide the playlist until there is only one song in each subsection. As well, the code will continuously combine the subsections, in order of duration or energy, by comparing values until there is one final sorted list. This code is also reusable and can be repeated with any playlist with energy or duration values between 0 - 100.

ABSTRACTION
Features of the songs that do not involve the duration or energy values, such as genre, are irrelevant. The only relevant factors to this code are the songs, the artists, duration values, energy values, the implementation of the merge sort, and the visual component of the app that displace the merge sort in action, and the final sorted playlist.


ALGORITHM DESIGN
The algorithm design in this code will be smooth and efficient. The program will begin by taking user inputs from the GUI and converting it into a consistent playlist data structure that the algorithm can work with. That data will then be passed into the merge sort, dividing the playlist repeatedly and merging them back together in a sorted structure. Throughout this process, the code will also record each comparison and merge step, so the final output includes both the sorted playlist, and a readable explanation of how the algorithm reached that result. Finally, the output of the playlist and the log of the sorting steps will be formatted and returned to the interface, finishing a code where data flows logically from user input, through the sorting algorithm, and back to the user in an understandable form.

Hugging Face Link


Steps to Run
This app requires an input of songs, their artists, the duration of the songs, and an energy rating from 0 – 100. Make sure the data is inputted in comma separated format, and in the same order for each input. The outputs will consist of the sorted playlist (depending on which category you select), and a bar graph that shows the steps of how the playlist was sorted.
Sorted by Duration

Sorted by Energy






Empty Inputs



Testing
I tested each sorting type with the same five songs to make sure that the code changed correctly according to which sorting type was selected. I expected the sorted playlist and a visual representation of how it was sorted, and that is exactly what I got. I also tested how the code would function if there were no inputs, and the output was as expected (“No songs to sort!”). Lastly, I tested one inputted song into the code, and the code returned that song and the single bar in the bar graph as expected.

Acknowledgement
The only non-AI source I used was the provided examples of apps (https://huggingface.co/spaces/RuslanKain/sorting-searching-recognized-gestures) and the Gradio beginner video (https://www.youtube.com/watch?v=xqdTFyRdtjQ). Other than that, I used Copilot (Microsoft Copilot: Your AI companion) to help me develop and structure the code and give me ideas as to how to program it. I used Claude.AI (Claude) when I needed help with the actual implementation of the code.