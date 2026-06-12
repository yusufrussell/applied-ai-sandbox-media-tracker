from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for, abort

from models import MediaCategory, MediaItem, MediaLibrary, MediaStatus
from storage import load, save


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "media-tracker-dev-key"

    app.library: MediaLibrary = load()  # type: ignore[attr-defined]

    @app.context_processor
    def inject_categories() -> dict:
        return {
            "categories": list(MediaCategory),
            "category_counts": {
                cat: len(app.library.filter_by_category(cat))
                for cat in MediaCategory
            },
        }

    @app.route("/")
    def home():
        cat_param = request.args.get("category", "")
        status_param = request.args.get("status", "")

        active_category = None
        if cat_param:
            try:
                active_category = MediaCategory(cat_param)
            except ValueError:
                pass

        active_status = None
        if status_param:
            try:
                active_status = MediaStatus(status_param)
            except ValueError:
                pass

        cats_to_show = [active_category] if active_category else list(MediaCategory)
        grouped: dict = {}
        for cat in cats_to_show:
            items = app.library.filter_by_category(cat)
            if active_status:
                items = [i for i in items if i.status == active_status]
            grouped[cat] = items

        total = sum(len(v) for v in grouped.values())
        return render_template(
            "home.html",
            grouped=grouped,
            total=total,
            active_category=active_category,
            active_status=active_status,
            statuses=list(MediaStatus),
        )

    @app.route("/add", methods=["GET", "POST"])
    def add():
        errors: dict[str, str] = {}
        form: dict[str, str] = {}

        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            category = request.form.get("category", MediaCategory.MOVIE.value)
            status = request.form.get("status", MediaStatus.PLANNING.value)
            rating_raw = (request.form.get("rating") or "").strip()
            notes = (request.form.get("notes") or "").strip()

            form = {
                "title": title,
                "category": category,
                "status": status,
                "rating": rating_raw,
                "notes": notes,
            }

            if not title:
                errors["title"] = "Title is required."

            rating: int | None = None
            if rating_raw:
                try:
                    rating = int(rating_raw)
                    if not 1 <= rating <= 10:
                        errors["rating"] = "Rating must be between 1 and 10."
                        rating = None
                except ValueError:
                    errors["rating"] = "Rating must be a whole number."

            if not errors:
                item = MediaItem.from_dict({
                    "title": title,
                    "category": category,
                    "status": status,
                    "rating": rating,
                    "notes": notes,
                })
                app.library.add(item)
                save(app.library)
                return redirect(url_for("home"))

        return render_template(
            "add.html",
            form=form,
            errors=errors,
            statuses=list(MediaStatus),
        )

    @app.route("/media/<item_id>")
    def detail(item_id: str):
        item = app.library.get(item_id)
        if item is None:
            abort(404)
        return render_template(
            "detail.html",
            item=item,
            statuses=list(MediaStatus),
            errors={},
            form={},
        )

    @app.route("/media/<item_id>/edit", methods=["POST"])
    def edit(item_id: str):
        item = app.library.get(item_id)
        if item is None:
            abort(404)

        status_raw = request.form.get("status", "")
        rating_raw = (request.form.get("rating") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        errors: dict[str, str] = {}

        try:
            new_status = MediaStatus(status_raw)
        except ValueError:
            errors["status"] = "Invalid status."
            new_status = item.status

        new_rating: int | None = None
        if rating_raw:
            try:
                new_rating = int(rating_raw)
                if not 1 <= new_rating <= 10:
                    errors["rating"] = "Rating must be between 1 and 10."
                    new_rating = item.rating
            except ValueError:
                errors["rating"] = "Rating must be a whole number."
                new_rating = item.rating

        if errors:
            return render_template(
                "detail.html",
                item=item,
                statuses=list(MediaStatus),
                errors=errors,
                form={"status": status_raw, "rating": rating_raw, "notes": notes},
            )

        item.status = new_status
        item.rating = new_rating
        item.notes = notes
        save(app.library)
        return redirect(url_for("detail", item_id=item_id))

    @app.route("/media/<item_id>/delete", methods=["POST"])
    def delete(item_id: str):
        if not app.library.remove(item_id):
            abort(404)
        save(app.library)
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
