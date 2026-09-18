import os
import subprocess
import sys

def build():
    print("=======================================================")
    print("Building Standalone Windows Executable (.exe) IndexRadar Pro")
    print("=======================================================")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=IndexRadar",
        "--icon=indexradar_icon.ico",
        "--add-data=indexradar_icon.ico;.",
        "--add-data=indexradar_icon.png;.",
        "--distpath=dist",
        "--workpath=build",
        "--collect-all=customtkinter",
        "--collect-all=selenium",
        "main.py"
    ]

    print("Executing command:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_path = os.path.abspath("dist/IndexRadar.exe")
        print("\n=======================================================")
        print("BUILD EXECUTABLE SUCCESSFUL!")
        print(f"Executable created at:\n{exe_path}")
        print("=======================================================\n")

        # Cek Inno Setup Compiler jika terpasang
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe"
        ]
        iscc_exe = next((p for p in inno_paths if os.path.exists(p)), None)
        if iscc_exe:
            print("Compiling Inno Setup Installer (.exe Wizard)...")
            os.makedirs("Output", exist_ok=True)
            iscc_res = subprocess.run([iscc_exe, "installer_setup.iss"])
            if iscc_res.returncode == 0:
                print("=======================================================")
                print("INSTALLER CREATED SUCCESSFULLY in Output/ folder!")
                print("=======================================================")
        else:
            print("[INFO] Inno Setup Compiler (ISCC.exe) tidak ditemukan secara otomatis.")
            print("Anda dapat mengompilasi file installer_setup.iss menggunakan Inno Setup Compiler.")
    else:
        print("\nBUILD FAILED! Periksa log error di atas.")

if __name__ == "__main__":
    build()
