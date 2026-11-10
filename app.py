"""Flask photo editor app with user authentication, image editing, and gallery features."""

import os
import re
import uuid
from base64 import b64encode

from cs50 import SQL
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from PIL import Image, ImageFilter, ImageOps
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required

app = Flask(__name__)
db = SQL("sqlite:///photo.db")

# Configure server-side session storage so login state persists without storing
# sensitive user data in browser cookies.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.confing["SESSION_FILE_DIR"] = "/tmp/flask_session"

Session(app)


def user_login(username, password):
    """Validate login credentials and create the user's session if they are valid."""

    if not username:
        return "Please provide a username."

    elif not password:
        return "Please provide a password."

    rows = db.execute(
        "SELECT * FROM users WHERE username = ?", request.form.get("username")
    )

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return "The username or password is incorrect."

    session["user_id"] = rows[0]["id"]
    return None


def user_signup(username, password, confirmation):
    """Create a new user account after validating the submitted signup details."""

    if not username:
         message = "Please provide a username."

    elif not password:
         message = "Please provide a password."
     
    elif not confirmation:
         message = "Please confirm your password."

    elif password != confirmation:
         message = "The passwords do not match."
     
    elif db.execute("SELECT * FROM users WHERE username = ?", username):
         message = "That username is already taken. Please choose another."
     
    else:
         message = None

    if message:
        return message
     
    password_hash = generate_password_hash(password)

    db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
    x = db.execute("SELECT id FROM users WHERE username = ? ", username)
    session["user_id"] = x[0]["id"]
    return None
    


def validate_filename(filename_by_user, user_id):
    """Check that a gallery name is valid and unique for the current user."""
    if not filename_by_user:
        return "Please provide a filename."

    if len(filename_by_user) > 99:
        return "Filenames must be less than 100 characters long."

    if re.search(r"\.[^./\\]+$", filename_by_user):
        return "Please provide a filename without an extension."

    x = db.execute(
        "SELECT * FROM images WHERE user_id=? AND filename_by_user=?",
        user_id,
        filename_by_user,
    )

    if x:
        return "This filename already exists in your gallery, please choose another."

    return None


def save_image():
    """Persist the in-progress edited image to the user's permanent gallery."""
    user_id = session.get("user_id")
    filename_by_user = session.get("filename_by_user")
    filename = session.get("filename")

    if not user_id:
        return redirect(url_for("p_login"))

    if not filename or filename_by_user is None:
        return render_template(
            "error2.html",
            message="There is no edited image waiting to be saved.",
            retry_url=url_for("create"),
        )

    message = validate_filename(filename_by_user, user_id)
    if message:
        return render_template(
            "error2.html",
            message=message,
            retry_url=url_for("back"),
        )

    temp_filepath = os.path.join(app.root_path, "temp", filename)
    save_filepath = os.path.join(app.root_path, "save", filename)

    if not os.path.isfile(temp_filepath):
        return render_template(
            "error2.html",
            message="The edited image is no longer available. Please choose it again.",
            retry_url=url_for("create"),
        )

    os.makedirs(os.path.dirname(save_filepath), exist_ok=True)
    os.replace(temp_filepath, save_filepath)
    db.execute(
        "INSERT INTO images (user_id, filename, filename_by_user, filepath) "
        "VALUES (?, ?, ?, ?)",
        user_id,
        filename,
        filename_by_user,
        os.path.join("save", filename),
    )
    session.pop("filename", None)
    session.pop("filename_by_user", None)
    return redirect(url_for("gallery"))


