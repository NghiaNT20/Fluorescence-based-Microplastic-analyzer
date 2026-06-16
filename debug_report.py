from generate_report_v2 import create_report
import traceback

try:
    create_report()
except Exception as e:
    traceback.print_exc()
