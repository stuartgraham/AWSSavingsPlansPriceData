import requests
import csv
from pprint import pprint
import time
import xlsxwriter
import collections

CSVFILE = 'savings-plans.xls'

REGIONS = ['eu-west-1']
TYPES = ['Linux']
SPPRICES = ['1YALL']  # add 1YPA and 3YPA for partials
TENANCY = ['Shared']

REGIONS = ['eu-west-1', 'eu-west-2']
TYPES = ['Windows', 'RHEL', 'Linux']
SPPRICES = ['1YALL', '1YNO', '3YALL', '3YNO']  # add 1YPA and 3YPA for partials
TENANCY = ['Shared', 'Dedicated']




BASEURL = "https://view-publish.us-west-2.prod.pricing.aws.a2z.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-savings-plan-ec2"
ENDURL = "index.json?timestamp="


def construct_urls():
    URLS = []
    TIMESTAMP = str(int(time.time()))
    for R in REGIONS:
        if R == "eu-west-1":
            R = "EU%20(Ireland)"
        if R == "eu-west-2":
            R = "EU%20(London)"
        for T in TYPES:
            for S in SPPRICES:
                if S == "1YALL":
                    S = '1%20year/All%20Upfront'
                if S == "1YNO":
                    S = '1%20year/No%20Upfront'
                if S == "1YPA":
                    S = '1%20year/Partial%20Upfront'
                if S == "3YALL":
                    S = '3%20year/All%20Upfront'
                if S == "3YNO":
                    S = '3%20year/No%20Upfront'
                if S == "3YPA":
                    S = '3%20year/Partial%20Upfront'
                for X in TENANCY:
                    URLS.append("{}/{}/{}/{}/{}/{}{}".format(BASEURL, S, R, T, X, ENDURL, TIMESTAMP))
    pprint(URLS)
    return URLS


def get_json(in_url):
    time.sleep(1)
    response = requests.get(in_url)
    working_data = response.json()
    working_data = working_data['regions']
    for i in working_data:
        region = i

    for k, v in working_data[region].items():
        entry = {}
        rate = v
        instance = rate['ec2:InstanceType']
        spregion = rate['ec2:Location']
        if spregion == "EU (Ireland)":
            spregion = "eu-west-1"
        if spregion == "EU (London)":
            spregion = "eu-west-2"
        operatingsystem = rate['ec2:OperatingSystem']
        if operatingsystem == "Linux":
            operatingsystem = "Linux/UNIX"
        if operatingsystem == "RHEL":
            operatingsystem = "Red Hat Enterprise Linux"
        tenancy = rate['ec2:Tenancy']

        commityear = rate['LeaseContractLength']
        committime = rate['PurchaseOption']
        if committime == "All Upfront":
            committime = "A"
        if committime == "Partial Upfront":
            committime = "P"
        if committime == "No Upfront":
            committime = "N"
        commitcode = commityear + committime

        sprate = rate['price']
        odrate = rate['ec2:PricePerUnit']
        spcode = "{}-{}-{}-{}-{}".format(instance, spregion, operatingsystem, tenancy, commitcode)
        savingper = ((float(odrate)-float(sprate))/float(odrate))*100

        entrykey = instance+commitcode
        entry = {"instance": instance,
                "region": spregion,
                 "os": operatingsystem,
                 "tenancy": tenancy,
                 "commitcode": commitcode,
                 "odrate": "{:0.4f}".format(float(odrate)),
                 "sprate": sprate,
                 "savingper": "{:0.2f}%".format(savingper)
                 }

        if instance[0] not in response_dict:
            response_dict[instance[0]] = collections.OrderedDict()
            response_dict[instance[0]][entrykey] = entry
        else:
            response_dict[instance[0]][entrykey] = entry


def xlwriter(response_dict):
    workbook = xlsxwriter.Workbook(CSVFILE)

    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '$#,##0'})

    for key, value in response_dict.items():
        worksheet = workbook.add_worksheet(key)

        row = 0
        column = 0

        worksheet.write(row, column, "Instance", bold)
        worksheet.write(row, column + 1, "region", bold)
        worksheet.write(row, column + 2, "os", bold)
        worksheet.write(row, column + 3, "tenancy", bold)
        worksheet.write(row, column + 4, "commitcode", bold)
        worksheet.write(row, column + 5, "odrate", bold)
        worksheet.write(row, column + 6, "sprate", bold)
        worksheet.write(row, column + 7, "% Saving", bold)

        row = 1
        column = 0

        for _key, _value in value.items():
            print(_key)
            print(_value)
            worksheet.write(row, column, _value["instance"])
            worksheet.write(row, column + 1, _value["region"])
            worksheet.write(row, column + 2, _value["os"])
            worksheet.write(row, column + 3, _value["tenancy"])
            worksheet.write(row, column + 4, _value["commitcode"])
            worksheet.write(row, column + 5, _value["odrate"], money)
            worksheet.write(row, column + 6, _value["sprate"], money)
            worksheet.write(row, column + 7, _value["savingper"])
            row += 1

    workbook.close()



working_urls = construct_urls()
response_dict = collections.OrderedDict()
for i in working_urls:
    i = i + str(int(time.time()))
    get_json(i)

xlwriter(response_dict)
exit()

create_new_csv()

def create_new_csv():
    with open(CSVFILE, mode='w', newline='') as sp_file:
        sp_writer = csv.writer(sp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sp_writer.writerow(["SP-ITEM", "SP-RATE", "OD-RATE"])


def append_csv(line):
    with open(CSVFILE, mode='a', newline='') as sp_file:
        sp_writer = csv.writer(sp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sp_writer.writerow(line)