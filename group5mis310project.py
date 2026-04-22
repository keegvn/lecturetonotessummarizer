import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from openai import OpenAI

#api key
API_KEY = "-----"

client = OpenAI(api_key=API_KEY)

class LectureToNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lecture to Notes Summarizer")
        self.root.geometry("960x740")
        self.root.configure(bg="#f0f4f8")

        self.file_path = None
        self.transcript = ""
        self.notes = ""

        self.create_ui()

    def create_ui(self):

        tk.Label(self.root, text="Lecture to Notes Summarizer",
                 font=("Arial", 20, "bold"), bg="#f0f4f8", fg="#1e3a8a").pack(pady=20)

        #file Selection
        file_frame = tk.Frame(self.root, bg="#f0f4f8")
        file_frame.pack(fill="x", padx=30, pady=10)

        tk.Label(file_frame, text="Audio File:", font=("Arial", 11), bg="#f0f4f8").pack(side="left")
        self.file_label = tk.Label(file_frame, text="No file selected", fg="gray", bg="#f0f4f8")
        self.file_label.pack(side="left", padx=15)

        tk.Button(file_frame, text="Browse", width=15, command=self.browse_file).pack(side="right")

        #buttons
        btn_frame = tk.Frame(self.root, bg="#f0f4f8")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="1. Transcribe Audio", font=("Arial", 11, "bold"),
                  bg="#2563eb", fg="white", width=22, command=self.transcribe_audio).pack(side="left", padx=10)

        self.notes_btn = tk.Button(btn_frame, text="2. Generate Structured Notes", font=("Arial", 11, "bold"),
                                   bg="#16a34a", fg="white", width=25, command=self.generate_notes, state="disabled")
        self.notes_btn.pack(side="left", padx=10)

        #status
        self.status_label = tk.Label(self.root, text="Ready - Please select an audio file",
                                    fg="gray", bg="#f0f4f8", font=("Arial", 10))
        self.status_label.pack(pady=8)

        #transcript Area
        tk.Label(self.root, text="Raw Transcript:", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(anchor="w", padx=30)
        self.transcript_area = scrolledtext.ScrolledText(self.root, height=10, font=("Arial", 10))
        self.transcript_area.pack(fill="x", padx=30, pady=5)

        #notes Area
        tk.Label(self.root, text="Structured Notes:", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(anchor="w", padx=30)
        self.notes_area = scrolledtext.ScrolledText(self.root, height=16, font=("Arial", 10))
        self.notes_area.pack(fill="both", expand=True, padx=30, pady=8)

        #save Button
        tk.Button(self.root, text="Save Notes as Markdown", bg="#eab308", fg="black",
                  font=("Arial", 11), command=self.save_notes).pack(pady=12)

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.mp4 *.mpeg *.webm")]
        )
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path), fg="black")
            self.status_label.config(text="File loaded → Click 'Transcribe Audio'", fg="blue")

    def transcribe_audio(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select an audio file first!")
            return

        self.status_label.config(text="Transcribing audio... (this may take 30-90 seconds)", fg="orange")
        self.root.update()

        try:
            with open(self.file_path, "rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en",
                    response_format="text"
                )

            self.transcript = result
            self.transcript_area.delete(1.0, tk.END)
            self.transcript_area.insert(tk.END, self.transcript)

            self.notes_btn.config(state="normal")
            self.status_label.config(text="Transcription complete! Now click 'Generate Structured Notes'", fg="green")

        except Exception as e:
            messagebox.showerror("Transcription Error", str(e))
            self.status_label.config(text="Transcription failed", fg="red")

    def generate_notes(self):
        if not self.transcript:
            messagebox.showerror("Error", "No transcript available!")
            return

        self.status_label.config(text="Generating clean structured notes...", fg="orange")
        self.root.update()

        try:
            prompt = f"""You are an excellent academic assistant. 
Convert the following lecture transcript into clean, well-organized study notes using markdown format.

**Lecture Title:** [Short, descriptive title]

**Main Topics:**
- ...

**Detailed Notes:**
[Organized with headings and bullet points]

**Key Takeaways:**
• ...
• ...

**Important Terms:**
- Term: definition

Transcript:
{self.transcript}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2200
            )

            self.notes = response.choices[0].message.content

            self.notes_area.delete(1.0, tk.END)
            self.notes_area.insert(tk.END, self.notes)

            self.status_label.config(text="✅ Notes generated successfully!", fg="green")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate notes:\n{str(e)}")
            self.status_label.config(text="Notes generation failed", fg="red")

    def save_notes(self):
        if not self.notes:
            messagebox.showwarning("Nothing to save", "Please generate notes first.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown File", "*.md"), ("Text File", "*.txt")]
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.notes)
            messagebox.showinfo("Saved", f"Notes successfully saved to:\n{save_path}")


#run gui
if __name__ == "__main__":
    root = tk.Tk()
    app = LectureToNotesApp(root)
    root.mainloop()