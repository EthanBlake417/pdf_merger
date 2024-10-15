import os
import subprocess
import shutil


def create_dmg():
    # Name of your main Python script
    main_script = "pdf_editor.py"  # Replace with your actual script name

    # Name for the output application
    app_name = "PdfEditor"

    # Icon file name
    icon_file = "pdf_editing_icon.icns"  # Note: For macOS, you need a .icns file

    # Ensure the icon file exists
    if not os.path.exists(icon_file):
        raise FileNotFoundError(f"Icon file '{icon_file}' not found.")

    # PyInstaller command
    command = [
        "pyinstaller",
        "--name=" + app_name,
        "--windowed",
        f"--icon={icon_file}",
        f"--add-data={icon_file}:.",  # Include the icon file in the app bundle
        "--osx-bundle-identifier=com.yourcompany.pdfeditor",  # Replace with your bundle identifier
        main_script
    ]

    # Run PyInstaller
    subprocess.run(command, check=True)

    print(f"Application bundle created successfully: {app_name}.app")

    # Create a temporary directory for the DMG contents
    dmg_dir = "dmg_contents"
    os.makedirs(dmg_dir, exist_ok=True)

    # Move the .app bundle to the DMG directory
    shutil.move(f"dist/{app_name}.app", dmg_dir)

    # Create a symbolic link to the Applications folder
    os.symlink("/Applications", os.path.join(dmg_dir, "Applications"))

    # Create the DMG
    dmg_name = f"{app_name}.dmg"
    subprocess.run([
        "hdiutil",
        "create",
        "-volname", app_name,
        "-srcfolder", dmg_dir,
        "-ov",
        "-format", "UDZO",
        dmg_name
    ], check=True)

    print(f"DMG created successfully: {dmg_name}")

    # Clean up
    print("Cleaning up...")
    shutil.rmtree(dmg_dir)
    shutil.rmtree("build")
    shutil.rmtree("dist")
    os.remove(f"{app_name}.spec")

    print("DMG creation process completed.")


if __name__ == "__main__":
    create_dmg()
