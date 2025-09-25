from django.core.management import execute_from_command_line
import os
import sys
import dotenv
if __name__ == '__main__':
    dotenv.load_dotenv()
    execute_from_command_line(sys.argv)
