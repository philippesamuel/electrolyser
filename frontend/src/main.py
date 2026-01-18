from dash_chart import app

server = app.server


def main():
    app.run(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    main()
