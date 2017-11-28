import requests
import csv
import re
import time
import os
from bs4 import BeautifulSoup as bs
from random import randint

results_path = "scripts_output/mastersportal"
main_url = "http://www.mastersportal.eu/countries/"

# Create results folder if it does not exist
if not os.path.exists(results_path):
    os.makedirs(results_path)

# helpers
def get_no_from_str(x):
    result = "N/A"
    s = re.search(r"[0-9]{1,5}([,.][0-9]{1,2})?", x)
    if s:
        result = s.group()
    return result

# get main url data
countries_res = requests.get(main_url)
countries_page = bs(countries_res.text, "lxml")

# Write csv output header
programs_headers = ["country_url", "country_name", "country_id", "university_url",
                    "university_name", "university_id", "university_country", "study_url",
                    "study_name", "program_name", "program_type", "study_id", "name", "deadline",
                    "tuition_amount", "tuition_currency", "tuition_price_specification", "duration",
                    "language", "university", "university_rank", "city", "country", "structure", "start_date",
                    "application_deadline", "facts", "ielts_score", "cae_score", "toefl_score",
                    "tuition_fees_containers", "academic_req"]
programs_file = open("{}/programs{}.csv".format(results_path, round(time.time())), "a")
programs_csv = csv.DictWriter(programs_file, fieldnames=programs_headers)
programs_csv.writeheader()

counter = 1

