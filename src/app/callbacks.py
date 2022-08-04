import dash
from dash import html
from dash.dependencies import Input, Output, State


def register_callbacks(dashapp):
    import pandas as pd
    from app_functions import QR_functions, connect_to_db, Media_Upload_To_AWS

    #NEW QR assets
    @dashapp.callback(
        Output('QR-agency-dd', 'options'),
        Output('QR-agency-dd', 'value'),
        Output('QR-org-dd', 'options'),
        Output('QR-org-dd', 'value'),
        Input('URL', 'pathname'))
    def QR_builder_temp_dropdowns(pathname):
        #build dropdown to simulate different users, this will be dropped for production
        db = connect_to_db()
        df = db.client_data
        df = pd.DataFrame(list(df.find()))
        drop_list = ['_id']
        df = df.drop(drop_list, axis=1)
        agencies = []
        orgs = []
        for i, r in df.iterrows():
            agencies.append(r['AGENCY'])
            orgs.append(r['ORG'])
        agencies = list(set(agencies))
        orgs = list(set(orgs))
        options1 = [{'label': s, 'value': s} for s in agencies]
        options2 = [{'label': s, 'value': s} for s in orgs]
        return options1, 'Smith Buck and Son', options2, 'Head Office'

    @dashapp.callback(
        Output('QR-header', 'children'),
        Output('QR-Div2', 'children'),
        Input('QR-btn', 'n_clicks'),
        State('QR-agency-dd', 'value'),
        State('QR-org-dd', 'value'))
    def QR_builder(n, agency, org):
        #builds out initial assets from library populating the dropdown assets and the button blocks with collapses
        QR = QR_functions(agency, org)
        dropdown = QR.qr_dropdown()
        btn = QR.QR_designer_btn_block()
        return dropdown, btn

    @dashapp.callback(
        Output('QR-Div1', 'children'),
        Input('QR-dropdown', 'value'),
        State('QR-agency-dd', 'value'),
        State('QR-org-dd', 'value'))
    def QR_image(opt, agency, org):
        #populate the QR image boxes from the QR dropdown
        QR = QR_functions(agency, org)
        content = QR.QR_viewer(opt)
        QR.QR_code_stats(opt)
        return content

    @dashapp.callback(
        Output("QR-icon-collapse", "is_open"),
        Output("QR-create-collapse", "is_open"),
        Output("QR-asset-collapse", "is_open"),
        [Input("QR-icon-btn", "n_clicks"),
         Input("QR-create-btn", "n_clicks"),
         Input("QR-asset-btn", "n_clicks")],
    )
    def QR_icons_collapse(n, n1, n2):
        #buttons to open single collapses and close others
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'QR-icon-btn' in changed_id:
            return True, False, False
        elif 'QR-create-btn' in changed_id:
            return False, True, False
        elif 'QR-asset-btn' in changed_id:
            return False, False, True
        else:
            return False, False, False

    @dashapp.callback(
        Output("QR-icon-gallery", "children"),
        Output("QR-icon-submit-alert", "children"),
        Output("QR-icon-submit-alert", "is_open"),
        Output("QR-icon-submit-alert", "color"),
        Input("QR-icon-upload-btn", "n_clicks"),
        State('QR-agency-dd', 'value'),
        State('QR-org-dd', 'value'),
        State('QR-icon-upload-drop', 'contents'),
        State('QR-icon-upload-drop', 'filename'),
        State('QR-icon-upload-name', 'value')
    )
    def QR_icons_builder(n, agency, org, file, filename, file_desc):
        #uploading new local icon and send results to an alert
        QR = QR_functions(agency, org)
        icons = QR.QR_icon_builder()
        content, is_open, color = 'Loading...', False, 'info'
        if n:
            if file is None:
                content, is_open, color = 'No file selected', True, 'danger'
            elif file_desc is None:
                content, is_open, color = 'You must provide a name', True, 'warning'
            else:
                photos = Media_Upload_To_AWS(agency, org)
                upload1 = photos.upload_photo_local_icon(file, filename, file_desc)
                content = [html.P(f'{upload1}'), html.Img(src=file)]
                is_open = True
                icons = QR.QR_icon_builder()
        return icons, content, is_open, color

    @dashapp.callback(
        Output('QR-colorpickerBack', 'value'),
        Output('QR-colorpicker1', 'value'),
        Output('QR-colorpicker2', 'value'),
        Output('QR-style-dd', 'value'),
        Output('QR-icon-dd', 'value'),
        Output('QR-asset-dd', 'value'),
        Output('QR-link-test', 'value'),
        Input('QR-btn-template', 'n_clicks'),
        State('QR-template-dd', 'value'),
        State('QR-agency-dd', 'value'),
        State('QR-org-dd', 'value'),
        )
    def QR_image_template(n, template, agency, org):
        #set defaults of the form inputs from a template
        QR = QR_functions(agency, org)
        icons, _ = QR.get_qr_icons()
        c1, c2, c3, type, icon, url, split = '#FFFFFF', QR.brandColour, '#FFFFFF', 'Single_colour', icons.iloc[
            0]['ASSET_URL'], 'www.simplermovedata.co.uk', ['marketreport']
        if n:
            c1, c2, c3, type, icon, url, split = QR.QR_template_results(template)
        split = QR.QR_link_checker(split)
        return c1, c2, c3, type, icon, split, url

    @dashapp.callback(
        Output('QR-preview-img', 'src'),
        Output('QR-test-link1', 'children'),
        Output('QR-test-link2', 'href'),
        Input('QR-colorpickerBack', 'value'),
        Input('QR-colorpicker1', 'value'),
        Input('QR-colorpicker2', 'value'),
        Input('QR-style-dd', 'value'),
        Input('QR-icon-dd', 'value'),
        Input('QR-link-test', 'value'),
        Input('QR-template-dd', 'value'),
        Input('QR-asset-dd', 'value'),
        State('QR-asset-tabs', 'active_tab'),
        State('QR-agency-dd', 'value'),
        State('QR-org-dd', 'value'),
        )
    def QR_image_preview(c1, c2, c3, type, icon, url, template, asset, custom, agency, org):
        #populate the preview image based on form inputs
        QR = QR_functions(agency, org)
        style, icon, _, _ = QR.style_qr(c1, c2, c3, type, icon)
        link, preview = QR.QR_links_preview(url, asset, custom)
        content = QR.Make_QR_preview(style, icon, link)
        return content, preview, link

    @dashapp.callback(
        Output('QR-submit-alert', 'children'),
        Output('QR-submit-alert', 'is_open'),
        Output('QR-submit-alert', 'color'),
        Input('QR-btn-save', 'n_clicks'),
        State('QR-preview-img', 'src'),
        State('QR-camp-name', 'value'),
        State('QR-camp-desc', 'value'),
        State('QR-colorpickerBack', 'value'),
        State('QR-colorpicker1', 'value'),
        State('QR-colorpicker2', 'value'),
        State('QR-style-dd', 'value'),
        State('QR-icon-dd', 'value'),
        State('QR-link-test', 'value'),
        State('QR-asset-dd', 'value'),
        State('QR-agency-dd', 'value'),
        State('QR-org-dd', 'value'),
        )
    def QR_create_new(n, img, name, desc, c1, c2, c3, type, icon, url, report_type, agency, org):
        #Create new QR assets and DB assets and save them to AWS and the mongoDB simultaneously
        content, is_open, color = 'None', False, 'info'
        if n:
            QR = QR_functions(agency, org)
            #size is there as a legacy function that will be used to create % data assuming we have data from a mailing list
            size = 1000
            style, icon, cstring, varient = QR.style_qr(c1, c2, c3, type, icon)
            content, is_open, color = QR.create_QR_campaign(img, name, desc, 'media', size, report_type, style, icon, cstring, varient, url)
        return content, is_open, color


######
