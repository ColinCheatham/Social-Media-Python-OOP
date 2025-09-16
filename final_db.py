# db.py - Handles all data interactions for the social media analytics app

import sqlite3
from final_objects import Post, Analytics

DB_PATH = "final.db"

def connect():
    """Connect to the database and return the connection and cursor."""
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()

# ================== POST FUNCTIONS ==================

def get_all_posts():
    """Retrieve all posts from the Posts table."""
    conn, cursor = connect()
    cursor.execute("SELECT * FROM Posts ORDER BY post_id ASC")
    rows = cursor.fetchall()
    conn.close()

    posts = []
    for row in rows:
        post = Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
        posts.append(post)
    return posts

def get_post_by_id(post_id):
    """Retrieve a single post by ID."""
    conn, cursor = connect()
    cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Post(post_id=row[0], user_id=row[1], date_time=row[4], content=row[3])
    return None

def insert_post(post, files):
    """
    Insert a new post and its files into the database.
    Args:
        post (Post): A Post object containing metadata.
        files (list): A list of (file_name, file_content) tuples, up to 3.
    Returns:
        int: The newly inserted post_id.
    """
    conn, cursor = connect()

    try:
        padded_files = files + [("none.txt", None)] * (3 - len(files))
        cursor.execute("""
            INSERT INTO Posts (
                user_id, file_type, content, post_DateTime,
                file_name_1, file_content_1,
                file_name_2, file_content_2,
                file_name_3, file_content_3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post.get_user_id(), "Image", post.get_content(), post.get_date_time(),
            padded_files[0][0], padded_files[0][1],
            padded_files[1][0], padded_files[1][1],
            padded_files[2][0], padded_files[2][1]
        ))
        post_id = cursor.lastrowid

        cursor.execute("INSERT INTO Analytics (post_id, views, likes) VALUES (?, 0, 0)", (post_id,))
        conn.commit()
        return post_id
    except Exception as e:
        print("Error inserting post:", e)
        conn.rollback()
        return None
    finally:
        conn.close()

def delete_post(post_id):
    """Delete a post and its associated analytics."""
    conn, cursor = connect()
    cursor.execute("DELETE FROM Analytics WHERE post_id = ?", (post_id,))
    cursor.execute("DELETE FROM Posts WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()

# ================== ANALYTICS FUNCTIONS ==================

def get_analytics_by_post_id(post_id):
    """Retrieve analytics by post_id."""
    conn, cursor = connect()
    cursor.execute("SELECT * FROM Analytics WHERE post_id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Analytics(post_id=row[0], likes=row[1], views=row[2], comments=row[3])
    return None

def increment_view(post_id):
    """Increment the view count for a post."""
    conn, cursor = connect()
    cursor.execute("UPDATE Analytics SET views = views + 1 WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()

def increment_like(post_id):
    """Increment the like count for a post."""
    conn, cursor = connect()
    cursor.execute("UPDATE Analytics SET likes = likes + 1 WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()

def ensure_analytics_for_all_posts():
    """Ensure that all posts have a corresponding analytics row."""
    conn, cursor = connect()
    cursor.execute("SELECT post_id FROM Posts")
    post_ids = [row[0] for row in cursor.fetchall()]

    for pid in post_ids:
        cursor.execute("SELECT 1 FROM Analytics WHERE post_id = ?", (pid,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Analytics (post_id, views, likes) VALUES (?, 0, 0)", (pid,))
    conn.commit()
    conn.close()

def get_attached_files(post_id):
    """Retrieve all attached file name/content pairs for a post."""
    conn, cursor = connect()
    cursor.execute("""
        SELECT file_name_1, file_content_1, 
               file_name_2, file_content_2, 
               file_name_3, file_content_3 
        FROM Posts WHERE post_id = ?
    """, (post_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return []

    files = []
    for i in range(0, 6, 2):
        name = row[i]
        content = row[i + 1]
        if name and content:
            files.append((name, content))
    return files
