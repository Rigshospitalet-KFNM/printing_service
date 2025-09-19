import subprocess

def list_printers():
    result = subprocess.run(
        ["lpstat", "-h", "hopper.petnet.rh.dk:631/version=1.1", "-l", "-p"],
        capture_output=True
    )
    # try utf-8, fallback to latin-1
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return result.stdout.decode("latin-1") #handle danish characters

print(list_printers())
