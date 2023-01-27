from api.main import create_app_instance

app = create_app_instance()

if __name__ == "__main__":
    app.run(debug=True)
