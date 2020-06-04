import time
import requests
import awsrefs as aws
import xlsxwriter
import collections
from concurrent.futures import ThreadPoolExecutor

# SETTINGS
# CSV SETTINGS
CSV_FILE = 'savings-plans.xlsx'
FAMILY_PER_TAB = True
LOOKUP_CODE = False

# PLAN SETTINGS
PLAN_TYPE = 'ec2'
INSTANCE_FAMILY = ['m5', 'c5']
PLAN_LENGTH = [1,3]                           
PLAN_COMMIT = ['A','N']      
REGIONS = ['eu-west-1', 'eu-west-2']
OSES = ['Windows', 'RHEL', 'Linux']
TENANCY = ['Shared', 'Dedicated']

PLAN_TYPE = 'ec2'
INSTANCE_FAMILY = ['m5']
PLAN_LENGTH = [1]                           
PLAN_COMMIT = ['A']      
REGIONS = ['eu-west-1']
OSES = ['Linux']
TENANCY = ['Shared']

#FIXED URL
BASE_URL = "https://view-publish.us-west-2.prod.pricing.aws.a2z.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/"
MID_URLS = {'compute':"compute-savings-plan-ec2",'ec2':"instance-savings-plan-ec2"}
#/instance-savings-plan-ec2/1%20year/All%20Upfront/m5,%20c5/EU%20(Ireland)/Windows/Dedicated/index.json?timestamp=1591304347
#/instance-savings-plan-ec2/1%20year/No%20Upfront/m5/US%20East%20(Ohio)/Linux%20with%20SQL%20Ent/Shared/
#/compute-savings-plan-ec2/1%20year/No%20Upfront/US%20East%20(Ohio)/Linux%20with%20SQL%20Ent/Shared/
END_URL = "index.json?timestamp="


def get_terms():
    global SP_TERMS
    terms = []
    for length in PLAN_LENGTH:
        for commit in PLAN_COMMIT:
            terms.append("{}{}".format(int(length),commit))
    SP_TERMS = terms
    

def construct_urls():
    URLS = []
    TIMESTAMP = str(int(time.time()))
    START_URL = "{}{}".format(BASE_URL, MID_URLS[PLAN_TYPE.lower()])
    for region in REGIONS:
        for k,v in aws.regions.items():
            if region == k:
                region = v

        for os in OSES:
            for terms in SP_TERMS:
                terms = list(terms)
                for k,v in aws.commit.items():
                    if terms[1] == k:
                        term = "{} year/{}".format(str(terms[0]),v)
                
                for tenancy in TENANCY:
                    if PLAN_TYPE.lower() == 'compute':
                        URLS.append((region, "{}/{}/{}/{}/{}/{}{}".format(START_URL, term, region, os, tenancy, END_URL, TIMESTAMP)))
                    if PLAN_TYPE.lower() == 'ec2':
                        for instance in INSTANCE_FAMILY: 
                            URLS.append("{}/{}/{}/{}/{}/{}/{}{}".format(START_URL, term, instance, region, os, tenancy, END_URL, TIMESTAMP))

    print("Working on {} URLS".format(len(URLS)))
    print(URLS)
    return URLS


def get_json(in_url):
    response = requests.get(in_url)
    if response.status != 200:
        print("ERROR : Could not connect to {}".format(in_url))
    print(response.json())
    working_data = response.json()
    print(working_data)
    print(type(working_data))
    working_data = working_data['regions']
    print(working_data)
    print(working_data.values()[0])
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

        entry_key = instance+spcode
        entry = {"instance": instance,
                "region": spregion,
                "os": operatingsystem,
                "tenancy": tenancy,
                "commitcode": commitcode,
                "odrate": "{:0.4f}".format(float(odrate)),
                "sprate": sprate,
                "savingper": "{:0.2f}".format(savingper),
                 }
        if LOOKUP_CODE == True:
            entry.update({"spcode" : spcode})

        # Tabulate Excel if True
        if FAMILY_PER_TAB == True:
            xls_tab = instance[0]
        else:
            xls_tab = 'All'

        if xls_tab not in response_dict:
            response_dict[xls_tab] = collections.OrderedDict()
            response_dict[xls_tab][entry_key] = entry
        else:
            response_dict[xls_tab][entry_key] = entry


def xlwriter(response_dict):
    workbook = xlsxwriter.Workbook(CSV_FILE)

    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '$#,##0.0000'})

    for k, v in response_dict.items():
        # Create Worksheet
        worksheet = workbook.add_worksheet(k)
        # Add Header Row
        worksheet.write(0, 0, "instance", bold)
        worksheet.write(0, 1, "region", bold)
        worksheet.write(0, 2, "os", bold)
        worksheet.write(0, 3, "tenancy", bold)
        worksheet.write(0, 4, "commitcode", bold)
        worksheet.write(0, 5, "odrate", bold)
        worksheet.write(0, 6, "sprate", bold)
        worksheet.write(0, 7, "% Saving", bold)
        if LOOKUP_CODE == True:
            worksheet.write(0, 8, "lookup", bold)

        # Iterate Rows
        row = 1
        for k, v in v.items():
            worksheet.write(row, 0, v["instance"])
            worksheet.write(row, 1, v["region"])
            worksheet.write(row, 2, v["os"])
            worksheet.write(row, 3, v["tenancy"])
            worksheet.write(row, 4, v["commitcode"])
            worksheet.write_number(row, 5, float(v["odrate"]), money)
            worksheet.write_number(row, 6, float(v["sprate"]), money)
            worksheet.write_number(row, 7, float(v["savingper"]))
            if LOOKUP_CODE == True:
                worksheet.write(row, 8, v["spcode"])
            row += 1

    workbook.close()

def main():
    get_terms()
    print("\nRegions - {}".format(', '.join(map(str, REGIONS))))
    print("OS - {}".format(', '.join(map(str, OSES))))
    print("Tenancy - {}".format(', '.join(map(str, TENANCY))))
    print("Commitment Types - {}".format(', '.join(map(str, SP_TERMS))))
    working_urls = construct_urls()

    with ThreadPoolExecutor() as executor:
        executor.map(get_json, working_urls, timeout=30)

    xlwriter(response_dict)

start = time.time()
response_dict = collections.OrderedDict()
main()
stop = time.time()
print("\nRuntime {:0.2f}s\n".format(stop-start))