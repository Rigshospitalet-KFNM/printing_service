from printing.services import CupsCLIService

cups = CupsCLIService()
#result = cups.print("maria", "/home/Mathias/Testing/testfile.ps", user="tester")
#print(result)
printers = cups.list_printers()
print(printers.get("maria"))
print(printers.get("maria").device_uri) # type: ignore
print(printers.get("maria").is_reachable()) # type: ignore