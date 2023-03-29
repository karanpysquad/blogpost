# blogpost

This is Blogpost project where user can create account abd then post thier blogs on thier feed and also can comment and like on posts.

## Functions/Features

* User signup
* Login with JWT authentication
* Update profile
* Password reset
* Post blog, comments, likes
* Delete and update comments and posts
* Search by name


# Model

* There is Django's default User which is provide in-built fields like username, password and custom model UserProfile


# Operations

* signup/login : post
* profile : post, put, patch, delete, retrieve

#  Open Terminal and Execute Following Commands :

```
pip install -r requirements.txt
pyhon manage.py makemigrations
python manage.py migrate
python manage.py runserver
```