@app.route("/pending", methods=["POST"])
def pending():
    """Receive the final edited image, store it in the temp folder,take sanity check and continue the save flow."""
    user_id = session.get("user_id")

    output = request.files.get("output_image")
    filename_by_user = request.form.get("filename", "").strip()

    if not output:
        return render_template(
            "error2.html",
            message="No image received.",
            retry_url=url_for("create"),
        )

    filename = f"{uuid.uuid4()}.jpg"
    temp_directory = os.path.join(app.root_path, "temp")
    filepath = os.path.join(app.root_path, temp_directory, filename)

    os.makedirs(temp_directory, exist_ok=True)

    try:
        with Image.open(output) as image:
            image.convert("RGB").save(filepath, format="JPEG")
    except (OSError, ValueError):
        return render_template(
            "error2.html",
            message="The uploaded image could not be read. Please choose another image.",
            retry_url=url_for("create"),
        )

    previous_filename = session.get("filename")
    if previous_filename and previous_filename != filename:
        previous_filepath = os.path.join(temp_directory, previous_filename)
        if os.path.isfile(previous_filepath):
            os.remove(previous_filepath)

    session["filename"] = filename
    session["filename_by_user"] = filename_by_user

    if user_id:
        return save_image()

    return redirect(url_for("p_login"))

 
                                                                                                        
@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Display the login form and authenticate users when they submit credentials."""
    if request.method == "GET":
        return render_template("login.html")

    else:
         username = request.form.get("username")
         password = request.form.get("password")

         message = user_login(username, password)

         if message:
                     return render_template(                  
                         "error.html",                                                                           
                         message=message,                          
                         retry_url=url_for("login"),
                         retry_label="Return to log in",
                     )
         
         return redirect("/gallery")
    
  
    
@app.route("/create", methods=["GET", "POST"])
def create():
    """Show the editing screen and apply the chosen filter to an uploaded image."""
    if request.method == "GET":
        return render_template("create.html")

    im = request.files.get("image")
    selected_filter = request.form.get("filter")

    if not im:
        return render_template("error2.html", message="Please upload an image.",
                               retry_url=url_for("create"),        
                               )
    valid_filters = {
        "normal",
        "grayscale",
        "blur",
        "sharpen",
        "smooth",
        "detail",
        "invert",
        "mirror",
    }
    if selected_filter not in valid_filters:
        return render_template("error2.html", message="Invalid filter selected.",
                               retry_url=url_for("create"),
                               )  
          
    with Image.open(im) as image:
        image = image.convert("RGB")

        if selected_filter == "grayscale":
            output = ImageOps.grayscale(image)
        elif selected_filter == "blur":
            output = image.filter(ImageFilter.BLUR)
        elif selected_filter == "sharpen":
            output = image.filter(ImageFilter.SHARPEN)
        elif selected_filter == "smooth":
            output = image.filter(ImageFilter.SMOOTH)
        elif selected_filter == "detail":
            output = image.filter(ImageFilter.DETAIL)
        elif selected_filter == "invert":
            output = ImageOps.invert(image)
        elif selected_filter == "mirror":
            output = ImageOps.mirror(image)
        else:
            output = image

        return render_template("create.html", output=output)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Display the signup form and create a new account when the form is valid."""
    if request.method == "GET":
        return render_template("signup.html")

    else:
         username = request.form.get("username")
         password = request.form.get("password")
         confirmation = request.form.get("confirmation")

         message = user_signup(username, password, confirmation)

         if message:
                     
          return render_template(                  
              "error.html",                                                                           
              message=message,                          
              retry_url=url_for("signup"),
              retry_label="Return to sign up",
          )
    
         return redirect("/gallery")


@app.route("/gallery")
@login_required
def gallery():
    """Show the signed-in user's saved images in reverse chronological order."""
    user_id = session["user_id"]

    user_gallery = db.execute("SELECT * FROM images WHERE user_id =? ORDER BY timestamp DESC" , user_id)
    
    return render_template("gallery.html", user_gallery = user_gallery)


@app.route("/images/<filename>")
@login_required
def image(filename):
    """Serve an image file only if it belongs to the logged-in user."""
    user_id = session["user_id"]
    images = db.execute(
        "SELECT filename, filename_by_user FROM images WHERE user_id = ? AND filename = ?",
        user_id,
        filename,
    )

    if not images:
        abort(404)

    return send_from_directory(os.path.join(app.root_path, "save"), images[0]["filename"])


