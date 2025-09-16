
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from final_objects import Post, Analytics
from final_db import get_attached_files
from datetime import datetime
from PIL import Image, ImageTk
import io
import sqlite3
import os


# Custom temp folder for opened files
temp_dir = os.path.join(os.getcwd(), "temp_files")
os.makedirs(temp_dir, exist_ok=True)

# SQLite database connection
conn = sqlite3.connect("final.db")
print("Using database at:", os.path.abspath("final.db"))
cursor = conn.cursor()


# Create the main application window
root = tk.Tk()
style = ttk.Style()
style.theme_use("clam")  # 'clam' allows more styling control
style.configure("TSpinbox", arrowsize=15, foreground="white", fieldbackground="#013220", background="#013220")
style.configure("TCombobox", foreground="white", fieldbackground="#013220", background="#013220")
style.map("TCombobox", fieldbackground=[("readonly", "#013220")])
root.title("Snoop Media Drop")
root.geometry("600x500")
root.configure(bg="#013220")  # Dark mode background


# Set the overall style for the app using ttk.
# This applies a dark green background with white text and custom button colors.
style = ttk.Style()
style.theme_use("default")
style.configure(".", background="#013220", foreground="white", font=("Segoe UI", 10))
style.map("TButton", foreground=[("pressed", "white"), ("active", "white")],
          background=[("pressed", "#3e3e3e"), ("active", "#3e3e3e")])


# Track attached file
attached_file_path = None
attached_files = []




# Function to reset to the initial post creation UI
def reset_to_main():
    for widget in root.winfo_children():
        widget.destroy()
    create_main_ui()

