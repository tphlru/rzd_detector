import aiohttp
async def count_statistical(subj_rating, out_town, gender, age):
    score = 0
    if gender == "Мужской":
        score -= 1
    if age