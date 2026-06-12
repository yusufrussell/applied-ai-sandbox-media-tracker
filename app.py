from __future__ import annotations

from flask import Flask, render_template, abort

from models import MediaCategory, MediaLibrary
from storage import load


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "media-tracker-dev-key"

    app.library: MediaLibrary = load()  # type: ignore[attr-defined]

    @app.context_processor
    def inject_categories() -> dict:
        return {"categories": list(MediaCategory)}

    @app.route("/")
    def home():
        items = app.library.all()
        grouped = {
            cat: app.library.filter_by_category(cat)
            for cat in MediaCategory
        }
        return render_template("home.html", grouped=grouped, total=len(items))

    @app.route("/add", methods=["GET", "POST"])
    def add():
        # TASK 05 — full implementation
        return render_template("add.html")

    @app.route("/media/<item_id>")
    def detail(item_id: str):
        # TASK 07 — full implementation
        item = app.library.get(item_id)
        if item is None:
            abort(404)
        return render_template("detail.html", item=item)

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
