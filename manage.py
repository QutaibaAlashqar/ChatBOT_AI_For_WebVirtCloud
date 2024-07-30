import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_ai_part.settings')
    print("DJANGO_SETTINGS_MODULE set to:", os.environ['DJANGO_SETTINGS_MODULE'])
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    print("Command line arguments:", sys.argv)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()