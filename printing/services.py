import re
import subprocess
from printing.objects import Printer, Job


class CupsCLIService:
    def list_printers(self):
        raw_text = self._run_lpstat()
        return self._parse_printers(raw_text)


    #subprocesses
    def _run_lpstat(self):
        result = subprocess.run(
            ["lpstat", "-h", "hopper.petnet.rh.dk:631/version=1.1", "-l", "-p"],
            capture_output=True
        )
    
        return result.stdout.decode("latin-1") #Should be UTF-8 but hopper is too old


    #parsing
    def _parse_printers(self, raw_text):
        printers = {}
        blocks = raw_text.split("\nprinter ")
        for block in blocks:

            block = block.strip()
            if not block:
                continue
            if not block.startswith("printer "):
                block = "printer " + block

            lines = block.splitlines()
            header = lines[0]
            details = lines[1:]

            # parse header
            m = re.match(
                r"printer (\S+) is (\w+)(?: (\d+) job)?\. +(\w+) since (.+)",
                header
            )
            if not m:
                continue
            name, status, jobs, enabled, since = m.groups()
            jobs = int(jobs) if jobs else 0
            enabled = enabled.lower() == "enabled"

            # parse details
            desc, loc, error = None, None, None
            for line in details:
                line = line.strip()
                if line.startswith("Description:"):
                    desc = line.split(":", 1)[1].strip()
                elif line.startswith("Location:"):
                    loc = line.split(":", 1)[1].strip()
                elif "error" in line.lower():
                    error = line.strip()

            printers[name] = Printer(
                name=name,
                status=status,
                enabled=enabled,
                jobs=jobs,
                since=since,
                description=desc,
                location=loc,
                error=error,
            )
        return printers

