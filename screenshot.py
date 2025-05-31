import json
import re
import config
import time
from pathlib import Path
from typing import Dict, Final
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright


#from utils.imagenarator import imagemaker  


def get_screenshots_of_reddit_posts(reddit_thread, reddit_comments, theme="dark"):

    # settings values
    W = 1080
    H = 1920

    reddit_id = re.sub(r"[^\w\s-]", "", str(reddit_thread['ID']))
    # ! Make sure the reddit screenshots folder exists
    Path(f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)
    Path(f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/mp3").mkdir(parents=True, exist_ok=True)
    Path(f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/mp3_clean").mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        print("Launching Headless Browser...")

        #browser = p.chromium.launch(headless=False) #to check for chrome view
        browser = p.chromium.launch(headless=False)  # headless=False #to check for chrome view
        context = browser.new_context()
        my_config = config.load_config()
        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # So we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        dsf = (W // 600) + 1

        context = browser.new_context(
            locale="en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf,
        )
        # set the theme and disable non-essential cookies
        if theme == "dark":
            cookie_file = open(
                "./Python/Reddit Scraper/data/cookie-dark-mode.json", encoding="utf-8"
            )
            bgcolor = (33, 33, 36, 255)
            txtcolor = (240, 240, 240)


        cookies = json.load(cookie_file)
        cookie_file.close()

        context.add_cookies(cookies)  # load preference cookies

        # Get the thread screenshot
        page = context.new_page()
        # go to reddit's login page
        page.goto("https://www.reddit.com/login/?experiment_d2x_2020ify_buttons=enabled&use_accountmanager=true&experiment_d2x_google_sso_gis_parity=enabled&experiment_d2x_onboarding=enabled&experiment_d2x_am_modal_design_update=enabled&rdt=58447")
        # fill user info
        time.sleep(5)
        #page.wait_for_selector('input', timeout=20000) #Wait until the login appears??????????????
        #print(page.url)
        page.locator("id=loginUsername").fill(my_config["RedditCredential"]["username"])
        page.locator("id=loginPassword").fill(my_config["RedditCredential"]["passkey"])
        page.get_by_role("button", name="Log In").click()
        #time.sleep(5)
        # go to the thread
        postURL = reddit_thread['Post URL']
        #print(postURL)
        page.goto(str(postURL[0]), timeout=300000)
        '''time.sleep(5)
        page.keyboard.press("Escape")
        
        page.goto(str(postURL[0]), timeout=300000)'''
        
        time.sleep(5)
        '''page.keyboard.press("Escape")
        
        page.goto(str(postURL[0]), timeout=3000)
'''
        page.set_viewport_size(ViewportSize(width=W, height=H))
        Title = reddit_thread['Title']

        content_path = f"./Python/Reddit Scraper/Assets/temp/{reddit_id}"
        postcontentpath = f"{content_path}/png/title.png" #<------------------------------------CHANGE FILE LOCATION
        page.locator(f"shreddit-post").screenshot(path=postcontentpath)
        print("Screenshot for OP completed")

        comment = reddit_comments
        #comment = comment[0]
        print(comment)
        i = 1
        list = []
        for comment_text in comment: #<---- idx is returned as a list?
            

            if page.locator('[data-testid="content-gate"]').is_visible():
                page.locator('[data-testid="content-gate"] button').click()

            #page.goto(f'https://reddit.com{comment.permalink}', timeout=0)

            comment_txt = comment_text[:100]
            #comment_txt = re.escape(comment_txt).replace(r'\ ', r'\s*')
            try:
                if "'" in comment_txt and '"' in comment_txt:
    # If both types are present, escape the single quotes
                    locator = page.locator(f"shreddit-comment:has-text('{comment_txt.replace('\'', '\\\'')}')").screenshot(
                    path=f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/png/{i}.png"
                    
                )
                elif "'" in comment_txt:
                    # If only single quotes are present, use double quotes for the selector
                    locator = page.locator(f"shreddit-comment:has-text(\"{comment_txt}\")").screenshot(
                    path=f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/png/{i}.png"
                )
                elif '"' in comment_txt:
                    # If only single quotes are present, use double quotes for the selector
                    locator = page.locator(f"shreddit-comment:has-text(\'{comment_txt}\')").screenshot(
                    path=f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/png/{i}.png"
                )
                else:
                    # If no single quotes, use single quotes for the selector
                    locator = page.locator(f"shreddit-comment:has-text('{comment_txt}')").screenshot(
                    path=f"./Python/Reddit Scraper/Assets/temp/{reddit_id}/png/{i}.png"
                )


                print(f"Screenshot for comment {i} out of {len(comment)}")
                list.append(comment_text)
                i += 1




            except TimeoutError:
                print("TimeoutError: Skipping screenshot...")
                continue
            except Exception:
                print("String Error, Skipping Screenshot")
                continue

        # close browser instance when we are done using it
        browser.close()

    print("Screenshots downloaded Successfully.")
    return list, content_path
