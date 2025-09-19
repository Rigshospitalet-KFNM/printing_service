import re
import subprocess
from objects import Printer, Job


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
        lines = raw_text.splitlines()
        pattern = re.compile(
            r"printer (\S+) is (\w+)(?: (\d+) job)?\. +enabled since (.+)"
        )
        for line in lines:
            match = pattern.match(line)
            if match:
                name, status, jobs, since = match.groups()
                jobs = int(jobs) if jobs else 0
                printers[name] = Printer(name=name, status=status, jobs=jobs, since=since)
        return printers

