from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import os
import geopandas as gpd
import zipfile


def get_sentinel_images(reef, start_date, end_date, num_images,user,password):
    #login into api
    api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

    #load in geojson of reef
    reef_path = reef.get_path()
    reef_gjson_fp = os.path.join(reef_path ,reef.get_reef_name()+'.geojson')
    reef_footprint = geojson_to_wkt(read_geojson(reef_gjson_fp))

    #query sentinel sat api
    products = api.query(reef_footprint,date = (start_date, end_date),platformname = 'Sentinel-2'\
                         ,area_relation = 'Intersects',processinglevel = 'Level-2A',\
                         order_by = 'cloudcoverpercentage')

    #creating folder for saving sentinel images
    sentinel_path = os.path.join(reef_path, 'SAFE files')
    if not os.path.exists(sentinel_path):
        os.makedirs(sentinel_path)

    #downloading num_images
    for i,x in enumerate(products.items()):
        k,v = x[0],x[1]
        if i < num_images:
            api.download(k, directory_path = sentinel_path)

    #unzipping files
    for file in os.listdir(sentinel_path):
        if file.endswith('.zip'):
            file_path = os.path.join(sentinel_path, file)
            out_path = os.path.join(sentinel_path, file.split('.')[0])

            if os.path.exists(file_path) and not os.path.exists(out_path):
                with zipfile.ZipFile(file_path,"r") as zip_ref:
                    zip_ref.extractall(sentinel_path)
                os.remove(file_path)