import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

def countcaps(x):
    c = 0
    for i in x:
        if i.isupper():
            c+=1
        if i.isdigit():
            c+=1
    if c>=2 and len(x)>=4:
        return True
    return False

def extractname(ls):
    k = ls[0].split(' ')
    hotelname = ""
    temp = " "
    for i in k:
        if countcaps(i): 
            temp = i
            break
        else:
            hotelname+=i
            hotelname+=" "
    c = 0
    for i in temp :
        if i.isupper():
            c+=1
        if i.isdigit():
            c+=1
        if c==2:
            break
        hotelname+=i
    return hotelname
            
def extractaddress(ls):
    k = ls[0].split(' ')
    address = ""
    flag = False
    temp = " "
    for i in k:
        if flag:
            address+=i
            address+=" "
        if countcaps(i) and not flag:
            temp = i
            flag = True
    c = 0
    t = ""
    for i in temp:
        if i.isupper():
            c+=1
        if i.isdigit():
            c+=1
        if c==2:
            t+=i
    full = t+" "+address
    finaladdr = ""
    for i in full:
        if i !="₹":
            finaladdr+=i
        else:
            break
    return finaladdr

base_url = "https://www.dineout.co.in/chennai-restaurants/welcome-back?p="
total_pages = 1
data = []

for page_num in range(1, total_pages + 1):
    url = f"{base_url}{page_num}"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Success! Scraping data from page {page_num}")

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the specific HTML tags that contain the restaurant info
        restaurants = soup.find_all('div', class_='restnt-main-wrap clearfix')

        for restaurant in restaurants:
            # Extract the restaurant's name
            name = restaurant.find('div', class_='restnt-detail-wrap').text 

            # Iterate over possible rating classes (1 to 5)
            for rating_class in ['rating-1', 'rating-2', 'rating-3', 'rating-4', 'rating-5','rating-0']:
                rating_div = restaurant.find('div', class_=f'restnt-rating {rating_class}')
                if rating_div:
                    # If the rating div is found, extract its text
                    rating = rating_div.text.strip()
                    break  # Break the loop once the rating is found
                else:
                    # If the rating div is not found, set rating to 'Not available'
                    rating = 'Not available'

            # Print the name and rating
            name = name[12:]
            data.append([name, rating])

    else:
        print(f"Error: {response.status_code} for page {page_num}")

hotellist = []
addresslist = []
ratings = []

for i in data:
    addresslist.append(extractaddress(i))
    hotellist.append(extractname(i))


for i in data:
    k = i[1]
    if k != 'Not available':
        ratings.append(float(k))
    else:
        ratings.append("NR")

rupees_list = []
rflag = False
for text in data:
    m = ""
    rflag = False
    for i in text[0]:
        if rflag:
            if i.isdigit() or i=="," or i==" ":
                m+=i
            else:
                break
        if i=="₹":
            rflag = True
    rupees_list.append(m)
rupees = []
for i in rupees_list:
    k = ""
    if ','in i:
        for j in i:
            if j!=',' and j!=" ":
                k+=j
        rupees.append(k)
    else:
        rupees.append(i[1:4])


df = pd.DataFrame({
    'Hotel Name': hotellist,
    'Address': addresslist,
    'Rating (5)': ratings,
    'Price (2)': rupees
}, index=range(1, len(hotellist) + 1))

output_directory = r"C:\Users\SAM\output.xlsx"

output_path = os.path.join(output_directory, 'output.xlsx')
with pd.ExcelWriter(output_path) as writer:
    df.to_excel(writer, index=True)

print("Excel file saved successfully:", output_path)

# Save the DataFrame to an Excel file
df.to_excel('output.xlsx', index=True)
print(df)