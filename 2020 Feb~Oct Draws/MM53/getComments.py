import praw
from praw.models import MoreComments
import json
import hashlib


def init_reddit():
    with open('auth.json', 'r') as f:
        auth = json.load(f)

    return praw.Reddit(
        client_id=auth['client_id'],
        client_secret=auth['client_secret'],
        username=auth['username'],
        password=auth['password'],
        user_agent=auth['user_agent'])


def hash_sha256(file):
    buf_size = 65536  # lets read stuff in 64kb chunks!
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def fetch_thread_cids(thread=None, reddit=None):
    submission = reddit.submission(url=thread)
    submission.comment_sort = 'old'
    sublist = []

    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            sublist += top_level_comment.children
        else:
            sublist.append(str(top_level_comment.id))

    return sublist


def fetch_all_cids(reddit=None, meta=None):
    # Get each individual thread's comment IDs, then combine them into one list
    all_cid = []
    for thread in meta['threads']:
        thread_cids = fetch_thread_cids(thread=thread['link'], reddit=reddit)
        thread['length'] = len(thread_cids)
        all_cid += thread_cids

    print("Found {} comments".format(len(all_cid)))
    return all_cid


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    # Get comment IDs from all threads
    all_id = fetch_all_cids(reddit=init_reddit(), meta=meta)

    # Save IDs to file
    with open(file_name, "w") as f:
        f.write("\n".join(sorted(all_id)))

    print("Comments saved in {}".format(file_name))

    # Calculate and save file's hash
    meta['CID_SHA256'] = hash_sha256(file_name)
    print("Comment ID SHA-256 Hash: {}".format(meta['CID_SHA256']))

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("End..")
    return


if __name__ == "__main__":
    main()
