import csv

pd = {0: 0, 2: 0, 4: 0, 6:0, 8:0}
with open("C:\\Users\\rvtej\\Documents\\Spring 2021\\FAI\\testData.csv") as file:
    data = csv.reader(file, delimiter='=')
    for id, each in enumerate(data):
        if id in [0,2,4,6,8]:
            for i in each:
                pd[id] += (float(i[1:-1]))

for each in pd.items():
    pd[each[0]] = each[1] - 5000000

print(pd)