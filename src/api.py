import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False, port=5001) 