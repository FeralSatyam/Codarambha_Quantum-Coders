import customtkinter as ctk
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = {
    "Traffic Detection": os.path.join(BASE_DIR, "demo_4_lanes.py"),
    "Vehicle Detection (Camera)": os.path.join(BASE_DIR, "test_detector.py"),
    "2D Simulation": os.path.join(BASE_DIR, "traffic_sim_2d.py"),
}

def run_script(script_path):
    if not os.path.exists(script_path):
        print(f"Script {script_path} not found!")
        return
    app.withdraw()
    subprocess.call([sys.executable, script_path])
    app.deiconify()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")

# -------------------------------
# Main App
# -------------------------------
app = ctk.CTk()
app.title("Smart Traffic System Launcher")
app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")

# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")   # bluish theme

# Root layout
main_frame = ctk.CTkFrame(app, corner_radius=20)
main_frame.pack(expand=True, fill="both", padx=40, pady=40)

title = ctk.CTkLabel(
    main_frame,
    text="Smart Traffic Management System",
    font=ctk.CTkFont(size=36, weight="bold"),
    text_color="#ffffff"   # bluish accent
)
title.pack(pady=(30, 10))

subtitle = ctk.CTkLabel(
    main_frame,
    text="Real-time adaptive traffic control powered by AI.",
    font=ctk.CTkFont(size=16),
    text_color="#93c5fd"   # lighter blue
)
subtitle.pack(pady=(0, 30))

# Buttons
btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
btn_frame.pack(pady=20)

for name, path in SCRIPTS.items():
    btn = ctk.CTkButton(
        btn_frame,
        text=name,
        width=400,
        height=60,
        font=ctk.CTkFont(size=18, weight="bold"),
        corner_radius=12,
        fg_color="#142953",       # primary blue
        hover_color="#1d4ed8",    # darker blue hover
        command=lambda p=path: run_script(p)
    )
    btn.pack(pady=15)


# Exit button
exit_btn = ctk.CTkButton(
    main_frame,
    text="Exit",
    width=400,
    height=50,
    fg_color="#3b82f6",       # blue exit button
    hover_color="#1e40af",    # darker hover
    font=ctk.CTkFont(size=18, weight="bold"),
    corner_radius=12,
    command=app.quit
)
exit_btn.pack(pady=30)

app.mainloop()