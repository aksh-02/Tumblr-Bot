import pytumblr
import praw
import os
import urllib.request
import time
import sys
from random import shuffle


def write_log(res):
	try:
		with open(os.path.join(os.getcwd(), 'postid.txt'), 'a+') as fw:
			fw.write(str(res)+'\n')
	except Exception as e:
		print(f"In writing id {res} : ", e)


def read_prev_posts():
	try:
		with open(os.path.join(os.getcwd(), 'postid.txt')) as fr:
			prev_posts = fr.readlines()
		return prev_posts
	except Exception as e:
		print('In reading Previous Posts : ', e)
		return []


def post_photo(cap, tag, link):
	tag = tag + my_tags[:ntags]
	try:
		client.create_photo(blogName, caption=cap, tags=tag, state="published", source=link)
		print(f"Posted image :", cap)
	except Exception as e:
		print("Posting image : ", e)


def post_text(title, tag, content):
	tag = tag + my_tags[:ntags]
	try:
		client.create_text(blogName, state="published", tags=tag, title=title, body=content)
		print(f"Posted text :", title)
	except Exception as e:
		print("Posting text : ", e)


def post_video(cap, tag, fname):
	tag = tag + my_tags[:ntags]
	try:
		client.create_video(blogName, state="published", tags=tag, caption=cap, data=fname)
		print(f"Posted video :", cap)
	except Exception as e:
		print("Posting video : ", e)


def get_posts(rsubs, plim=10, lim=30):
	try:
		posts = reddit.subreddit(rsubs).hot(limit=lim)
	except Exception as e:
		print("Fetching posts : ", e)
		return

	ptext = 0
	ppics = 0
	pvids = 0

	for post in posts:
		if ptext+ppics+pvids >= plim:  # To make sure we don't cross the API limit
			break

		try:
			pid = post.id
			if pid+'\n' in prev_posts:
				print(f"Post {pid} already scraped.")
				continue

			write_log(pid)
		except Exception as e:
			print("Writing and checking log : ", e)
		
		try:
			title = post.title
			url = post.url
			sub = [str(post.subreddit)]
		except Exception as e:
			print("Title or Url : ", e)

		if post.is_self:  # Text post
			try:
				content = post.selftext
				print(f"Posting text {pid}", title)
				post_text(title, sub, content)
				ptext += 1
			except Exception as e:
				print("In text post : ", e)
		elif not post.media and post.url.split('.')[-1] in ["jpg", "png"]:  # Image post
			try:
				print(f"Posting image {pid}", title)
				post_photo(title, sub, url)
				ppics += 1
			except Exception as e:
				print("In image post : ", e)
		else:   # Video post
			try:
				reddit_vid = True
				med = post.media
				fallback_url = med["reddit_video"]["fallback_url"]
				length = med["reddit_video"]["duration"]
				if float(length) >= 20:
					print(f"Video {pid} is long.")
					continue
				urllib.request.urlretrieve(fallback_url, f"{pid}.mp4")
				print(f"Posting video {pid}", title)
				post_video(title, sub, str(pid)+".mp4")
				pvids += 1
			except Exception as e:
				reddit_vid = False
				print("In video post : ", e)
				#print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
			
			if not reddit_vid:
				try:
					embedded_link = med["oembed"]["html"].split('src="')[1].split('"')[0]
					print(f"The embedded link : {embedded_link}")
				except:
					pass

		time.sleep(5)

	print(f"Number of text posts : {ptext}")
	print(f"Number of image posts : {ppics}")
	print(f"Number of video posts : {pvids}")



# Main

# Tumblr Creds
cons_key = ""
cons_secret = ""
oauth_token = ""
oauth_secret = ""

client = pytumblr.TumblrRestClient(
    cons_key,
    cons_secret,
    oauth_token,
    oauth_secret,
)

# Reddit Creds
cid = ""
csecret = ""
uagent = ""

reddit = praw.Reddit(client_id=cid, client_secret=csecret, user_agent=uagent)

blogName = ""  # Put your blogname here
subs = []
shuffle(subs)
my_tags = [] # Add your tags here
ntags = 2 # Number of tags you want to add to each post
rsubs = '+'.join(subs)

prev_posts = read_prev_posts()
print(f"{len(prev_posts)} previous posts found in log.")

get_posts(rsubs, 1) # The second argument can be number of posts you'd want to do each time, taking into account the api limit


