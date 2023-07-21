import requests
import json

GEN_ED_CATEGORIES = ['FSAW', 'FSAR', 'FSMA', 'FSOC', 'DSHS', 'DSHU', 'DSNS', 'DSNL', 'DSSP', 'DVCC', 'DVUP', 'SCIS', 'DSNL_labs']

def get_gen_ed_data():
    # Save data to a JSON file
    gen_ed_mapping = {gen_ed: [] for gen_ed in GEN_ED_CATEGORIES}
    
    for i in range(1, 51):
        url = 'https://api.umd.io/v1/courses?per_page=100&page=' + str(i)
        response = requests.get(url)
        if response.status_code == 200:
            courses_data = response.json()

            for course in courses_data:
                gen_ed_codes : list[list[str]] = course.get('gen_ed', [])
                course_id = course.get('course_id')
                #                       [["DSNL|AOSC201"], ["DSNS","SCIS"]]
                for gen_ed_code_list in gen_ed_codes:
                    #                  ["DSNS", "SCIS"]
                    for gen_ed_code in gen_ed_code_list:
                        # "DSNS"
                        if "|" in gen_ed_code:
                            gen_ed_code, lab = gen_ed_code.split("|")
                            if gen_ed_code in gen_ed_mapping:
                                gen_ed_mapping[gen_ed_code].append(course_id)
                                gen_ed_mapping['DSNL_labs'].append(course_id + "|" + lab)
                        else:
                            if gen_ed_code in gen_ed_mapping:
                                gen_ed_mapping[gen_ed_code].append(course_id)

            print("Gen-ed data dump created successfully!", i)
        else:
            print("Failed to retrieve data from the UMD IO API.")
     # Save data to a JSON file
    with open('gen_ed_data_dump.json', 'w') as file:
        json.dump(gen_ed_mapping, file, indent=4)



# def get_gen_ed_data():
#     url = 'https://api.umd.io/v1/courses?per_page=100'
#     response = requests.get(url)
#     if response.status_code == 200:
#         courses_data = response.json()

#         gen_ed_mapping = {}
#         for course in courses_data:
#             gen_ed_codes = course.get('gen_ed', [])
#             course_id = course.get('course_id')
            
#             for gen_ed_code_list in gen_ed_codes:
#                 for gen_ed_code in gen_ed_code_list:
#                     if gen_ed_code not in gen_ed_mapping:
#                         gen_ed_mapping[gen_ed_code] = []
#                     gen_ed_mapping[gen_ed_code].append(course_id)

#         # Save data to a JSON file
#         with open('gen_ed_data_dump.json', 'w') as file:
#             json.dump(gen_ed_mapping, file, indent=4)

#         print("Gen-ed data dump created successfully!")
#     else:
#         print("Failed to retrieve data from the UMD IO API.")


if __name__ == "__main__":
    get_gen_ed_data()
