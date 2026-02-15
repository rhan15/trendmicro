import sys
from app import create_app

app = create_app()

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        # exe mode
        app.run(debug=False, 
                use_reloader=False, 
                host="0.0.0.0", 
                port=3001, 
                threaded=True)
    else:
        # dev mode
        app.run(debug=True, 
                use_reloader=False, 
                host="0.0.0.0", 
                port=3001, 
                threaded=True)
