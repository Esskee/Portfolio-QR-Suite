from dash import dcc, html
import dash_bootstrap_components as dbc
import datetime
import pandas as pd
from pymongo import MongoClient
import certifi
from cryptography.fernet import Fernet
import boto3
import base64
import os
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles import colormasks, moduledrawers
from PIL import ImageColor, Image


###connection to mongo db
MONGO_URL = 'Placeholder'  # hidden for security
ca = certifi.where()
client = MongoClient(MONGO_URL, connect=False, tlsCAFile=ca)
db = client['smdata']


def connect_to_db():
    #as a function
    MONGO_URL = 'Placeholder'  # hidden for security
    ca = certifi.where()
    # New Authenticated Users
    client = MongoClient(MONGO_URL, connect=False, tlsCAFile=ca)
    db = client['smdata']
    return db


####connection to AWS
path = "./assets/config/awscli.ini"
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = path
print('Connected to AWS using: ' + os.environ['AWS_SHARED_CREDENTIALS_FILE'])


class QR_functions():
    #initilizer for regularly used varibles and one time db queries
    def __init__(self, agency, org):
        self.agency = agency
        self.org = org
        #for url ecryption
        self.key = Fernet(b'HzVL5G-aiUwncT84eZEILcGGFiOukYkVEvM4_5HNxo4=')
        query = {'AGENCY': agency, 'ORG': org, 'STATUS': 'live'}
        #grabbing all QR data belonging to agencies
        resp = list(db.campaign_tracker.find(query))
        if len(resp) == 0:
            query = {'AGENCY': agency, 'ORG': 'Head Office', 'STATUS': 'live'}
            resp = list(db.campaign_tracker.find(query))
        self.QR = resp
        camps = [d['CAMPAIGN'] for d in resp]
        self.campaigns = list(set(camps))
        #grabbing asset data like brand colours and logos
        assets = db.client_data.find_one({"AGENCY": agency, 'ORG': org})
        self.brandColour = assets['BRAND_COLOR']
        self.homepage = assets['BASE_URL']
        self.box_font = {'font-family': 'Franklin Gothic, Demi', 'font-size': '13px'}
        #creating dictionaries for the asset gallery
        self.asset_checker = ['market_report', 'energy_report', 'carbon_report', 'AVM', 'moving_checklist', 'selling_guide', 'secrets_guide', 'welcomeform']
        self.asset_dictionary = [{'Title': 'Market Report', 'report': 'market_report', 'Link': 'marketreport', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                  'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Energy Report', 'report': 'energy_report', 'Link': 'energydemo', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                 'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Carbon Report', 'report': 'carbon_report', 'Link': 'carbondemo', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                 'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Home Valuation', 'report': 'AVM', 'Link': 'AVM', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                 'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Moving Checklist', 'report': 'moving_checklist', 'Link': 'checklist', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                 'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Selling Guide', 'report': 'selling_guide', 'Link': 'sellingguide', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                 'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Secrets to Selling', 'report': 'secrets_guide', 'Link': 'secrets', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                 'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'},
                                 {'Title': 'Valuation Tool', 'report': 'val_checker', 'Link': 'welcomeform', 'img': 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos/Battersea-Park.jpg.jpeg',
                                  'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'}]

    def Splitter(self, i):
        #basic string splitter for the ref string in the client data db, this whole system badly needs a rework going forward
        #A simple campaign field would work wonders, or just more fields in general instead of concatinating a string
        #this needs to be sorted badly
        resp = i.split('-')
        resp = resp[0].split('^')
        return resp[0]

    def QR_code_stats(self, campaign):
        #grabbing stats from the live db tracking QR responses
        #convert into a pandas df then sorting by campaign for some quick activity stats
        df = db.agency_prospects
        df = pd.DataFrame(list(df.find()))
        drop_list = ['_id']
        df = df.drop(drop_list, axis=1)
        df = df[(df['AGENCY'] == self.agency) & (df['ORG'] == self.org)]
        camps = []
        for i in df.REF:
            camps.append(self.Splitter(i))
        responses = []
        for i in camps:
            if i == campaign:
                responses.append(i)
        return len(responses)

    def get_QR_assets(self, campaign):
        #grabbing more data about the specific QR, after the init has run
        QR = pd.DataFrame(self.QR)
        QR = QR[QR['CAMPAIGN'] == campaign]
        self.URL = QR['AWS_LOCATION']
        self.qr_url = QR['QRCODE']
        self.description = QR['DESCRIPTION']
        self.link = QR['QRCODE']
        self.cstring = QR['RGB']
        self.icon = QR['ICON']
        self.QR_Style = QR['STYLE']

    def get_QR_template_assets(self, campaign):
        #grabbing specific QR style assets for style duplication
        QR = pd.DataFrame(self.QR)
        QR = QR[QR['CAMPAIGN'] == campaign]
        cstring = QR.iloc[0]['RGB']
        icon = QR.iloc[0]['ICON']
        QR_style = QR.iloc[0]['STYLE']
        url = QR.iloc[0]['QRCODE']
        return cstring, icon, QR_style, url

    def get_qr_icons(self):
        #grabs data on locally saved QR center icons, both a selection of defaults and agency specific assets
        df = db.media_vault
        df = pd.DataFrame(list(df.find()))
        drop_list = ['_id']
        df = df.drop(drop_list, axis=1)
        agents = [self.agency, 'Smith Buck and Son']
        orgs = [self.org, 'Head Office']
        df = df[df.AGENCY.isin(agents)]
        df = df[df.ORG.isin(orgs)]
        df = df[df['MEDIA_TYPE'] == 'icon']
        df = df[['ASSET_URL', 'DESCRIPTION']]
        icons = []
        for i, r in df.iterrows():
            icons.append(r['ASSET_URL'])
        return df, icons

    def get_qr_links_df(self):
        #grabbing media links (currently unused)
        df = db.media_links
        df = pd.DataFrame(list(df.find()))
        drop_list = ['_id']
        df = df.drop(drop_list, axis=1)
        df = df[(df['AGENCY'] == self.agency) & (df['ORG'] == self.org)]
        return df

    def style_qr(self, c1, c2, c3, QR_Style, logo):
        #styling QRs using form inputs
        #convert colours to rgb from hex, PIL only takes rgb codes but the form only passes hexes
        colour1 = ImageColor.getcolor(c1, "RGB")
        colour2 = ImageColor.getcolor(c2, "RGB")
        colour3 = ImageColor.getcolor(c3, "RGB")
        #This string is saved to the db so it can be copied as a template
        cstring = f'{c1}-{c2}-{c3}'
        #default option
        style = colormasks.SolidFillColorMask(
            back_color=colour1, front_color=colour2)

        #pack the type
        if QR_Style == 'Single_colour':
            style = colormasks.SolidFillColorMask(
                back_color=colour1, front_color=colour2)
        elif QR_Style == 'Gradient_down':
            style = colormasks.VerticalGradiantColorMask(
                back_color=colour1, top_color=colour2, bottom_color=colour3)
        elif QR_Style == 'Gradient_across':
            style = colormasks.HorizontalGradiantColorMask(
                back_color=colour1, left_color=colour2, right_color=colour3)
        elif QR_Style == 'Gradient_center':
            style = colormasks.RadialGradiantColorMask(
                back_color=colour1, center_color=colour2, edge_color=colour3)
        #pass the logo through for convenience
        return style, logo, cstring, QR_Style

    def QR_template(self, campaign):
        #Similar styling, to the QR styler above but using a previously created QR and copying the saved styles
        style = []
        cstring, icon, QR_style, url = self.get_QR_template_assets(campaign)
        colours = cstring.split('-')
        colour1 = ImageColor.getcolor(colours[0], "RGB")
        colour2 = ImageColor.getcolor(colours[1], "RGB")
        colour3 = ImageColor.getcolor(colours[2], "RGB")

        if QR_style == 'Single_colour':
            style = colormasks.SolidFillColorMask(
                back_color=colour1, front_color=colour2)
        elif QR_style == 'Gradient_down':
            style = colormasks.VerticalGradiantColorMask(
                back_color=colour1, top_color=colour2, bottom_color=colour3)
        elif QR_style == 'Gradient_across':
            style = colormasks.HorizontalGradiantColorMask(
                back_color=colour1, left_color=colour2, right_color=colour3)
        elif QR_style == 'Gradient_center':
            style = colormasks.RadialGradiantColorMask(
                back_color=colour1, center_color=colour2, edge_color=colour3)
        return style, icon, cstring, QR_style

    def QR_template_results(self, template):
        #grabs template sylings from the assets function and splits the cstring and the URL for the QR
        cstring, icon, QR_style, url = self.get_QR_template_assets(template)
        colour1, colour2, colour3 = cstring.split('-')
        #splitting the URL on a / with the setup of a standard QR link the asset link will always be in the same slice
        split = url.split('/')
        return colour1, colour2, colour3, QR_style, icon, url, split

    def Make_QR_preview(self, style, icon, url):
        #The code to render the preview imgage for the create new QR function
        myimage = f"./assets/{icon}"
        icon = myimage

        qr = qrcode.QRCode(
              version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(image_factory=StyledPilImage,  embeded_image_path=icon,
                            color_mask=style, module_drawer=moduledrawers.RoundedModuleDrawer()).convert('RGBA')
        #image is returned in bytecode and must be formatted for the html.img to render it properly
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        return img

    def QR_upload_to_AWS(self, QR, name):
        #uploading a saved QR to an AWS bucket
        #decrypt the url to allow human readable filename for convenience
        name = name.replace(" ", "_")
        fullname = f'assets/qrcodes/{name}.png'

        #the full bytestream string is massive but contains a few items that are useless, the below split grabs the useful bit
        content_type, content_string = QR.split(',')
        content_type, _ = content_type.split(';')
        _, content_type = content_type.split(':')
        _, file_type = content_type.split('/')
        #decoding the uploaded bytestring for AWS upload
        decoded = base64.b64decode(content_string)
        #for this cut down version there is an authentication issue unless the details are passed here manually
        s3 = boto3.client('s3', aws_access_key_id='AKIAR26M65JFFX2ODGML', aws_secret_access_key='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')
        #s3 = boto3.client('s3')
        s3.put_object(Bucket='horizon-prod', Key=fullname,
                      Body=decoded, ContentType='image/png')
        return f'https://s3-eu-west-1.amazonaws.com/horizon-prod/{name}'

    def make_qr_url(self, asset_id, report_type, enc):
        #The QR url is split into 3 parts to be read by the simpelrmovedata website
        aname = self.agency.lower()
        aname = aname.replace(" ", "_")
        #no need to move this to lowercase anymore
        bname = asset_id.replace(" ", "_")
        if report_type is None:
            report_type = 'demoform'
        cname = report_type.lower()
        cname = cname.replace(" ", "_")
        #simple string encryption on the middle part of the string that contains some more sensitve data
        if enc is True:
            bname = bname.encode('utf-8')
            bname = self.key.encrypt(bname)
            bname = bname.decode('utf-8')

        url = f'https://qr.simplermovedata.co.uk/{aname}/{bname}/{cname}'
        return url

    def create_QR_campaign(self, QR, name, desc, channels, size, report_type, style, icon, cstring, type1, link):
        #creating the database details to track that specific QR
        content, is_open, color = 'None', False, 'info'
        if name == 'abc':
            var = 'ABC'
            campaigncode = f'{name}^{self.org}^'
        else:
            var = 'NEW'
        if report_type == 'passthrough':
            var = self.create_code_id(self.agency, self.org, name, channels, link)
            campaigncode = f'{name}^{self.org}^-{var}'
        else:
            var = 'NEW'
            campaigncode = f'{name}^{self.org}^'
        # need to encrypt and tokenise
        qr_url = self.make_qr_url(campaigncode, report_type, True)
        # need to make the QRcode and save the image to AWS and retuen the filepath
        aws_loc = self.QR_upload_to_AWS(QR, name)
        # now save the completed QR campaign to AWS
        action = {
                'AGENCY': self.agency,
                'CAMPAIGN': name,
                'DESCRIPTION': desc,
                'CHANNEL': channels,
                'SIZE': size,
                'QRCODE': qr_url,
                'AWS_LOCATION': aws_loc,
                'START': datetime.datetime.now(),
                'RGB': cstring,
                'STYLE': type1,
                'ICON': icon,
                'CODE_ID': var,
                'ORG': self.org,
                'STATUS': 'live'
        }
        #check if already exists
        count = db.campaign_tracker.count_documents(
            {'AGENCY': self.agency, 'CAMPAIGN': name, 'ORG': self.org})

        #insert the new document into collection
        if count == 0:
            db.campaign_tracker.insert_one(action)
            content, is_open, color = 'New QR successfully created', True, 'success'
        else:
            content, is_open, color = 'This name already exists!', True, 'danger'
        #output to an dbc.alert
        return content, is_open, color

    def qr_dropdown(self):
        #assets for the campaign dropdown
        resp = dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id='QR-dropdown',
                                options=[{'label': s, 'value': s} for s in self.campaigns], value=self.campaigns[0],
                                ),
                        ], width=8),
                    ], justify='center')
                ]),
        ])
        return resp

    def QR_viewer_box(self, src, camp, desc, link):
        #asset for the QR image frame, including stats on number of times scanned and a button to visit the link
        card = dbc.Card([dbc.CardImg(src=src, top=False, style={
                                    'object-fit': 'scale-down', 'height': '20em', 'margin-top': '5px'}),
                         dbc.CardBody([
                             dbc.Row(dbc.Button(desc, size='sm', className='btn mb-2 mb-md-0 btn-outline-white btn-block',
                                                outline=True, style={'color': 'dark'}, href=link, external_link=True)),
                             dbc.Card([dbc.Row(html.Small('Activity:', style={
                                                         'color': 'white', 'text-align': 'center'}), className='g-3 justify-content-center align-center align-items-center'),
                                       dbc.Row(dcc.Loading(html.H6(self.QR_code_stats(camp), style={
                                                         'color': 'white', 'text-align': 'center'}), color='#FFFFFF'), className='g-3 justify-content-center align-center align-items-center'),
                                       ], color=self.brandColour)
                             ])
                         ])
        return card

    def QR_viewer_boxes(self, content):
        #quick function to sort the images into tiles of 3
        cols = []
        rows = []
        boxes = []
        for i in content:
            cols.append(dbc.Col(i))
            if len(cols) >= 3:
                rows.append(cols)
                cols = []
        rows.append(cols)
        cols = []
        for row in rows:
            boxes.append(dbc.Row(row))
        return boxes

    def QR_viewer(self, campaign):
        #function to combine the couple above, create boxes based on the number of QR's
        self.get_QR_assets(campaign)
        if len(self.URL) > 1:
            desc = list(self.description)
            links = list(self.link)
            content = []
            for n, i in enumerate(self.URL):
                content.append(self.QR_viewer_box(i, campaign, desc[n], links[n]))
        else:
            content = self.QR_viewer_box(self.URL, campaign, self.description, self.link)
            content = self.QR_viewer_boxes([content])
        if len(content) > 1:
            content = self.QR_viewer_boxes(content)
        return content

    def QR_links_preview(self, link, asset, custom):
        #populating the link preview box
        url = []
        preview = 'Loading...'
        if custom == 'QR-tab1':
            url = self.make_qr_url('abc', asset, True)
            if asset is None:
                asset = 'demoform (legacy)'
            preview = asset
        elif custom == 'QR-tab2':
            url = self.make_qr_url('abc', 'passthrough', True)
            preview = link
        return url, preview

    def QR_designer_btn_block(self):
        #assets for all the extra buttons hidden into collapsable items
        return dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button('Create New', id='QR-create-btn',
                                           style={'background-color': '#8d5fff',
                                                  'color': '#ffffff'}, size='md'),
                                dbc.Button('QR Icons', id='QR-icon-btn',
                                           style={'background-color': '#8d5fff',
                                                  'color': '#ffffff'}, size='md'),
                                dbc.Button('Asset Gallery', id='QR-asset-btn',
                                           style={'background-color': '#8d5fff',
                                                  'color': '#ffffff'}, size='md')
                                ], className='flex-wrap w-100 mt-auto mb-1', style={'padding-top': '3em'})
                        ]),
                    ], justify='center', class_name='container'),
                    dbc.Row([
                        dbc.Col(
                            dbc.Collapse(self.QR_designer(), id='QR-create-collapse', is_open=True)
                        )
                    ], justify='center', class_name='container'),
                    dbc.Row([
                        dbc.Col(
                            dbc.Collapse(self.Qr_icons_gallery(), id='QR-icon-collapse', is_open=False)
                        )
                    ], justify='center', class_name='container'),
                    dbc.Row([
                        dbc.Col(
                            dbc.Collapse(self.QR_asset_viewer(), id='QR-asset-collapse', is_open=False)
                        )
                    ], justify='center', class_name='container')
                ])

    def QR_icon_boxes(self, src, desc):
        #assets for the center icons
        return dbc.Card([dbc.CardImg(src=src, top=False, style={
                                    'object-fit': 'scale-down', 'height': '5em', 'margin-top': '5px'}),
                        dbc.CardBody(html.H6(desc))])

    def QR_icon_builder(self):
        #check for set and custom assets
        QR, icons = self.get_qr_icons()
        content = []
        for i, r in QR.iterrows():
            print(r['ASSET_URL'])
            try:
                encoded_image = base64.b64encode(open(f"./assets/{r['ASSET_URL']}", 'rb').read())
            except FileNotFoundError:
                pass
            try:
                encoded_image = f'data:image/png;base64,{encoded_image.decode()}'
                box = self.QR_icon_boxes(encoded_image, r['DESCRIPTION'])
                content.append(box)
            except AttributeError:
                pass
        content = self.QR_viewer_boxes(content)
        return content

    def Qr_icons_gallery(self):
        #assets for the icon gallery and upload suite
        content = [dbc.Row(id='QR-icon-gallery'),
                   dbc.Row(dbc.InputGroup([
                       dcc.Upload([dbc.InputGroupText('Drag and Drop or Select File')],
                                  id='QR-icon-upload-drop'),
                       dbc.Input(
                           id='QR-icon-upload-name', placeholder='File Name'),
                       dbc.Button('Upload', id='QR-icon-upload-btn', style={
                           'background-color': '#8d5fff', 'color': '#ffffff'}, className='d-grid gap-2'),
                   ], className="mb-1")),
                   dbc.Row(dbc.Alert(style={'padding-left': '5px', 'margin-left': '5px'}, id='QR-icon-submit-alert',
                                     color='info', dismissable=True, is_open=False))]
        return content

    def QR_designer(self):
        #the assets for the QR designer suite
        QR, icons = self.get_qr_icons()
        content = dbc.Row([
                    dbc.Col(
                        dbc.Card([
                            dbc.Row(dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Name"),
                                    dbc.Input(id='QR-camp-name', type="text",
                                              placeholder="My new campaign"),
                                ],
                                class_name="mb-3",
                            )),
                            dbc.Row(dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Description"),
                                    dbc.Textarea(id='QR-camp-desc',
                                                 placeholder="Enter a description"),
                                ],
                                class_name="mb-3",
                            )),
                            dbc.Row([
                                dbc.InputGroup([
                                    dbc.InputGroupText(
                                        "Background Colour"),
                                    dbc.Input(
                                        type="color",
                                        id="QR-colorpickerBack",
                                        value='#FFFFFF',
                                        style={"width": 75, "height": 50}),
                                        ], className="mb-3"),
                                dbc.InputGroup([
                                    dbc.InputGroupText(
                                        "Top Colour"),
                                    dbc.Input(
                                        type="color",
                                        id="QR-colorpicker1",
                                        value=self.brandColour,
                                        style={"width": 75, "height": 50}),
                                        ], className="mb-3"),
                                dbc.InputGroup([
                                    dbc.InputGroupText(
                                        "Bottom Colour"),
                                    dbc.Input(
                                        type="color",
                                        id="QR-colorpicker2",
                                        value='#FFFFFF',
                                        style={"width": 75, "height": 50}),
                                        ], className="mb-3"),
                                dbc.InputGroup([
                                    dbc.InputGroupText('Style'),
                                    dbc.Select(id="QR-style-dd",
                                               options=[
                                                {"label": "Single colour",
                                                    "value": 'Single_colour'},
                                                {"label": "Gradient down",
                                                    "value": 'Gradient_down'},
                                                {"label": "Gradient across",
                                                    "value": 'Gradient_across'},
                                                {"label": "Gradient center",
                                                    "value": 'Gradient_center'},
                                                # {"label": "Template",
                                                #     "value": 'template'},
                                                   ],
                                               value='Single_colour'
                                               ),
                                    ], class_name="mb-3"),
                                dbc.InputGroup([
                                    dbc.InputGroupText('Center Icon'),
                                    dbc.Select(id="QR-icon-dd",
                                               options=[{'label': s, 'value': s} for s in icons],
                                               value=icons[0]
                                               ),
                                    ], class_name="mb-3"),
                            ]),
                            dbc.Tabs([
                                dbc.Tab([
                                    dbc.InputGroup([
                                        dbc.InputGroupText(
                                            "Media Asset"),
                                        dbc.Select(id="QR-asset-dd",
                                                   options=[{'label': v['Title'], 'value': v['Link']}
                                                            for v in self.asset_dictionary if v['report'] in self.QR_asset_gallery()],
                                                   value='welcomeform',
                                                   ),
                                    ], class_name="mb-3"),
                                ], label="Premium", tab_id="QR-tab1", tab_style={'margin-left': 'auto', 'margin-right': 'auto'}, disabled=False),
                                dbc.Tab(dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("link"),
                                        dbc.Input(id='QR-link-test', type="text", value=self.homepage,
                                                  placeholder="Type a custom link here"),
                                    ],
                                    class_name="mb-3",
                                ), label="Custom", tab_id="QR-tab2", tab_style={'margin-left': 'auto', 'margin-right': 'auto'}, disabled=False),
                            ], id="QR-asset-tabs", active_tab="QR-tab1", style={'text-align': 'center'}),
                            dbc.Row(
                                dbc.Button("SAVE", id='QR-btn-save', n_clicks=0,
                                           style={'background-color': '#8d5fff',
                                                  'color': '#ffffff'},
                                           size='md', className='d-grid gap-*')
                            )
                        ]), width=4),
                    dbc.Col([
                        dbc.Row([
                            dbc.Card([
                                    dbc.CardHeader([html.H1('QR Preview', style={
                                                        'margin-left': '10px', 'margin-right': '10px', 'text-align': 'center', 'color': '#8d5fff'}, className="card-title"),
                                                    html.Br(),
                                                    html.H5('This is a preview only and will be lost unless saved', style={
                                                                        'margin-left': '10px', 'margin-right': '10px', 'text-align': 'center', 'color': '#8d5fff'}, className="card-title"),
                                                    html.Br(),
                                                    dcc.Dropdown(id='QR-template-dd', options=[{'label': s, 'value': s}
                                                                 for s in self.campaigns], value=self.campaigns[0]),
                                                    #html.Br(),
                                                    dbc.Badge("Copy QR style", id='QR-btn-template', n_clicks=0,
                                                              style={'color': '#8d5fff'},
                                                              pill=True, className='mb-3 mt-1')
                                                    ]),
                                    dbc.CardBody(dcc.Loading(html.Img(id='QR-preview-img', style={'max-height': '20em'}), color='#8d5fff'))
                            ])
                        ]),
                        dbc.Row([
                            dbc.Card(
                                dbc.CardBody([
                                    dbc.Row(html.Small('Test Link:', style={
                                                                'color': 'white', 'text-align': 'center'}), className='g-3 justify-content-center align-center align-items-center'),
                                    dbc.Row(dcc.Loading(html.A(html.H6('www.Simplermovedata.co.uk', id='QR-test-link1', style={
                                                                'color': 'white', 'text-align': 'center'}), id='QR-test-link2', href='www.simplermovedata.co.uk', target="_blank"), color='#FFFFFF'), className='g-3 justify-content-center align-center align-items-center'),
                                    ]), color=self.brandColour, class_name='container'),
                        ]),
                        dbc.Row(dbc.Alert(style={'padding-left': '5px', 'margin-left': '5px'}, id='QR-submit-alert',
                                          color='info', dismissable=True, is_open=False))
                    ], width=8)
        ], class_name='container')
        return content

    def QR_asset_gallery(self):
        #checking what assets the agency and org already have
        df = db.media_vault
        df = pd.DataFrame(list(df.find()))
        drop_list = ['_id']
        df = df.drop(drop_list, axis=1)
        df = df[(df['AGENCY'] == self.agency) & (df['ORG'] == self.org)]
        media = []
        for i, r in df.iterrows():
            if r['MEDIA_TYPE'] in self.asset_checker:
                media.append(r['MEDIA_TYPE'])
        return media

    def QR_asset_box(self, img, name, desc, link):
        #assets for custom QR content gallery boxes
        card = dbc.Card([dbc.CardImg(src=img, top=False, style={
                                    'object-fit': 'cover', 'height': '7em', 'margin-top': '5px'}),
                         dbc.CardBody([
                             dbc.Row(dbc.Button(name, size='sm', className='btn mb-2 mb-md-0 btn-outline-white btn-block',
                                                outline=True, style={'color': 'dark'}, href=link, external_link=True)),
                            ]),
                         dbc.Row(html.P(
                                desc, style={'margin-left': '10px', 'margin-right': '10px', 'text-align': 'center'}))
                         ])
        return card

    def QR_asset_viewer(self):
        #function to assemble QR asset gallery boxes
        assets = self.QR_asset_gallery()
        content = []
        for i in self.asset_dictionary:
            if i['report'] in assets:
                content.append(self.QR_asset_box(i['img'], i['Title'], i['desc'], self.make_qr_url('abc', i['Link'], True)))
        content = self.QR_viewer_boxes(content)
        return content

    def QR_link_checker(self, link):
        #matches asset selection to current assets
        for i in self.asset_dictionary:
            if i['Link'] in link:
                return i['Link']


