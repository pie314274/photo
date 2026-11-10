# The Pixel
#### Video Demo :  <https://www.youtube.com/watch?v=wMAl__ejl_M>
### Description:
The Pixel is a web-based image processing application that allows users to upload images, apply various image filters and adjust brightness, contrast and  saturation. Then users can download images or save in his/her gallery (saving needs to login). And also users can download and delete images from their gallery.

Unlike install dedicated image-editing softwares, it allows users to edit image, save it in gallery by loging in  and view it without install in users own devieces.

## Features:

- ### Image Upload
- ### Image Processing:
  - **Filters**
    -  Grayscale
    - Blur
    - Sharpen
    - Smooth
    - Detail
    - Invert
    - Mirror
  - **Adjustments**
    -  Brightness
    - Contrast
    - Saturation 
- ### Image Download
- ### User Authentication
- ### Image saving for logged in users
- ### Personal Gallery
## Used Technologies
- Python
- Flask 
- Flask-Session
- Pillow (PLI) 
- SQLite
- HTML
- CSS
- Bootswatch
- JavaScript

## Project Structure

### **photo/**
- > **save**
- > **static** /
  - script.js
  - styles.css
- > **temp**
- > **templates** /
  - create.html
  - error.html
  - error2.html
  - gallery.html   
  - index.html
  - layout.html
  - login.html
  - p_login.html
  - p_signup.html
  - signup.html
- app.py
- helper.py
- photo.db
- requirements.txt
- README.md

## Directory and File Descriptions :

- ## Directories :
  - ### save:
      **save** stores images which are saved by authenticated users.

  - ### static:
      **static** contains **CSS** and **JavaScript** for this project.

  - ### temp:
     **temp**  folder temporarily stores processed images awaiting authentication and  sanity check.

  - ### templates:
     **templates** contains **HTML** templates.

- ## Files :
  - ## HTML Files
    - ### create.html :
        **create.html** provides the photo editor for uploading, adjusting, previewing, saving, and downloading images.
  
    - ###  error.html :
       **error.html** shows login-related error message.
  
    - ### error2.html :
       **error2.html** shows filename and editing related error message.
  
    - ### gallery.html :
       **gallery.html** shows the user gallery. 
  
    - ### index.html:
       **index.html** shows the homepage of the application.
  
    - ### layout.html:
        **layout.html** provides the shared page structure and loads Bootstrap and project styles.
  
    - ### login.html:
        **login.html** provides the standard login form for returning users to access their account and gallery.
  
    - ### p_login.html :
        **p_login.html** is the post-edit login screen that prompts a user to sign in before saving the current edited image.
    
    - ### p_signup.html :
        **p_signup.html** is the post-edit sign-up page that lets a user create an account before saving an image to the gallery.
    
    - ### signup.html :
        **signup.html** provides the account creation form for new users who want to register before using the app.


  - ## JavaScript File
    - ### script.js :
        **script.js** manages image uploads, editing previews, and editor downloads.

  - ## CSS File
    - ### styles.css :
        **styles.css** styles the application pages, forms, and error messages.


  - ## Python Files 
    - ### app.py :
       **app.py** contains the backend of this application. It handles the application's core logic, routing, authentication and database operations.

       #### **It includes the following functions :**
       - **user_login() :**

           It validates login credentials and creates the user's session if they are valid.

      - **user_signup :**

          It creates a new user account after validating the submitted signup details.

      - **validate_filename() :**

          It validates the filename a user submits when saving an image.

      - **index() :**

          **Route :** `/index`

          **Method :** `GET`  

          **Purpose :** Displaying the homepage.

      - **login() :**

          **Route :** `/login`

          **Method :** `GET`,`POST`

          **Purpose :** Displaying  the standard login form and authenticate users  by calling  `user_login()` and then redirect to` /gallery` .   

      - **signup() :**

        **Route :** `/signup`

        **Method :** `GET` , `POST`

        **Purpose :** Displaying standard signup form  and creating a user account by calling `user_signup()` and then redirect to `/gallery` .

      - **create() :**

        **Route :** `/create`

        **Method :** `GET` , `POST`

        **Purpose :** Showing the editing screen and applying the chosen filter to an uploaded image.

      - **pending() :**

        **Route :** `/pending`

        **Method :** `POST`

        **Purpose :**  Receiving the final edited image, storing it in the temp folder, taking sanity check and continuing the save flow.  

      - **p_login() :**

         **Route :** `/p_login`

         **Method :** `GET` , `POST`

         **Purpose :** When a user trying to save image but he/she is not loged in , showing him/her login form and authenticating users  by calling `user_login()`   then saving the image.

      - **p_signup :**

        **Route :** `/p_signup`
        
        **Method :** `GET` , `POST`

        **Purpose :** When a user trying to save image but he/she  dose not have an account, showing him/her signup form and create an account by calling `user_signup()` then saving the image.

      - **back() :**

        **Route :** `/back`

        **Method :**  `POST`

        **Purpose :** Returning to homepage or editor when an error occurs during saving an image.

      - **save() :**
        
         It saves an image in the user's personal gallery.

      - **gallery() :**

        **Route :** `/gallery`

        **Method :** `GET`

        **Purpose :** Showing the signed-in user's saved images in reverse chronological order in user's personal gallery.   

      - **image() :**

        **Route :** `/images/<filename>`

        **Method :** `GET`

        **Purpose :** Serving an image file only if it belongs to the logged-in user. 

      - **download() :**

        **Route :** `/download/<filename>`

        **Method :** `GET`

        **Purpose :** Sending a saved image to the browser as a downloadable JPG file.

      - **delete() :**

        **Route :** `/delete/<filename>`

        **Method :** `POST`

        **Purpose :** Deleting a single image from a user's gallery.

      - **logout() :**

        **Route :** `/logout`

        **Method :** `GET`

        **Purpose :** Logging out a user.         

    - ### helper.py :
        **helper.py** contains the **login_required()** function whose purpose is to confirm that a user is logged in.

  - ### photo.db :
     **photo.db** contains the application's database.


  - ### requirements.txt :  
     **requirements.txt** lists all python packages and their dependencies required to install and run the application.

  ## Database Structure :

  The application’s database uses SQLite and it has two tables:
  - ### users :
     **Schema :**
        
        CREATE TABLE users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        username TEXT NOT NULL,
        hash TEXT NOT NULL);

        CREATE UNIQUE INDEX username ON users (username);


  - ### images :
    **Schema :**

        CREATE TABLE images 
        (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL, 
        filename_by_user TEXT NOT NULL,  
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
        filepath TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id));

        CREATE UNIQUE INDEX filename ON images (filename);
        CREATE INDEX user_id ON images (user_id);
     
     