import os
import subprocess
import shutil

def create_executable():
    # Name of your main Python script
    main_script = "pdf_editor.py"  # Replace with your actual script name

    # Name for the output executable
    exe_name = "PdfEditor"

    # Icon file name
    icon_file = "pdf_editing_icon.webp"

    # Ensure the icon file exists
    if not os.path.exists(icon_file):
        raise FileNotFoundError(f"Icon file '{icon_file}' not found.")

    # PyInstaller command
    command = [
        "pyinstaller",
        "--name=" + exe_name,
        "--onefile",
        "--windowed",
        f"--icon={icon_file}",
        f"--add-data={icon_file};.",  # Include the icon file in the executable
        "--noconsole",  # Prevents console window from appearing
        main_script
    ]

    # Run PyInstaller
    subprocess.run(command, check=True)

    print(f"Executable created successfully: {exe_name}")

    # Clean up PyInstaller build files
    print("Cleaning up build files...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists(f"{exe_name}.spec"):
        os.remove(f"{exe_name}.spec")

    print("Build process completed.")

if __name__ == "__main__":
    create_executable()