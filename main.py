import requests
import csv
from pprint import pprint
import time
 
CSVFILE = 'savings-plans.csv'
REGIONS = ['eu-west-1','eu-west-2']
TYPES = ['Windows', 'RHEL', 'Linux']
SPPRICES = ['1YALL', '1YNO', '3YALL', '3YNO']  #add 1YPA and 3YPA for partials
TENANCY = ['Shared', 'Dedicated']
BASEURL = "https://view-publish.us-west-2.prod.pricing.aws.a2z.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-savings-plan-ec2"
ENDURL = "index.json?timestamp="
 
def construct_urls():
    URLS=[]
    TIMESTAMP = str(int(time.time()))
    for R in REGIONS:
        if R == "eu-west-1":
            R = "EU%20(Ireland)"
        if R == "eu-west-2":
            R = "EU%20(London)"
        for T in TYPES:
            for S in SPPRICES:
                if S == "1YALL":
                    S= '1%20year/All%20Upfront'
                if S == "1YNO":
                    S= '1%20year/No%20Upfront'
                if S == "1YPA":
                    S= '1%20year/Partial%20Upfront'
                if S == "3YALL":
                    S= '3%20year/All%20Upfront'
                if S == "3YNO":
                    S= '3%20year/No%20Upfront'
                if S == "3YPA":
                    S= '3%20year/Partial%20Upfront'
                for X in TENANCY:
                    URLS.append("{}/{}/{}/{}/{}/{}{}".format(BASEURL,S,R,T,X,ENDURL,TIMESTAMP))
    pprint(URLS)
    return URLS
 
def get_json(in_url):
    time.sleep(1)
    response = requests.get(in_url)
    working_data = response.json()
    working_data = working_data['regions']
    for i in working_data:
        region = i
    
    for k,v in working_data[region].items():
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
        spcode = "{}-{}-{}-{}-{}".format(instance,spregion,operatingsystem,tenancy,commitcode)
        append_csv([spcode,sprate,odrate])
 
def create_new_csv():
    with open(CSVFILE, mode='w', newline='') as sp_file:
        sp_writer = csv.writer(sp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sp_writer.writerow(["SP-ITEM","SP-RATE","OD-RATE"])
 
def append_csv(line):
    with open(CSVFILE, mode='a', newline='') as sp_file:
        sp_writer = csv.writer(sp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sp_writer.writerow(line)
 
create_new_csv()
working_urls = construct_urls()
for i in working_urls:
    i = i + str(int(time.time()))
    get_json(i)
