# Entry point for all to avoid circular imports
from main import app
from views import *


if __name__ == "__main__":
    app.run(debug=True)
