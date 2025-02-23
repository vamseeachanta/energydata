# Standard library imports
import os
import logging
from loguru import logger

# Third party imports
import pandas as pd

from assetutilities.common.utilities import is_dir_valid_func
from assetutilities.common.yml_utilities import WorkingWithYAML  # noqa
from assetutilities.modules.zip_utilities.read_zip_to_df import ReadZiptoDf

wwy = WorkingWithYAML()
rziptodf = ReadZiptoDf()

class GetDataFromFiles:
    
    def __init__(self):
        pass

    def router(self, cfg):

        if cfg['data_from_files']['production']:
            self.get_production_data_by_api12(cfg)

        return cfg

    def get_production_data_by_api12(self, cfg):

        folder_path = cfg['data_retrieval']['production']['zip']

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")

        library_name = 'energydata'
        library_file_cfg = {
            'filepath': folder_path,
            'library_name': library_name
        }

        folder_path = wwy.get_library_filepath(library_file_cfg, src_relative_location_flag=False)

        api12 = cfg['data']['groups'][0]['api12']
        logging.info(f"Getting production data for API12: {api12} ... START")
        output_file = os.path.join(cfg['Analysis']['result_folder'], 'Data', 'production_data_' + str(api12) + '.csv')

        api12_dataframes= {}
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".zip"):
                zip_filepath = os.path.join(folder_path, file_name)

                # Load the ZIP file into memory
                with open(zip_filepath, "rb") as f:
                    zip_bytes = f.read()

                column_names = ['LEASE_NUMBER', 'COMPLETION_NAME', 'PRODUCTION_DATE', 'DAYS_ON_PROD', 'PRODUCT_CODE', 'MON_O_PROD_VOL', 'MON_G_PROD_VOL', 'MON_WTR_PROD_VOL', 'API_WELL_NUMBER', 'WELL_STAT_CD', 'AREA_CODE_BLOCK_NUM', 'OPERATOR_NUM', 'SORT_NAME', 'BOEM_FIELD', 'INJECTION_VOLUME', 'PROD_INTERVAL_CD', 'FIRST_PROD_DATE', 'UNIT_AGT_NUMBER', 'UNIT_ALOC_SUFFIX']
                
                df = rziptodf.zip_to_dataframes(zip_bytes, column_names)
                df_name = file_name.split('.')[0]
                
               
    
                if 'API_WELL_NUMBER' not in df.columns:
                    print(f"Skipping {df_name}: 'API_WELL_NUMBER' column not found.")
                    continue
                
                # Find matching rows for the current api12
                matching_rows = df[df['API_WELL_NUMBER'] == api12]

                if not matching_rows.empty:
                    # Move 'API_WELL_NUMBER' column to the first position
                    columns = ['API_WELL_NUMBER'] + [col for col in matching_rows.columns if col != 'API_WELL_NUMBER']
                    matching_rows = matching_rows[columns]

                    # Append matching rows to the corresponding api12 DataFrame
                    if api12 not in api12_dataframes:
                        api12_dataframes[api12] = matching_rows
                    else:
                        api12_dataframes[api12] = pd.concat([api12_dataframes[api12], matching_rows], ignore_index=True)

                    logger.info(f"Production data found for API {api12} in file {df_name}.")
                else:
                    logger.debug(f"Production data NOT found for API {api12} in file {df_name}.")

               

        # Write each api12 DataFrame to a separate output file
        for api12, df in api12_dataframes.items():
            output_file = os.path.join(output_file)
            df.to_csv(output_file, index=False)
            print(f"API {api12} Matched rows from certain files written to {output_file} .")

        logging.info(f"Getting production data for API12: {api12} ... COMPLETE")

        return api12_dataframes