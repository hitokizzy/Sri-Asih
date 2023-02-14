from pyrogram import filters

from Srikandi import app, arq
from Srikandi.core.decorators.errors import capture_err
from Srikandi.utils.dbfunctions import get_nsfw_status

__MODULE__ = "Reddit"
__HELP__ = "/reddit [query] - results something from reddit"


@app.on_message(filters.command("reddit"))
@capture_err
async def reddit(_, message):
    if len(message.command) != 2:
        return await message.reply_text("/reddit needs an argument")
    subreddit = message.text.split(None, 1)[1]
    m = await message.reply_text("Searching")
    reddit = await arq.reddit(subreddit)
    if not reddit.ok:
        return await m.edit(reddit.result)
    reddit = reddit.result
    nsfw = reddit.nsfw
    sreddit = reddit.subreddit
    title = reddit.title
    image = reddit.url
    link = reddit.postLink
    if nsfw:
        if await get_nsfw_status(message.chat.id) == False:
            return await m.edit(
                "NSFW content is disabled in this chat! Enable it using /nsfw"
            )
    caption = f"""
**Title:** `{title}`
**Subreddit:** {sreddit}
**PostLink:** {link}"""
    try:
        await message.reply_photo(photo=image, caption=caption)
        await m.delete()
    except Exception as e:
        await m.edit(e.MESSAGE)