class Media_Upload_To_AWS():
    #simple file handler to pass images to AWS
    def __init__(self, agency, org):
        self.agency = agency
        self.org = org
        self.agent_photos_path = 'https://s3-eu-west-1.amazonaws.com/horizon-prod/assets/agentphotos'
        self.agent_photos_path_aws = 'assets/agentphotos'
        self.admin_path = 'assets'
        self.local_path = './assets/'

    def filename_maker(self, filename, path_type, file_type):
        #creates file paths depending on upload type
        if path_type == 'db':
            return f'{self.agent_photos_path}/{filename}.{file_type}'
        elif path_type == 'aws':
            return f'{self.agent_photos_path_aws}/{filename}.{file_type}'
        elif path_type == 'admin':
            return f'{self.admin_path}/{filename}.{file_type}'
        elif path_type == 'icon':
            return os.path.join("./assets/", f'{filename}')
        else:
            raise ValueError(f'{path_type} is not valid')

    def file_handler(self, file, filename, path_type):
        s3 = boto3.client('s3')
        #really ugly string formatting to grab file type and bytestring
        content_type, content_string = file.split(',')
        content_type, _ = content_type.split(';')
        _, content_type = content_type.split(':')
        _, file_type = content_type.split('/')
        #decoding the uploaded bytestring for AWS upload
        decoded = base64.b64decode(content_string)

        path = self.filename_maker(filename, path_type, file_type)
        if path_type == 'icon':
            image = Image.open(io.BytesIO(decoded))
            image.save(path, file_type)

        else:
            s3.put_object(Bucket='horizon-prod', Key=path,
                          Body=decoded, ContentType=content_type)
        return path, file_type

    def upload_photo_local_icon(self, file, filename, file_desc):
        #upload icon file locally
        if file is not None:
            path, file_type = self.file_handler(file, filename, 'icon')
            self.upload_photo_DB(filename, file_type, file_desc, True)
            return f'{filename} uploaded to app as {file_type}'
        else:
            raise ValueError(f'ERROR: File not found')

###
###
###
###
###
###
###
###
###
###
###
