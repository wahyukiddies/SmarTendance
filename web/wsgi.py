from flask_app import create_app
# from .extensions import socketio

app = create_app(testing=False) # Change to True for testing purposes

if __name__ == "__main__":
	# socketio.run(app)
	app.run(host='0.0.0.0', port=5000)
