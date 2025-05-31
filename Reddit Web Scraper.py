import praw
from praw.models import MoreComments
import pandas as pd
import time
import TTS, screenshot
import asyncio
import config
from pathlib import Path
from pydub import AudioSegment
import videomaker as vd
import math, subprocess
import os, sys


my_config = config.load_config()

def login():
    try:
        reddit = praw.Reddit(client_id=my_config['RedditCredential']['client_id'],
                             client_secret=my_config['RedditCredential']['client_secret'],
                             user_agent=my_config['RedditCredential']['user_agent'])
        #print(f'Succesfully logged in: {reddit}')
        return reddit
    except Exception as e:
        return e


def get_posts(subreddit):
    posts = subreddit.top(time_filter="week")
    posts_dict = {"Title":[], "Post Text":[], 
                "ID": [], "Score": [], 
                "Total Comments": [], "Time": [], "Post URL": []}
    num_posts = 1
    old_posts = file.to_dict()
    ids = old_posts['ID'].values()

    for post in posts:
        if not post.id in ids and not 'sex' in post.title: #Why are there so many posts about that???
            posts_dict["Title"].append(post.title)
            posts_dict["Post Text"].append(post.selftext)
            posts_dict["ID"].append(post.id)
            posts_dict["Score"].append(post.score)
            posts_dict["Total Comments"].append(post.num_comments) 
            posts_dict["Time"].append(time.time())
            posts_dict["Post URL"].append(post.url)

            if len(posts_dict["Title"]) >= num_posts:
                break
            else: continue

    return posts_dict



def get_comments(thread, reddit):
    num_comments = my_config['Reddit']['topn_comments']
    #Throw a list of 5 comments in here, then match it to the ID in the dict
    comments = []
    for item in posts_dict["ID"]:
        ID = item
        #print(ID)
        for i in (reddit.submission(ID).comments): #It has to be something with this not updating
            #print(i)
            if len(comments) == num_comments:
                break
            if isinstance(i, MoreComments):
                continue
            if ('[removed]') in i.body:
                continue
            comments.append(i.body)
            #print(len(post_comment))
    
        #print(f"{len(post_comment)} comments are chosen")
    return comments

def add_pause(input_path, output_path, pause):
    input_mp3_file = input_path
    output_mp3_file = output_path

    original_file = AudioSegment.from_mp3(input_mp3_file)
    silenced_file = AudioSegment.silent(duration=pause)
    combined_file = original_file + silenced_file

    combined_file.export(output_mp3_file, format="mp3")



if __name__ == '__main__':
    file_location = ('Python\\Reddit Scraper\\data.csv')
    script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
    file = pd.read_csv(file_location)

    reddit = login()
    subreddit = reddit.subreddit("AskReddit")
    print(f"Display Name: {subreddit.display_name}")
    print(f"Title: {subreddit.title}")

    posts_dict = get_posts(subreddit)
    
    print(posts_dict)
    top_posts = pd.DataFrame(posts_dict) 
    comments = get_comments(top_posts, reddit)
    top_posts.to_csv(file_location, mode='a', header=False) #Will add to existing csv file

    #top_posts.
    #Saves it in a CSV file

    post = posts_dict
    Path(f".\\Python\\Reddit Scraper\\Assets\\temp").mkdir(parents=True, exist_ok=True)
    #Run TTS
     # Works, but does everything under the 'Title' section; need to change it to do just one at a time
    #asyncio.run(TTS.record(posts_dict['Title'], 'Post Title', posts_dict["ID"]))

    #Grab screenshots of the posts
    comments, path = screenshot.get_screenshots_of_reddit_posts(reddit_thread=post, reddit_comments=comments)

    
    ID = posts_dict['ID']
    thread_id_path = f"\\Assets\\temp\\{ID[0]}"


    #This will skip any comments that it couldn't screenshot
    x=0
    title = posts_dict['Title']
    tts_path = f'{script_directory}{thread_id_path}\\mp3'
    asyncio.run(TTS.record(title[0], 'title', tts_path)) #Record the Title, then the comments in TTS
    for i in comments:
        x += 1
        try:
            asyncio.run(TTS.record(i, str(x), tts_path))
        except Exception as e:
            print(f'error: {e}')


    #video editor <-------------
    

        # make sure the tts of the title and comments don't exceed the total duration
    total_video_duration = my_config['VideoSetup']['total_video_duration']
    pause = my_config['VideoSetup']['pause']
    current_video_duration = 0

    #tts_title_path = f'.\\{thread_id_path}\\mp3\\title.mp3'
    tts_title_path = f'{script_directory}{thread_id_path}\\mp3\\title.mp3'
    #print(f'TITLE PATH: {tts_title_path}')

    title_duration = TTS.get_length(path=tts_title_path)
    current_video_duration += title_duration + pause + pause

    list_of_number_of_comments = list(range(len(comments)))

    # make sure the tts of the title and comments don't exceed the total duration
    total_video_duration = my_config['VideoSetup']['total_video_duration'] # <-- Make sure that it is no longer than duration, but doesn't go over the total length by a large amount


    pause = my_config['VideoSetup']['pause']

    comments_audio_path = []
    comments_audio_clean_path = []
    comments_image_path = []
    for i in list_of_number_of_comments:
        comment_audio_path = f'{script_directory}{thread_id_path}\\mp3\\{i+1}.mp3'
        comment_audio_clean_path = f'{script_directory}{thread_id_path}\\mp3_clean\\{i+1}.mp3'
        comment_image_path = f'{script_directory}{thread_id_path}\\png\\{i+1}.png'
        comment_duration = TTS.get_length(comment_audio_path)
        #print(f'comment path: {comment_audio_path}, comment duration: {comment_duration}')

        if current_video_duration + comment_duration + pause <= total_video_duration:
            comments_audio_path.append(comment_audio_path)
            comments_audio_clean_path.append(comment_audio_clean_path)
            comments_image_path.append(comment_image_path)
            current_video_duration += comment_duration + pause

    #total_video_duration = current_video_duration + pause

    title_image_path = f'{script_directory}{thread_id_path}\\png\\title.png'

    # convert the pause(in seconds) into milliseconds

    script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 

    title_audio_path = f'{script_directory}{thread_id_path}\\mp3\\title.mp3'
    title_audio_clean_path = f'{script_directory}{thread_id_path}\\mp3_clean\\title.mp3'

    mp3_pause = pause * 1000
    add_pause(title_audio_path, title_audio_clean_path, mp3_pause)

    comments_combined = list(zip(comments_audio_path, comments_audio_clean_path))
    for input_path, output_path in comments_combined:
        add_pause(input_path, output_path, mp3_pause)




    

    

    ID = posts_dict['ID']

    # create final video
    Path("./Results").mkdir(parents=True, exist_ok=True)
    save_path = script_directory
    
    vd.make_final_video(title_audio_path=title_audio_clean_path,
                     comments_audio_path=comments_audio_clean_path,
                     title_image_path=title_image_path,
                     comments_image_path=comments_image_path,
                     length=math.ceil(current_video_duration),
                     reddit_id=ID,
                     save_path=save_path,
                     duration=current_video_duration,
                     )

    if my_config['App']['upload_to_youtube']:
        upload_file = f'./Results/{ID}.mp4'
        directory_path = my_config['Directory']['path']
        cmd = ['python', f'{directory_path}/Youtube/upload.py', '--file', upload_file, '--title',
               f'{posts_dict['Title']}', '--description', f'{posts_dict['Title']}']
        subprocess.run(cmd)






    #Upload X
    