# This function displays a post's content along with its analytics, attached files, and comments.
# It also allows the user to like the post, add a comment, and navigate between other posts.
def show_post_screen(post, post_list=None, current_index=0):
    # Clear the window to prepare for the post display screen
    for widget in root.winfo_children():
        widget.destroy()

    post_id = post.get_post_id()

    # Increase view count each time the post is shown
    cursor.execute("UPDATE Analytics SET views = views + 1 WHERE post_id = ?", (post_id,))
    conn.commit()

    # Fetch the latest analytics data (likes, views, and comments)
    cursor.execute("SELECT likes, views, comments FROM Analytics WHERE post_id = ?", (post_id,))
    row = cursor.fetchone()
    likes, views, comments = row if row else (0, 0, "")
    analytics = Analytics(post_id=post_id, likes=likes, views=views, comments=comments)

    # Display the post description as the main title
    ttk.Label(root, text=f"File: {post.get_content()}", font=("Helvetica", 14)).pack(pady=10)

    # Load all files attached to this post and prepare to navigate them
    attached_files = get_attached_files(post_id)
    file_index = [0]  # Use a list to make this index mutable in nested functions

    # Container to display files
    file_display_frame = ttk.Frame(root)
    file_display_frame.pack(pady=10)

    # Shows which file out of total is being displayed
    file_counter_label = ttk.Label(root)
    file_counter_label.pack()

    # Display the currently selected attached file (image or non-image)
    def display_file():
        for widget in file_display_frame.winfo_children():
            widget.destroy()

        if not attached_files:
            ttk.Label(file_display_frame, text="No attached files").pack()
            return

        name, content = attached_files[file_index[0]]
        file_counter_label.config(text=f"File {file_index[0] + 1} of {len(attached_files)}")

        ttk.Label(file_display_frame, text=f"Attached File: {name}").pack()

        # Show image thumbnails
        if name.lower().endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(io.BytesIO(content))
                image.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(image)
                img_label = ttk.Label(file_display_frame, image=photo)
                img_label.image = photo
                img_label.pack()
            except:
                ttk.Label(file_display_frame, text="❌ Couldn't preview that image").pack()
        else:
            # Non-image: offer to open file using system viewer
            def open_file(data=content, fname=name):
                temp_path = os.path.join(temp_dir, f"temp_{fname}")
                with open(temp_path, "wb") as f:
                    f.write(data)
                os.startfile(temp_path)

            ttk.Button(file_display_frame, text=f"Open {name}", command=open_file).pack(pady=2)

    # Navigate to the next file
    def next_file():
        if attached_files:
            file_index[0] = (file_index[0] + 1) % len(attached_files)
            display_file()

    # Navigate to the previous file
    def prev_file():
        if attached_files:
            file_index[0] = (file_index[0] - 1) % len(attached_files)
            display_file()

    # Show next/previous file buttons if there are multiple files
    if len(attached_files) > 1:
        file_nav = ttk.Frame(root)
        file_nav.pack()
        ttk.Button(file_nav, text="⬅️", command=prev_file).pack(side="left", padx=10)
        ttk.Button(file_nav, text="➡️", command=next_file).pack(side="right", padx=10)

    # Show the first file
    display_file()

    # Option to delete the post
    delete_var = tk.BooleanVar()
    delete_checkbox = ttk.Checkbutton(root, text="🗑️ Delete Post", variable=delete_var)
    delete_checkbox.pack(anchor="ne", padx=10)

    # Like the post and update analytics
    def like_post():
        cursor.execute("UPDATE Analytics SET likes = likes + 1 WHERE post_id = ?", (post_id,))
        conn.commit()
        cursor.execute("SELECT likes FROM Analytics WHERE post_id = ?", (post_id,))
        new_likes = cursor.fetchone()[0]
        like_label.config(text=f"Likes: {new_likes}")
        like_button.config(state="disabled", text="❤️ Liked")

    # Show current likes and views
    like_label = ttk.Label(root, text=f"Likes: {analytics.get_likes()}")
    like_label.pack(side="left", padx=10)

    like_button = ttk.Button(root, text="❤️ Like This", command=like_post)
    like_button.pack()

    view_label = ttk.Label(root, text=f"Views: {analytics.get_views()}")
    view_label.pack(side="right", padx=10)

    # Display the post ID and user ID
    ttk.Label(root, text=f"Post ID: {post_id} | User ID: {post.get_user_id()}").pack()

    # Show the post description (read-only)
    ttk.Label(root, text="Description:").pack()
    desc_box = tk.Text(root, height=4, width=40)
    desc_box.insert(tk.END, post.get_content())
    desc_box.configure(state="disabled")
    desc_box.pack()

    # Display all comments from the database
    cursor.execute("SELECT comments FROM Posts WHERE post_id = ?", (post_id,))
    comment_text = cursor.fetchone()[0] or ""
    ttk.Label(root, text="Comments:").pack()
    comment_display = tk.Text(root, height=4, width=50)
    comment_display.insert(tk.END, comment_text)
    comment_display.configure(state='disabled')
    comment_display.pack()

    # Allow the user to add a new comment
    ttk.Label(root, text="Add a Comment:").pack()
    comment_entry = tk.Entry(root, width=50)
    comment_entry.pack()

    def save_comment():
        new_comment = comment_entry.get().strip()
        if new_comment:
            updated = comment_text + "\n" + new_comment if comment_text else new_comment
            cursor.execute("UPDATE Posts SET comments = ? WHERE post_id = ?", (updated, post_id))
            conn.commit()
            comment_display.configure(state='normal')
            comment_display.insert(tk.END, f"\n{new_comment}")
            comment_display.configure(state='disabled')
            comment_entry.delete(0, tk.END)

    ttk.Button(root, text="💬 Submit Comment", command=save_comment).pack(pady=5)

    # Button to return to post creation or delete the post
    def handle_back():
        if delete_var.get():
            cursor.execute("DELETE FROM Analytics WHERE post_id = ?", (post_id,))
            cursor.execute("DELETE FROM Posts WHERE post_id = ?", (post_id,))
            conn.commit()
            messagebox.showinfo("Deleted", f"Post {post_id} and its files were smoked.")
        reset_to_main()

    ttk.Button(root, text="⏪ Back to Post Creation", command=handle_back).pack(pady=10)

    # Navigation buttons to jump between posts in the database
    if post_list:
        nav_frame = ttk.Frame(root)
        nav_frame.pack(pady=10)

        def go_first():
            first_id = post_list[0]
            cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (first_id,))
            row = cursor.fetchone()
            if row:
                new_post = Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
                show_post_screen(new_post, post_list, 0)

        def go_last():
            last_index = len(post_list) - 1
            last_id = post_list[last_index]
            cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (last_id,))
            row = cursor.fetchone()
            if row:
                new_post = Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
                show_post_screen(new_post, post_list, last_index)

        def prev_post():
            if current_index > 0:
                new_id = post_list[current_index - 1]
                cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (new_id,))
                row = cursor.fetchone()
                if row:
                    new_post = Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
                    show_post_screen(new_post, post_list, current_index - 1)

        def next_post():
            if current_index < len(post_list) - 1:
                new_id = post_list[current_index + 1]
                cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (new_id,))
                row = cursor.fetchone()
                if row:
                    new_post = Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
                    show_post_screen(new_post, post_list, current_index + 1)

        ttk.Button(nav_frame, text="⏮️ First", command=go_first).pack(side="left", padx=5)
        ttk.Button(nav_frame, text="⬅️ Previous", command=prev_post).pack(side="left", padx=5)
        ttk.Button(nav_frame, text="Next ➡️", command=next_post).pack(side="left", padx=5)
        ttk.Button(nav_frame, text="⏭️ Last", command=go_last).pack(side="left", padx=5)
    
    


