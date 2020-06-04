import requests
from pprint import pprint
import time
import awsrefs as aws
import xlsxwriter
import collections
from concurrent.futures import ThreadPoolExecutor

# SETTINGS
# CSVFILE: Path to CSV File
CSVFILE = 'savings-plans.xlsx'
CSV_PER_TAB = True
# PLANLENGTH: 1 year, 3 years
PLANLENGTH = [1,3]
# PLANCOMMIT: [A]ll Upfront, [N]o Upfront, [P]artial Upfront                               
PLANCOMMIT = ['A','N']
# REGION: https://github.com/adv4000/aws-region-codes            
REGIONS = ['eu-west-1', 'eu-west-2']
TYPES = ['Windows', 'RHEL', 'Linux']
TENANCY = ['Shared', 'Dedicated']

#FIXED URL
BASEURL = "https://view-publish.us-west-2.prod.pricing.aws.a2z.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-savings-plan-ec2"
ENDURL = "index.json?timestamp="

def get_plans():
    plans = []
    for _L in PLANLENGTH:
        for _C in PLANCOMMIT:
            plans.append("{}{}".format(int(_L,),_C))
    return plans


def construct_urls():
    URLS = []
    TIMESTAMP = str(int(time.time()))
    #SPPRICES = get_plans()
    for _R in REGIONS:
        for k,v in aws.regions.items():
            if _R == k:
                R = v

        for T in TYPES:
            for _S in SPPRICES:
                _S = list(_S)
                for k,v in aws.commit.items():
                    if _S[1] == k:
                        S = "{} year/{}".format(str(_S[0]),v)
                
                for X in TENANCY:
                    URLS.append((_R, "{}/{}/{}/{}/{}/{}{}".format(BASEURL, S, R, T, X, ENDURL, TIMESTAMP)))

    print("Working on {} URLS".format(len(URLS)))
    return URLS


def get_json(in_url):
    (_region, in_url) = in_url
    response = requests.get(in_url)
    working_data = response.json()

    working_data = working_data['regions']
    for i in working_data:
        region = i

    for k, v in working_data[region].items():
        entry = {}
        rate = v
        tenancy = rate['ec2:Tenancy']
        instance = rate['ec2:InstanceType']
        spregion = rate['ec2:Location']
        for k,v in aws.regions.items():
            if spregion == v:
                spregion = k

        operatingsystem = rate['ec2:OperatingSystem']
        for k,v in aws.os.items():
            if operatingsystem == v:
                operatingsystem = k
    
        commityear = rate['LeaseContractLength']
        commitamount = rate['PurchaseOption']
        for k,v in aws.commit.items():
            if commitamount  == v:
                commitamount  = k

        commitcode = commityear + commitamount

        sprate = rate['price']
        odrate = rate['ec2:PricePerUnit']
        spcode = "{}-{}-{}-{}-{}".format(instance, spregion, operatingsystem, tenancy, commitcode)
        savingper = ((float(odrate)-float(sprate))/float(odrate))*100

        entrykey = instance+spcode
        entry = {"instance": instance,
                "region": spregion,
                 "os": operatingsystem,
                 "tenancy": tenancy,
                 "commitcode": commitcode,
                 "odrate": "{:0.4f}".format(float(odrate)),
                 "sprate": sprate,
                 "savingper": "{:0.2f}".format(savingper)
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

def main():
    global SPPRICES
    SPPRICES = get_plans()
    print("\nRegions - {}".format(', '.join(map(str, REGIONS))))
    print("OS - {}".format(', '.join(map(str, TYPES))))
    print("Tenancy - {}".format(', '.join(map(str, TENANCY))))
    print("Commitment Types - {}".format(', '.join(map(str, SPPRICES))))
    working_urls = construct_urls()

    with ThreadPoolExecutor() as executor:
        executor.map(get_json, working_urls, timeout=30)

    xlwriter(response_dict)

start = time.time()
response_dict = collections.OrderedDict()
main()
stop = time.time()
print("\nRuntime {:0.2f}\n".format(stop-start))