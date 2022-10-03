import streamlit as st
import os
import pandas as pd
import datetime
def index():
    st.session_state["index"] =True
    st.session_state["page1"] =False
    st.session_state["page2"] =False
    st.header("About this application.")
    st.markdown("Recent international standardization of accounting reporting format led to the number of reports with XBRL increase. XBRL is a generalized format of operation report: e.g., including balance sheet, investment, and operating status. In general, XBRLs contain essential information for investors and academic researchers to analyze the company's financial status. However, the XBRL file format is hard to read for humans. It, therefore, made it difficult to access companies' accounting information easily. I thus made an open-source web-application that enables easy data acquisition of accounting information disclosed on EDINET and its preprocessing.")

    #with st.form(key="name-form"):
    #    st.text_input("Name", key="name")
    #    st.form_submit_button(label="Submit", on_click=change_page)

st.set_page_config(page_title="Get Data from EDINET", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
index()

import streamlit as st
import os
import pandas as pd
import datetime
import edinet
import numpy as np
from edinet.xbrl_file import XBRLDir
from edinet.xbrl_file import XBRLFile
from edinet.xbrl_file import XBRLElement

import os
import shutil
from bs4 import BeautifulSoup




class XBRLFile_():

    def __init__(self, data):
        self._root = BeautifulSoup(data, "lxml-xml")

    @property
    def root(self):
        return self._root

    @property
    def text(self):
        return self._root.text

    def find(self, tag, attrs={}, recursive=True, text=None,
             **kwargs):
        tag_element = self._root.find(tag, attrs, recursive, text, **kwargs)
        return XBRLElement(tag_element)

    def find_all(self, tag, attrs={}, recursive=True, text=None,
                 limit=None, **kwargs):
        tag_elements = self._root.find_all(
                        tag, attrs, recursive, text, limit, **kwargs)

        return [XBRLElement(e) for e in tag_elements]

    def parse_by(self, parser_cls):
        return parser_cls(self._root)


    
def collectTags(data):
    Tags = []
    for i in data.values:
        i = i.split(" ")
        n = 0
        dic = {}
        N = len(i)
        for j in i:
            if len(j)==0:
                continue
            j = j.strip("<")
            if j[0]=="j":
                Tags.append(j)
            break
        pass
    Tags = np.unique(Tags)
    return Tags
    pass

def ReturnTags(Tags):
    tags = []
    dic = {i[0]:i[1] for i in pd.read_csv("Dictionary_en",header=None).values}
    for i in Tags:
        if i in dic.keys():
            tags.append([dic[i],i])
            pass
        else:
            tags.append([i,i])
    return tags
    pass

def download_data():
    kind = None
    name = None
    DataPath = None
    with st.container():
        st.subheader("Please fill in following form")
        col1, col2 = st.columns(2)
        # select company
        with col1:
            st.markdown("##### Select company")
            st.markdown("Please input the company name or ticker code you want to download on the following form.")
            st.markdown("Currently available data can see from A.")
            kind = st.radio(
            "Input",
            ('Company name', 'Tieker code'))
            pass
        # select year
        with col2:
            st.markdown("##### Select year")
            now = datetime.datetime.now()
            year = now.year
            st.markdown("EDINET allows us to download data at most five years before (from {1}/{2}/{0} to {4}/{5}/{3}).".format(now.year-5,now.month,now.day,now.year,now.month,now.day) )
            pass
    with st.container():
        col1, col2 = st.columns(2)
        # select company
        with col1:
            if kind == "Company name":
                name = st.text_input("Fill in the company name")
                pass
            else:
                name = st.text_input("Fill in the ticker code" )
                pass
            pass
        # select year
        with col2:
            options = st.multiselect( 'Select year', [i for i in range(year-5,year+1,1)],  [year])
            pass
    with st.container():
        st.header("Following data is available")
        if kind !=None:
            st.dataframe(pd.DataFrame([[1,2,3],[1,2,3]]) ,use_container_width=True)
            pass
        st.text(name)
        st.text(options)
        DataPath = "S100N4TI"
    with st.container():
        try:
            if DataPath!=None:
                xbrl_path = edinet.api.document.get_xbrl(DataPath, save_dir=".tmp", expand_level="file")
                xbrlfile = XBRLFile(xbrl_path)
                st.markdown("Successed")
                return xbrlfile,xbrl_path
            pass
        except:
            st.markdown("Sorry, the data is not available")
            return None
        pass

def page1():
    xbrlfile =None
    path = None
    df = None
    with st.container():
        st.header("Application: XBRL file reader.")
        pass
    with st.container():
        st.subheader("Upload XBRL file.")
        st.markdown("""Upload XBRL file downloaded from EDINET which was located on XBRL/PublicDoc/***.xbrl.
                    """
            )
        uploaded_file = st.file_uploader("Upload XBRL file")
        if uploaded_file != None:
            try:
                xbrlfile = XBRLFile_(uploaded_file.read())
                a = uploaded_file.getvalue().decode("utf-8")
                b=""
                for i in a:
                    b+=str(i)
                    pass
                df = pd.Series(b.split("\n"))
                pass
            except:
                st.markdown("""
                            We failed to read the uploaded XBRL file. Ensure the uploaded XBRL file is 		
                                1. downloaded from EDINET. 
                                2. located on XBRL/PublicDoc/***.xbrl.
                            """)
                pass
        pass
    
    with st.container():
        if xbrlfile!=None:
            st.markdown("# See Accounting information")

            Tags = collectTags(df)
            t = np.array(ReturnTags(Tags))
            tags = st.multiselect( 'Select account items.', t[:,0])
            t = {i[0]:i[1] for i in t}
            df = []
            for i in tags:
                if xbrlfile.find(i)!=[]:
#                    st.text("{0} {1}".format(i,t[i]))
                    df.append([i, xbrlfile.find(t[i]).text])
                    pass
                else:
                    df.append([i, None])
                pass
            df = pd.DataFrame(df)
            st.dataframe(df ,use_container_width=True)
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label="Download Table",
                data=csv,
                file_name='ProcessedData.csv',
                mime='text/csv',
            )
            pass
        pass


page1()

st.header("How to use this application.")
st.markdown("to be written...")

st.header("Credit.")
st.markdown("Author: Yuki Sato. contact: yuki.sato.f.r(at)gmail.com")
    
st.header("Acknowledgement.")
st.markdown("This software is composed of various open-source software: python, pandas, numpy, edinet, requests, BeautifulSoup, streamlit, and their dependencies. We represent our greatest gratitude to all contributors.")
    