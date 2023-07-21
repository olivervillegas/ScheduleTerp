import aiohttp
import asyncio
import json

GEN_ED_CATEGORIES = ['FSAW', 'FSAR', 'FSMA', 'FSOC', 'DSHS', 'DSHU', 'DSNS', 'DSNL', 'DSSP', 'DVCC', 'DVUP', 'SCIS']

async def fetch_data(url):
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(url) as response:
                return await response.json()
        except aiohttp.client_exceptions.ContentTypeError as e:
            print(f"Failed to fetch data from {url}: {e}")
            return []  # Return an empty list to indicate no data

async def get_courses_data(page):
    url = f'https://api.umd.io/v1/courses?per_page=100&page={page}'
    return await fetch_data(url)

async def get_gen_ed_data():
    tasks = [get_courses_data(page) for page in range(1, 50)]  # Adjust the range as needed

    courses_data = await asyncio.gather(*tasks)

    all_courses = []
    for courses_page in courses_data:
        all_courses.extend(courses_page)

    gen_ed_mapping = {gen_ed: [] for gen_ed in GEN_ED_CATEGORIES}

    for course in all_courses:
        gen_ed_codes = course.get('gen_ed', [])
        course_id = course.get('course_id')

        for gen_ed_code_list in gen_ed_codes:
            for gen_ed_code in gen_ed_code_list:
                if gen_ed_code in gen_ed_mapping:
                    gen_ed_mapping[gen_ed_code].append(course_id)

    # Save data to a JSON file
    with open('gen_ed_data_dump.json', 'w') as file:
        json.dump(gen_ed_mapping, file, indent=4)

    print("Gen-ed data dump created successfully!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_gen_ed_data())