@app.route("/download/<filename>")
@login_required
def download(filename):
    """Send a saved image to the browser as a downloadable JPG file."""
    user_id = session["user_id"]
    images = db.execute(
        "SELECT filename, filename_by_user FROM images WHERE user_id = ? AND filename = ?",
        user_id,
        filename,
    )

    if not images:
        abort(404)

    return send_from_directory(
        os.path.join(app.root_path, "save"),
        images[0]["filename"],
        as_attachment=True,
        download_name=f'{images[0]["filename_by_user"]}.jpg',
    )



# Delete a single image from storage and from the database for the current user.
@app.route("/delete/<filename>", methods=["POST"])
@login_required
def delete(filename):
    # Confirm the image belongs to this user, then remove its file and record.
    user_id = session["user_id"]
    images = db.execute(
        "SELECT filename FROM images WHERE user_id = ? AND filename = ?",
        user_id,
        filename,
    )

    if not images:
        abort(404)

    filepath = os.path.join(app.root_path, "save", images[0]["filename"])
    if os.path.isfile(filepath):
        os.remove(filepath)

    db.execute(
        "DELETE FROM images WHERE user_id = ? AND filename = ?",
        user_id,
        filename,
    )
    return redirect("/gallery")

# End the active session and return the user to the public home page.
@app.route("/logout")
@login_required
def logout():
    # Clear the signed-in user's session and return to the home page.
    session.clear()
    return redirect("/")


# Return the user to the editor while restoring the in-progress image preview.
@app.route("/back", methods=["POST"])
def back():
    filename = session.get("filename")
    destination = request.form.get("destination")

    if destination == "home":
        if filename:
            filepath = os.path.join(app.root_path, "temp", filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        session.pop("filename", None)
        session.pop("filename_by_user", None)
        return redirect(url_for("index"))

    if not filename:
        return render_template(
            "error2.html",
            message="There is no pending image to edit.",
            retry_url=url_for("create"),
        )

    filepath = os.path.join(app.root_path, "temp", filename)
    if not os.path.isfile(filepath):
        session.pop("filename", None)
        session.pop("filename_by_user", None)
        return render_template(
            "error2.html",
            message="The pending image is no longer available. Please choose it again.",
            retry_url=url_for("create"),
        )

    with open(filepath, "rb") as image_file:
        image_data = b64encode(image_file.read()).decode("ascii")
    os.remove(filepath)

    filename_by_user = session.get("filename_by_user", "")
    session.pop("filename", None)
    session.pop("filename_by_user", None)

    return render_template(
        "create.html",
        output=True,
        output_url=f"data:image/jpeg;base64,{image_data}",
        filename_by_user=filename_by_user,
    )


# Login flow used when a user is in the editing process and needs to save later.
@app.route("/p_login", methods=["GET", "POST"])
def p_login():
    # Display the login form, or check submitted credentials and start a session.
    if request.method == "GET":
        return render_template("p_login.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")

        message = user_login(username, password)

        if message:
            return render_template(                  
                "error.html",                                                                           
                message=message,                          
                retry_url=url_for("p_login"),
                retry_label="Return to log in",
            )

        if session.get("filename"):        
            return save_image()
        return redirect(url_for("gallery"))


@app.route("/p_signup", methods=["GET", "POST"])
def p_signup():        
    
    if request.method == "GET":
        return render_template("p_signup.html")

    else:
         username = request.form.get("username")
         password = request.form.get("password")
         confirmation = request.form.get("confirmation")

         message = user_signup(username, password, confirmation)

         if message:
            return render_template(                  
                "error.html",                                                                           
                message=message,                          
                retry_url=url_for("p_signup"),
                retry_label="Return to sign up",
            )
             
         if session.get("filename"):
             return save_image()
         return redirect(url_for("gallery"))