# This function handles submitting a new post.
# It collects the description and any attached files,
# inserts the post and files into the database,
# initializes the analytics (views and likes),
# and then shows the newly created post screen.
def submit_post():
    global attached_files

    # Get the description from the entry field
    desc = desc_entry.get()

    # Simulate a user ID for this example (can be expanded later)
    user_id = 1

    # Capture the current date and time for the post
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Prepare placeholders in case fewer than 3 files are attached
        file_data = [("none.txt", None)] * 3

        # Load file content from the attached file paths
        for i in range(min(len(attached_files), 3)):
            path = attached_files[i]
            with open(path, "rb") as f:
                file_data[i] = (os.path.basename(path), f.read())

        # Insert the post into the Posts table with up to 3 files
        cursor.execute("""
            INSERT INTO Posts (
                user_id, file_type, content, post_DateTime,
                file_name_1, file_content_1,
                file_name_2, file_content_2,
                file_name_3, file_content_3
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, file_type.get(), desc, date_time,
            file_data[0][0], file_data[0][1],
            file_data[1][0], file_data[1][1],
            file_data[2][0], file_data[2][1]
        ))
        conn.commit()

        # Get the post ID of the newly inserted post
        post_id = cursor.lastrowid

        # Initialize analytics for the new post (0 views, 0 likes)
        cursor.execute("""
            INSERT INTO Analytics (post_id, views, likes)
            VALUES (?, ?, ?)
        """, (post_id, 0, 0))
        conn.commit()

        # Retrieve all post IDs for navigation
        cursor.execute("SELECT post_id FROM Posts ORDER BY post_id ASC")
        post_ids = [row[0] for row in cursor.fetchall()]
        current_index = post_ids.index(post_id)

        # Create a Post object and display it on screen
        post = Post(post_id=post_id, user_id=user_id, date_time=date_time, content=desc)
        show_post_screen(post, post_ids, current_index)

    except Exception as e:
        # Show an error message if something goes wrong with the database
        messagebox.showerror("Database Error", str(e))


# This function builds the main UI where users can create a new post.
# It includes fields for description, file attachments, file type selection,
# and buttons to submit the post or view previous posts.
def create_main_ui():
    global desc_entry, file_type, attached_files

    # Clear out the current UI to reset the screen
    attached_files = []
    for widget in root.winfo_children():
        widget.destroy()

    # Used to display labels for each attached file
    file_labels = []

    # Function to attach files selected by the user
    def attach_files():
        nonlocal file_labels
        # Clear any previous file labels
        for label in file_labels:
            label.destroy()
        file_labels.clear()
        attached_files.clear()

        try:
            # Get number of files selected from the spinbox
            num_files = int(files_spinbox.get())
            if num_files > 3:
                messagebox.showerror("Limit", "Maximum 3 files allowed.")
                return
        except:
            messagebox.showerror("Error", "Invalid number of files.")
            return

        # Prompt user to choose files and store file paths
        for i in range(num_files):
            file_path = filedialog.askopenfilename()
            if file_path:
                attached_files.append(file_path)
                label = ttk.Label(root, text=f"Attached: {os.path.basename(file_path)}")
                label.pack()
                file_labels.append(label)

    # Label showing the  user ID
    user_id_label = ttk.Label(root, text="User ID (Auto): 1")
    user_id_label.pack(pady=5)

    # Spinbox to choose number of files to attach
    files_label = ttk.Label(root, text="Number of Files:")
    files_label.pack()
    files_spinbox = ttk.Spinbox(root, from_=1, to=3, width=5)
    files_spinbox.configure(foreground="black")
    files_spinbox.pack()

    # Dropdown menu to select the type of files (e.g. image, video, text)
    file_type_label = ttk.Label(root, text="File Type:")
    file_type_label.pack()
    file_type = ttk.Combobox(root, values=["Image", "Video", "Text"])
    file_type.configure(foreground="black")
    file_type.pack()

    # Input for the post's description
    desc_label = ttk.Label(root, text="Description:")
    desc_label.pack()
    desc_entry = ttk.Entry(root, width=50)
    desc_entry.configure(foreground="black")
    desc_entry.pack()

    # Button to attach files using the attach_files() function
    attach_btn = ttk.Button(root, text="📎 Attach File(s)", command=attach_files)
    attach_btn.pack(pady=5)

    # Button to submit the post using the submit_post() function
    submit_btn = ttk.Button(root, text="🚀 Submit Post", command=submit_post)
    submit_btn.pack(pady=10)

    # Button to view existing posts and navigate through them
    def open_analytics():
        # Make sure every post has analytics data
        cursor.execute("SELECT post_id FROM Posts")
        all_post_ids = [row[0] for row in cursor.fetchall()]

        for pid in all_post_ids:
            cursor.execute("SELECT post_id FROM Analytics WHERE post_id = ?", (pid,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Analytics (post_id, views, likes) VALUES (?, 0, 0)", (pid,))
                conn.commit()

        # Load posts and show the first one
        cursor.execute("SELECT post_id FROM Posts ORDER BY post_id ASC")
        post_ids = [row[0] for row in cursor.fetchall()]
    
        if not post_ids:
            messagebox.showinfo("No Posts", "You haven't dropped any posts yet.")
            return

        for index, post_id in enumerate(post_ids):
            cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (post_id,))
            row = cursor.fetchone()

            if row:
                post = Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
                show_post_screen(post, post_ids, index)
                return

        messagebox.showinfo("No Viewable Posts", "No posts found in the database.")

    # Add the analytics navigation button to the main screen
    analytics_btn = ttk.Button(root, text="📊 View Posts", command=open_analytics)
    analytics_btn.pack(pady=10)


# Launch UI
create_main_ui()
root.mainloop()
