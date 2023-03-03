import os
import requests
import datetime
from datetime import datetime, timedelta
import requests as req
from bs4 import BeautifulSoup
import warnings

def get_filenames():
    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.getcwd()) for f in filenames]
    new_result = []
    for item in result:
        if ".txt" in item:
            new_result.append(item)
   # return ["chessopeningtheory\\1._d4\\1...d5\\2._Bf4\\index.html"]
    return new_result

def show_today_data(filename):
    data = get_today_data(filename)
    if data is None:
        print("No data for " + filename)
        return
    tot_items = data[0]
    today_cals = data[1]
    food_items = data[2]
    for item in food_items:
        print(item[0], "x" + str(item[1]),"-", str(item[2]), "cals")
    print("---")
    print(tot_items, "items")
    print(today_cals, "calories total")
    print(1900 - today_cals, "calories remaining")
    print("---")

def get_today_data(filename):
    ff = open(filename, 'r')
    lines = ff.readlines()
    ff.close()
    today_cals = 0
    tot_items = 0
    food_items = []
    #print("---")
    for line in lines:
        line = line.replace("\n","")
        food = line
        cals = 0
        name = ''
        qty = 1
        if "-" in line:
            food = line.split("-")[0].strip()
            cals = line.split("-")[1].strip()
            if line.count("-") == 2: qty = line.split("-")[2]
            name = food
        else:
            info = lookup_food(food)
            if info is None: continue
            cals = info[1]
            name = info[0]
        cals = int(cals)
        qty = int(qty)
        cals *= qty
        name = name.strip()
        #print(name, "x" + str(qty),"-", cals, "cals")
        food_items.append([name, qty, cals])
        today_cals += cals
        tot_items += 1
        #break
    return (tot_items, today_cals, food_items)

def get_period_data(period):
    today = datetime.now()
    days_done = 0
    current_date = today + timedelta(1)
    output = []
    while days_done < period:
        current_date = current_date - timedelta(1)
        date_str = str(current_date).split(" ")[0]
        filename = os.getcwd() + "\\" + date_str + ".txt"
        if not os.path.exists(filename):
            output.append([date_str, "No data"])
        else:
            data = get_today_data(filename)
            if data is None:
                output.append([date_str, "No data"])
            else:
                tot_items = data[0]
                today_cals = data[1]
                output.append([date_str, tot_items, today_cals])
        days_done += 1
    return output

def show_period_data(weights, period):
    data = get_period_data(period)
    lastweight = -1
    currentweight = -1
    for item in data:
        date_str = item[0]
        items = item[1]
        if item[1] == 'No data':
            print(date_str, item[1])
        else:
            weight = 'N/A'
            if date_str in weights.keys():
                weight = weights[date_str]
            if weight != 'N/A':
                lastweight = weight
            if currentweight == -1 and weight != 'N/A':
                currentweight = weight
            cals = item[2]
            if cals == 0:
                print(date_str, "No data")
                continue
            deficit = cals - 2400
            print(date_str, str(cals) + " cals (" + str(deficit) + ") (" + str(weight) + "lbs)")
    print("Weight loss: " + str(int(currentweight) - int(lastweight)) + "lbs")



def lookup_food(name):
    url = "https://www.nutracheck.co.uk/CaloriesIn/Product/Search?desc=" + name.replace(" ", "+").replace("'", "%27")
    resp = req.get(url)
    started = False
    product_name = ''
    for line in resp.text.split("\n"):
        textline = ''
        try:
            soup = BeautifulSoup(line, "html.parser")
            textline = soup.get_text()
        except:
            textline = line
        if started:
            if "calories" in line and "fat" in line:
                calories = line.replace(" ", "").split("calories")[0]
                #calories = line.split(" ")[3].strip()
                #print(len(line.split(" ")))
                return (product_name, calories)
            if "<li><p>" in line:
                product_name = textline.replace("Calories in ", "")
        if "<ul class=\"LSN textLarge noListIndent nut_margin\">" in line:
            started = True
    #print(resp.text)

def get_weights():
    weights = {}
    ff = open('weight.txt','r')
    lines = ff.readlines()
    ff.close()
    for line in lines:
        date = line.split(":")[0].strip()
        weight = line.split(":")[1].strip()
        weights[date] = int(weight)
    return weights

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
filenames = get_filenames()
#print(filenames)
current_date = str(datetime.now()).split(" ")[0]
today_filename = ''
for filename in filenames:
    file_date = filename.replace(os.getcwd(),"").replace("\\","").replace(".txt","")
    if file_date == current_date:
        today_filename = filename
        show_today_data(filename)
#        show_week_data()

# create today's file if doesn't exists
current_filename = os.getcwd() + "\\" + current_date + ".txt"
if not os.path.exists(current_filename):
    ff = open(current_filename, 'w')
    ff.write("\n")
    ff.close()
    today_filename = current_filename

weights = get_weights()

while True:
    command = input("> ")
    command_split = command.split(" ")
    if command_split[0] == "today":
        if len(command_split) == 1:
            show_today_data(today_filename)
        elif len(command_split) > 1:
            temp_filename = os.getcwd() + "\\" + command_split[1] + ".txt"
            if not os.path.exists(temp_filename):
                print("Unable to find data for", command_split[1])
            else:
                print(temp_filename)
                show_today_data(temp_filename)
    if command == "week":
        show_period_data(weights, 7)
    if command == "month":
        show_period_data(weights, 30)
    if command == "edit":
        os.system("notepad.exe " + today_filename)
