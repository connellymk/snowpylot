# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:31:50 2021

@author: Ron Simenhois
"""

import argparse
import json
import os
import shutil
import xml.etree.ElementTree as ET
from glob import glob

import pandas as pd
import requests

from config import set_logger, PITS_PATH, STATES_DATA_PATH


def download_recent_pits(data_type="xml", **kwargs):
    """
    This function downloads and saves to local machine snowpits
    from snowpilot.org. By default, it saves the recent pits since
    the last download. If they're not recent downloads, it downloads
    pits from the last 7 days. This function updates a file with all
    the dates it loaded (or atempted but find not pits) pits of

    Parameters
    ----------
    data_type : str, optional
        The data format to download the data. The other option is caaml.
        The default is 'xml'.
    **kwargs : dict of str type
        A dictionary with strings of the start and end dates.
        The dates are in in the foremat of YYYY-MM-DD. If the dates are not
        specefied, the function will download the last day's pits.

    Returns
    -------
    None.

    """
    from datetime import datetime
    from datetime import timedelta

    if os.path.isfile(os.path.join(PITS_PATH, "MT", "pits_dates_inventory.txt")):
        with open(os.path.join(PITS_PATH, "MT", "pits_dates_inventory.txt")) as pf:
            pits_dates = pf.read().split(",")
        start = max(pits_dates)
    else:
        start = (datetime.now() - timedelta(days=7)).date().strftime("%Y-%m-%d")
    end = datetime.now().date().strftime("%Y-%m-%d")
    start = kwargs.get("start", start)
    end = kwargs.get("end", end)
    with open(STATES_DATA_PATH) as sdf:
        state_data = json.load(sdf)
    for state in state_data.keys():  # in ['CO', 'MT']:
        path = os.path.join(PITS_PATH, state)
        os.makedirs(path, exist_ok=True)
        try:
            with open(os.path.join(path, "pits_dates_inventory.txt"), "r") as f:
                dates_with_pits = f.read().split(",")
                start = min(start, max(dates_with_pits))
        except FileNotFoundError:
            dates_with_pits = []
        download_dates = [
            d[:10] for d in pd.date_range(start, end, freq="D").strftime("%Y-%m-%d")
        ]
        for s, e in zip(download_dates, download_dates[1:]):
            dates_with_pits.append(s)
            if os.path.isfile(os.path.join(path, f"{s}_pits.xml")):
                continue
            if data_type == "xml":
                download_xml(
                    s,
                    e,
                    state,
                    save_file=os.path.join(path, f"{s}_pits.xml"),
                    **state_data,
                )
            elif data_type == "caaml":
                saved_file = download_camml(s, e, state)
                extract_zipped_pits(saved_file)

        with open(os.path.join(path, "pits_dates_inventory.txt"), "w") as f:
            dates_with_pits = sorted(set(dates_with_pits))
            f.write(",".join(dates_with_pits))
        log.info("XML pits were downloaded for dates {} - {}".format(start, end))


def load_xml_from_file(start_date, end_date, state):
    """
    This function checks if there are saved snowpits for the requested
    dates range on the local machine and reads them if there are.

    Parameters
    ----------
    start_date : str
        format of YYYY-MM-DD.
    end_date : str
        format of YYYY-MM-DD.
    state : str
        state code of the state to read pits of .
        options: CO, MT
    Returns
    -------
    pits_xml_data : list
        list of text containing pits data for each date in xml format.

    """
    pits_path = os.path.join(PITS_PATH, state)
    pits_xml_data = []
    try:
        with open(os.path.join(pits_path, "pits_dates_inventory.txt"), "r") as f:
            avaliabole_dates = f.read().split(",")
    except FileNotFoundError:
        log.error(
            f"Pits dates inventory file not found - {os.path.join(pits_path, 'pits_dates_inventory.txt')}"
        )
        avaliabole_dates = []
    if start_date in avaliabole_dates and end_date in avaliabole_dates:
        start_idx = avaliabole_dates.index(start_date)
        end_idx = avaliabole_dates.index(end_date)
        load_dates = avaliabole_dates[start_idx:end_idx]
        load_files = [os.path.join(pits_path, f + "_pits.xml") for f in load_dates]

        for date in load_files:
            if os.path.isfile(date):
                try:
                    root = ET.parse(date).getroot()
                    xml = ET.tostring(root, encoding="utf8", method="xml")
                    pits_xml_data.append(xml)
                except:
                    pass
    return pits_xml_data


def download_xml(start_date, end_date, state, save_file=None, **kwargs):
    """
    This function queries snowpits from snowpilot.org for a given
    date range and state. The snopits data is downloaded in xml form

    Parameters
    ----------
    start_date : str
        format of YYYY-MM-DD.
    end_date : str
        format of YYYY-MM-DD.
    state : str
        CO or MT.
    save_file : str, optional
        path to save the pits. If none is given, not file is saved.
        The default is None.

    Returns
    -------
    data : str
        The downloaded snowpits in xml format.

    """

    SITE_URL = "https://snowpilot.org"
    LOG_IN_URL = SITE_URL + "/user/login"
    QUERY_URL = SITE_URL + "/snowpilot-query-feed.xml?"  #'/avscience-query-feed.xml?'#
    state_id = kwargs.get(state).get("id")

    user = os.environ.get("SNOWPILOT_USER")
    password = os.environ.get("SNOWPILOT_PASSWORD")
    payload = {"name": user, "pass": password, "form_id": "user_login", "op": "Log in"}

    query = f"STATE[{state_id}]={state_id}&OBS_DATE_MIN={start_date}&OBS_DATE_MAX={end_date}&per_page=1000"
    with requests.Session() as s:
        _ = s.post(LOG_IN_URL, data=payload)
        r = s.post(QUERY_URL + query, data=query)
    if r.status_code == 200 and '<?xml version="1.0"' in r.text:
        log.info("XML download sucsses")
        data = r.text
        if save_file is not None:
            tree = ET.ElementTree(ET.fromstring(data))
            tree.write(save_file)
    else:
        log.info(
            f"XML download faliure with code {r.status_code} or there are no pits for srate {state} this date ({start_date})"
        )
        data = None

    return data


def download_camml(start_date="2021-01-01", end_date="2021-02-30", state="CO"):
    """
    This function queries snowpits from snowpilot.org for a given
    date range and state. The snopits data is downloaded in zipped caaml
    files for every snopit

    Parameters
    ----------
    start_date : str
        format of YYYY-MM-DD.
    end_date : str
        format of YYYY-MM-DD.
    state : str
        CO or MT. The default is CO.
    save_file : str, optional
        path to save the pits. If none is given, not file is saved.
        The default is None.

    Returns
    -------
    data : str
        The downloaded snowpits in xml format.

    """

    SITE_URL = "https://snowpilot.org"
    LOG_IN_URL = SITE_URL + "/user/login"
    QUERY_URL = SITE_URL + "/avscience-query-caaml.xml?"
    DATA_URL = "https://snowpilot.org/sites/default/files/tmp/"
    save_file = None
    user = os.environ.get("SNOWPILOT_USER")
    password = os.environ.get("SNOWPILOT_PASSWORD")
    payload = {"name": user, "pass": password, "form_id": "user_login", "op": "Log in"}

    q = f"STATE={state}&OBS_DATE_MIN={start_date}&OBS_DATE_MAX={end_date}&per_page=100"
    with requests.Session() as s:
        _ = s.post(LOG_IN_URL, data=payload)
        query_pits = s.post(QUERY_URL + q)
        pist_file = query_pits.headers.get("Content-Disposition", None)
        if pist_file is not None and query_pits.status_code == 200:
            pists_file = pist_file[22:-1].replace("_caaml", "")
            pists_path = DATA_URL + pists_file
            pits = s.get(pists_path)
            log.info(f"Caaml data downlod sucsses. Donload file {pist_file}")
            data = pits.content
            save_file = os.path.join(PITS_PATH, pists_file)
            with open(save_file, "wb") as f:
                f.write(data)
        else:
            log.warning(
                f"Caaml data downlod faliure with code: {query_pits.status_code}"
            )
    return save_file


def extract_zipped_pits(f_name):
    """
    This function extract the caaml *.tar.gz file into the caaml
    snowpits file and save the files

    Parameters
    ----------
    f_name : str
        path to the *.tar.gz to unzip.

    Returns
    -------
    None.

    """
    shutil.unpack_archive(f_name, PITS_PATH)
    extraceted_path = f_name.split(".")[0]
    for f in glob(extraceted_path + "/*caaml.xml"):
        dest = os.path.join(PITS_PATH, os.path.split(f)[1])
        shutil.copyfile(f, dest)
    shutil.rmtree(extraceted_path, ignore_errors=True)
    for f in glob(os.path.join(PITS_PATH, "*tar.gz")):
        os.remove(f)


def main(args):
    data_source = args.data_source
    params = {}
    if args.start is not None:
        params["start"] = args.start
    if args.end is not None:
        params["end"] = args.end

    download_recent_pits(data_source, **params)


log = set_logger("Download data", log_file="../LOGS/SnowPilotOnMap.log", level="DEBUG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_source", default="xml")
    parser.add_argument("-s", "--start")
    parser.add_argument("-e", "--end")

    args = parser.parse_args()
    main(args)
