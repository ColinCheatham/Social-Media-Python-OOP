# This module contains the class definitions for the social media analytics application.
# Defines two classes: Post and Analytics 
# data retrieved from the database.

class Post:

    def __init__(self, post_id=0, user_id=0, date_time="", content=""):
        #initialize
        self.__post_id = post_id
        self.__user_id = user_id
        self.__date_time = date_time
        self.__content = content


# Get methods
    def get_post_id(self):
        #Return the post's ID.
        return self.__post_id
    
    def get_user_id(self):
        #Return the post's auuser_idthor
        return self.__user_id

    def get_date_time(self):
        #Return the post's creation date
        return self.__date_time

    def get_content(self):
        #Return the post's content
        return self.__content
    

# Set methods
    def set_post_id(self, post_id):
        #set post ID
        self.__post_id = post_id
    
    def set_user_id(self, user_id):
        #Set the user's ID
        self.__user_id = user_id
    
    def set_date_time(self, date_time):
        #Set the post's date and time
        self.__date_time = date_time
    
    def set_content(self, content):
        #Set the post's content
        self.__content = content
    

#string representation of Post
    def __str__(self):
        return f"Post(ID: {self.__post_id}, User ID: {self.__user_id}, Date: {self.__date_time})"



class Analytics:
    def __init__(self, post_id=0, likes=0, views=0, comments=""):
        self.__post_id = post_id
        self.__likes = likes
        self.__views = views
        self.__comments = comments

    def get_post_id(self):
        return self.__post_id

    def get_likes(self):
        return self.__likes

    def get_views(self):
        return self.__views

    def get_comments(self):
        return self.__comments

    def set_post_id(self, post_id):
        self.__post_id = post_id

    def set_likes(self, likes):
        self.__likes = likes

    def set_views(self, views):
        self.__views = views

    def set_comments(self, comments):
        self.__comments = comments

    def __str__(self):
        return f"Analytics(Post ID: {self.__post_id}, Likes: {self.__likes}, Views: {self.__views}, Comments: {self.__comments})"
