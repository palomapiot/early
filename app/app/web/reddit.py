"""
    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
	This file is part of early.
    early is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    early is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with early.  If not, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime, timezone
import praw
from django.conf import settings
from praw.models import MoreComments


def _reddit():
    return praw.Reddit(client_id="settings.REDDIT_CLIENT_ID",
                     client_secret="settings.REDDIT_SECRET",
                     user_agent="tfm-profiling by palomapiot")

def get_submissions(subreddit_name, nsubmissions):
    print('getting submissions')
    submissions = []
    for submission in _reddit().subreddit(subreddit_name).new(limit=int(nsubmissions)):
        submissions.append(submission.id)
    return submissions

def get_users(submissions, nusers):
    print('getting users')
    users = []
    for submission_id in submissions:
        submission = _reddit().submission(id=submission_id)
        submission.comment_sort = "new"
        submission.comments.replace_more(limit=None)
        comment_queue = submission.comments[:]  # seed with top-level
        while comment_queue and len(list(dict.fromkeys(users))) < int(nusers):
            comment = comment_queue.pop(0)
            if comment.author is not None:
                users.append(str(comment.author))
            comment_queue.extend(comment.replies)
    users = list(dict.fromkeys(users))
    return users


def get_user_comments(user_name, ncomments):
    print('processing user...' + str(user_name))
    comments = []
    user = _reddit().redditor(user_name)
    # User comments
    if user is not None:
        user_comments = user.comments.new(limit=int(ncomments))
        for comment in user_comments:
            comment_date = datetime.fromtimestamp(comment.created_utc)
            c = {"text": str(comment.body), "date": str(comment_date)}
            comments.append(c)
    comments.reverse() # now we will process the older comments before the new ones
    return  comments