for c in countries_page.select("#CountryOverview li a")[-3:]:

    country_url = c['href']
    country_name = c['title']
    country_id = re.search("/\d+/", country_url).group()[1:-1]

    print("+", country_name, "(" + country_id + ")")

    universities_res = requests.get(country_url)
    universities_page = bs(universities_res.text, "lxml")

    for u in universities_page.select("#CountryStudies li a"):

        university_url = u['href']
        university_name = u['title']
        university_id = re.search("/\d+/", university_url).group()[1:-1]
        university_country = country_id

        print("++", university_name, "(" + university_id + ")")

        studies_res = requests.get(university_url)
        studies_page = bs(studies_res.text, "lxml")

        for s in studies_page.select("#StudyListing .StudyInfo a"):

            study_url = s['href']
            study_name = s['title'].replace("/", "").replace(".", "")
            program_name = study_name.split(',')[:-1][0].strip()
            program_type = study_name.split(',')[-1].strip()
            study_id = re.search("/\d+/", study_url).group()[1:-1]
            study_university = university_id
            study_country = country_id

            print("+++", counter, study_name, "(" + study_id + ")")
            counter += 1

            details_res = requests.get(study_url)

            page_text = details_res.text.strip()
            page = bs(page_text, "lxml")

            name_s = "section#StudyHeader h1[itemprop='name']"
            name = page.select(name_s)[0].text.strip() if page.select(name_s) else 'N/A'

            deadline_s = "li.QuickFact.js-deadlineFact time"
            deadline = page.select(deadline_s)[0].text.strip() if page.select(deadline_s) else 'N/A'

            tuition_amount_s = ".js-tuitionFact [data-target='international'] [itemprop='price'] span"
            tuition_amount = page.select(tuition_amount_s)[0]['data-amount']  if page.select(tuition_amount_s) else 'N/A'

            tuition_currency_s = ".js-tuitionFact [data-target='international'] [itemprop='price'] span"
            tuition_currency = page.select(tuition_currency_s)[0]['data-currency'] if page.select(tuition_currency_s) else 'N/A'

            tuition_spec_s = "li.js-tuitionFact.QuickFact [itemprop='priceSpecification']"
            tuition_price_specification = page.select(tuition_spec_s)[0].text.strip() if page.select(tuition_spec_s) else 'N/A'

            duration_s = "li.js-durationFact.QuickFact span div"
            duration = page.select(duration_s)[0].text.strip() if page.select(duration_s) else 'N/A'

            language_s = "li.js-languageFact.QuickFact span.QFDetails div"
            language = page.select(language_s)[0].text.strip() if page.select(language_s) else 'N/A'

            university_s = ".OrganisationInformation span[itemprop='name']"
            university = page.select(university_s)[0].text.strip() if page.select(university_s) else 'N/A'

            university_rank_s = "#StudyOrganisationLocation .OrganisationRanking"
            university_rank_st = page.select(university_rank_s)[0].text.strip() if page.select(university_rank_s) else 'N/A'
            university_rank = get_no_from_str(university_rank_st)

            location_s = ".OrganisationCity"
            city = [x.text.strip() for x in page.select(location_s)[0::2]] if page.select(location_s) else 'N/A'

            country = [x.text.strip() for x in page.select(location_s)[1::2]] if page.select(location_s) else 'N/A'

            structure_s = "#StudyContents ul li"
            structure = [x.text.strip() for x in page.select(structure_s)] if page.select(structure_s) else 'N/A'

            start_date_s = "li.StartDateItem .js-deadlineFact"
            start_date = page.select(start_date_s)[0].text.strip() if page.select(start_date_s) else 'N/A'

            application_deadline_s = "li.ApplicationDeadlines time"
            application_deadline = page.select(application_deadline_s)[0].text.strip() if page.select(application_deadline_s) else 'N/A'

            facts_s = "li.FactItem"
            facts = [x.text.strip() for x in page.select(facts_s)] if page.select(facts_s) else 'N/A'

            ielts_score_s = "[data-segment-id='IELTS'] div.js-Score.Score"
            ielts_score_st = page.select(ielts_score_s)[0].text.strip() if page.select(ielts_score_s) else 'N/A'
            ielts_score = get_no_from_str(ielts_score_st)

            cae_score_s = "[data-segment-id='CAE'] .Score.js-Score"
            cae_score_st = page.select(cae_score_s)[0].text.strip() if page.select(cae_score_s) else 'N/A'
            cae_score = get_no_from_str(cae_score_st)

            toefl_score_s = "[data-segment-id='TOEFL IBT'] .Score.js-Score"
            toefl_score_st = page.select(toefl_score_s)[0].text.strip() if page.select(toefl_score_s) else 'N/A'
            toefl_score = get_no_from_str(toefl_score_st)

            fees_s = "ul.TuitionFees li.Item"
            tuition_fees_containers = [x.text.strip().replace(u'\xa0', u' ') for x in page.select(fees_s)] if page.select(fees_s) else 'N/A'

            academic_req_s = "#AcademicRequirements"
            academic_req = page.select(academic_req_s)[0] if page.select(academic_req_s) else 'N/A'

            new_row = {
                "country_url": country_url.replace(",", ""),
                "country_name": country_name.replace(",", ""),
                "country_id": country_id.replace(",", ""),
                "university_url": university_url.replace(",", ""),
                "university_name": university_name.replace(",", ""),
                "university_id": university_id.replace(",", ""),
                "university_country": university_country.replace(",", ""),
                "study_url": study_url.replace(",", ""),
                "study_name": study_name,
                "program_name": program_name,
                "program_type": program_type,
                "study_id": study_id.replace(",", ""),
                "name": name,
                "deadline": deadline,
                "tuition_amount": tuition_amount,
                "tuition_currency": tuition_currency,
                "tuition_price_specification": tuition_price_specification,
                "duration": duration,
                "language": language,
                "university": university,
                "university_rank": university_rank,
                "city": city,
                "country": country,
                "structure": structure,
                "start_date": start_date,
                "application_deadline": application_deadline,
                "facts": facts,
                "ielts_score": ielts_score,
                "cae_score": cae_score,
                "toefl_score": toefl_score,
                "tuition_fees_containers": tuition_fees_containers,
                "academic_req": academic_req
            }

            new_row = {k: str(v).encode("utf-8") for k, v in new_row.items()}
            programs_csv.writerow(new_row)

            time.sleep(randint(1,3))

programs_file.close()
