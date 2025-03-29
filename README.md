An LLM agent implementation in python.
=

Open Source Week day 4 release!

capabilities:
-
Tool usage:

The tools the agent is able to use out of the box are Python and Powershell. Tools are modular and are easily added, the agent itself is designed to take advantage of this and has the ability and knowledge to add tools to itself that it can then use, if prompted to do so.

Lessons:

Lessons are separate from tools, they are something I implemented to allow teaching the agent things other than tool usage, like how to behave in certain situations.

Practical problem-solving:

The agent has been tested on many tasks, all of which it achieved, for example:\
"Find the game Terraria on my pc and launch it for me."\
"Download the transcription of this Kurzgesagt YouTube video, read over it and tell me your thoughts."\
"Rename all the files in this folder following this specific complicated pattern based on their existing names: "

---

multi paradigm support:
-
The agent has been tested using openai gpt4 api, and locally hosted Dolphin model. naturally, the best results are achieved with openai api.
