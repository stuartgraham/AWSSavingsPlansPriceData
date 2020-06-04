import time
import requests
from pprint import pprint
import awsrefs as aws
import xlsxwriter
import collections
from concurrent.futures import ThreadPoolExecutor

# SETTINGS
# XLS SETTINGS
FAMILY_PER_TAB = True
LOOKUP_CODE = False

# PLAN SETTINGS
PLAN_TYPE = 'compute'
INSTANCE_FAMILY = []
PLAN_LENGTH = [1,3]                           
PLAN_COMMIT = ['A','N']      
REGIONS = ['eu-west-1', 'eu-west-2']
OSES = ['Windows', 'RHEL', 'Linux']
TENANCY = ['Shared', 'Dedicated']

#FIXED URL
BASE_URL = "https://view-publish.us-west-2.prod.pricing.aws.a2z.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/"
MID_URLS = {'compute':"compute-savings-plan-ec2",'ec2':"instance-savings-plan-ec2"}
END_URL = "index.json?timestamp="


def get_terms():
    '''Manipulates the PLAN_LENGTH and PLAN_COMMIT inputs'''
    global SP_TERMS
    terms = []
    for length in PLAN_LENGTH:
        for commit in PLAN_COMMIT:
            terms.append("{}{}".format(int(length),commit))
    SP_TERMS = terms
    

def construct_urls():
    '''Builds URL set from input'''
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
                        URLS.append("{}/{}/{}/{}/{}/{}{}".format(START_URL, term, region, os, tenancy, END_URL, TIMESTAMP))
                    if PLAN_TYPE.lower() == 'ec2':
                        for instance in INSTANCE_FAMILY: 
                            URLS.append("{}/{}/{}/{}/{}/{}/{}{}".format(START_URL, term, instance, region, os, tenancy, END_URL, TIMESTAMP))

    print("Working on {} URLS".format(len(URLS)))
    return URLS


def get_json(in_url):
    ''' Parse json to ordered dict '''
    response = requests.get(in_url)
    if response.status_code != 200:
        print("ERROR : Could not connect to {}".format(in_url))
    working_data = response.json()
    for i in working_data['regions'].values():
        for k, v in i.items():
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
    ''' Write to XSLX '''
    xls_file = "{}-savings-plans.xlsx".format(PLAN_TYPE.lower())
    workbook = xlsxwriter.Workbook(xls_file)
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
    ''' Main entry point of the app '''
    get_terms()
    print("\nRegions - {}".format(', '.join(map(str, REGIONS))))
    print("OS - {}".format(', '.join(map(str, OSES))))
    print("Tenancy - {}".format(', '.join(map(str, TENANCY))))
    print("Commitment Types - {}".format(', '.join(map(str, SP_TERMS))))
    working_urls = construct_urls()

    with ThreadPoolExecutor() as executor:
        executor.map(get_json, working_urls, timeout=30)

    xlwriter(response_dict)


if __name__ == "__main__":
    ''' This is executed when run from the command line '''
    start = time.time()
    response_dict = collections.OrderedDict()
    main()
    stop = time.time()
    print("\nRuntime {:0.2f}s\n".format(stop-start))