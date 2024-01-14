from io import StringIO
import os
from typing import List
import panel as pn
import pandas as pd
import datetime as dt

from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter, HTMLTemplateFormatter

from osw.core import OSW
from osw.auth import CredentialManager
import osw.wiki_tools as wt
import osw.model.entity as model
from osw.utils.wiki import get_full_title
from osw.wtsite import WtSite

def createApp():

    if not 'osw' in pn.state.cache:
        print("Invalid session")
        cred_mngr=CredentialManager(

        )
        cred_mngr.add_credential(
            CredentialManager.UserPwdCredential(
                iri="demo.open-semantic-lab.org", username="<user>", password="<password>"
            )
        )
        cred = cred_mngr.get_credential(CredentialManager.CredentialConfig(iri="")) # this will select the first entry

        site = WtSite(
            WtSite.WtSiteConfig(
                iri=cred.iri,
                cred_mngr=cred_mngr
            )
        )
        osw = OSW(
            site=site
        )
    else:
        osw: OSW = pn.state.cache['osw']
        user = pn.state.cache['osw_user']
        print(user)
    
    titles = wt.semantic_search(osw.site._site, wt.SearchParam(
        query="[[HasType::Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26]]",
        limit=25,
    ))
    print(titles)

    if hasattr(model, 'Item'):
        print("Item exists")
    if hasattr(model, 'Article'):
        print("Article exists")
    else: osw.fetch_schema(OSW.FetchSchemaParam(schema_title="Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26", mode="replace"))
    if hasattr(model, 'Tutorial'):
        print("Tutorial exists")
    if not hasattr(model, 'WikiFile'):
        osw.fetch_schema(OSW.FetchSchemaParam(schema_title="Category:OSW11a53cdfbdc24524bf8ac435cbf65d9d", mode="append"))
    if not hasattr(model, 'LocalFile'):
        osw.fetch_schema(OSW.FetchSchemaParam(schema_title="Category:OSW3e3f5dd4f71842fbb8f270e511af8031", mode="append"))
    
    # import the controller modules
    # note: since they depend on the data classes, they must be imported after the schemas are loaded
    from osw.controller.file.local import (  # noqa (ignore flake8 warning)
        LocalFileController,
    )
    from osw.controller.file.wiki import WikiFileController  # noqa (ignore flake8 warning)

    #file = osw.load_entity(f"File:Roomplan.png")  # the file
    #wf2 = file.cast(WikiFileController, osw=osw)  # the file controller
    #lf2 = LocalFileController.from_other(wf2, path="dummy2.mp4")
    #lf2.put_from(wf2)

    results = []
    result_dict = {
        #"index": [],
        "id": [],
        "name": [],
        "link": [],
        "include": [],
    }
    articles : List[model.Article] = osw.load_entity(titles)
    index = 0
    for article in articles:
        #result_dict["index"].append(index)
        result_dict["id"].append(str(article.uuid))
        result_dict["name"].append(article.label[0].text)
        #result_dict["link"].append({
        #    "url": os.getenv("OSW_SERVER") + "/wiki/",
        #    "value": article.label[0].text
        #})
        result_dict["link"].append(os.getenv("OSW_SERVER") + "/wiki/" + get_full_title(article))
        result_dict["include"].append(True)
        
        #results.append(article.json())
        results.append(result_dict)
        index += 1

    df = pd.DataFrame({
        'int': [1, 2, 3],
        'float': [3.14, 6.28, 9.42],
        'str': ['A', 'B', 'C'],
        'bool': [True, False, True],
        'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10)],
        'datetime': [dt.datetime(2019, 1, 1, 10), dt.datetime(2020, 1, 1, 12), dt.datetime(2020, 1, 10, 13)]
    })#, index=[1, 2, 3])
    df = pd.DataFrame(result_dict)

    bokeh_formatters = {
        'float': NumberFormatter(format='0.00000'),
        'include': BooleanFormatter(),
        'link': HTMLTemplateFormatter(template='<a href="<%= value %>" target="_blank">link</a>')
    }
    """ {
            "_data": results,
            "_columns": [
                {"title":"ID", "field":"id"},
                {"title":"name", "field":"name"},
                {"title":"link", "field":"link"},
                {"title":"include", "field":"include"}
                ]
            } """
    result_tab = pn.widgets.Tabulator(df, formatters=bokeh_formatters, selectable='checkbox')#, buttons={'Print': "<i class='fa fa-print'></i>"})

    #def click(event):
    #    print(f'Clicked cell in {event.column!r} column, row {event.row!r} with value {event.value!r}')
    #result_tab.on_click(click)

    def filtered_file():
        print(df)
        sio = StringIO()
        df.to_csv(sio)
        sio.seek(0)
        return sio

    #download_btn = pn.widgets.FileDownload(
    #    file='FileDownload.ipynb', button_type='success', auto=False,
    #    embed=False, name="Right-click to download using 'Save as' dialog"
    #)
    fd = pn.widgets.FileDownload(
        callback=pn.bind(filtered_file), filename='filtered_autompg.csv'
    )

    def callback(e):
        print(result_tab.selection)
        #print([art[i] for i in result_tab.selection])
        print([url.split("/")[-1] for url in result_tab.selected_dataframe["link"]])
    btn = pn.widgets.Button(name='Test', button_type='primary')
    btn.on_click(callback)

    row = pn.Row(result_tab, fd, btn)

    return row

if __name__ == "__main__":
    pn.serve(createApp(), port=5007)