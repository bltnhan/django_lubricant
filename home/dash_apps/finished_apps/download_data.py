import urllib.request

# data A220222 Gain - VN Lubricant Import Data
url1 = 'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107257&ithint=file%2cxlsx&authkey=!AMISo-nz92nMhpA'

# company directory
url2 = 'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107216&ithint=file%2cxlsx&authkey=!AFWwzx98ryaPkig'

# oil application
url3 = 'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107098&ithint=file%2cxlsx&authkey=!AFjg9MHgv4VRIqI'

# main brand
url4 = 'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107220&ithint=file%2cxlsx&authkey=!ALjBwbSqS6TYXn4'

urllib.request.urlretrieve(url1, "home/dash_apps/finished_apps/data/data.xlsx")
urllib.request.urlretrieve(url2, "home/dash_apps/finished_apps/data/company_directory.xlsx")
urllib.request.urlretrieve(url3, "home/dash_apps/finished_apps/data/oil_application.xlsx")
urllib.request.urlretrieve(url4, "home/dash_apps/finished_apps/data/main_brand.xlsx")


