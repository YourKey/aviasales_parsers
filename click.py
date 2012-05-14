# -*- coding: utf-8 -*-
#
# Набор методов для создания урлов для приземления.
#

__author__ = 'vit'

import boot

AVAILABLE_HOSTS = ["airasia.com","webjet.com","tigerairways.com","cebupacificair.com"]

PARAMS = {
    "webjet.com": {
        "url":"http://res.webjet.com/process.aspx",
        "params":"agentid=189&"
                 "flight_search_action=http%3A%2F%2Fres.webjet.com%2Fprocess.aspx&"
                 "WebSiteId=189&"
                 "TripType=rdbRoundTrip&"
                 "departure_label={origin_iata}&"
                 "txtDepCity1={origin_iata}&"
                 "txtdate1={depart_date}&" # %2F - delimiter
                 "arrival_label={destination_iata}&"
                 "txtArrCity1={destination_iata}&"
                 "txtdate2={return_date}&" # %2F - delimiter
                 "ddlCabin=Y&"
                 "ddlPaxADT={adults}&"
                 "ddlPaxCHD={children}&"
                 "ddlPaxINF={infants}&"
                 "txtArrCity2={origin_iata}&"
                 "txtDepCity2={destination_iata}&"
                 "EntryPoint=Flight&"
                 "RequestFrom=Outside&"
                 "btnSubmitAir=Search+for+flights"
    },
    "airasia.com": {
        "url":"http://booking.airasia.com/Compact.aspx",
        "params":"pageToken=&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$RadioButtonMarketStructure=RoundTrip&"
              "ControlGroupCompactView_AvailabilitySearchInputCompactVieworiginStation1=KBV&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$TextBoxMarketOrigin1=KBV&"
              "ControlGroupCompactView_AvailabilitySearchInputCompactViewdestinationStation1=MEL&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$TextBoxMarketDestination1=MEL&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketDay1=07&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketMonth1=2012-05&"
              "date_picker=05%2F14%2F2012&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketDay2=14&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketMonth2=2012-05&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListPassengerType_ADT=1&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListPassengerType_CHD=0&"
              "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListPassengerType_INFANT=0&"
              "ControlGroupCompactView$ButtonSubmit=Search&"
              "__EVENTTARGET=&"
              "__EVENTARGUMENT=&"
              "viewState=%2FwEPDwUBMGRktapVDbdzjtpmxtfJuRZPDMU9XYk%3D"
    },
    "tigerairways.com": {
        "url":"http://booking.tigerairways.com/MagnetSearch.aspx",
        "params":"__EVENTTARGET=ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24LinkButtonNewSearch&"
                 "__EVENTARGUMENT=&"
                 "__VIEWSTATE=%2FwEPDwUBMGRk7p3dDtvn3PMYYJ9u4RznKUiVx98%3D&"
                 "pageToken=&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24RadioButtonMarketStructure=RoundTrip&"
                 "originStation1=SIN&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24TextBoxMarketOrigin1=SIN&"
                 "destinationStation1=HKG&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24TextBoxMarketDestination1=HKG&"
                 "originStation2=&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24TextBoxMarketOrigin2=&"
                 "destinationStation2=&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24TextBoxMarketDestination2=&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListMarketDay1=12&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListMarketMonth1=2012-05&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListMarketDateRange1=1%7C1&"
                 "date_picker=2012-05-12&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListMarketDay2=19&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListMarketMonth2=2012-05&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListMarketDateRange2=1%7C1&"
                 "date_picker=2012-05-19&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListPassengerType_ADT=1&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListPassengerType_CHD=0&"
                 "ControlGroupMagnetSearchView%24AvailabilitySearchInputMagnetSearchView%24DropDownListPassengerType_INFANT=0&"
                 "ASP.NET_SessionIdb5dpla55xiloqzieu3e1kcaw"
    },
    "cebupacificair.com": {
        "url": "http://book.cebupacificair.com/Select.aspx",
        "params":"_tripType=RoundTrip&"
                 "ddOrigin=SIN&"
                 "ddDestination=PEK&"
                 "_depday=15&"
                 "_depmonthyear=2012-05&"
                 "departure=&"
                 "_retday=20&"
                 "_retmonthyear=2012-05&"
                 "return=&"
                 "_adults=1&"
                 "_children=0&"
                 "_infants=0&"
                 "x=46&"
                 "y=6&"
                 "__EVENTTARGET=ControlGroupSearchView%24AvailabilitySearchInputSearchView%24LinkButtonNewSearch&"
                 "__EVENTARGUMENT=&"
                 "__VIEWSTATE=%2FwEPDwUBMGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFPENvbnRyb2xHcm91cFNlbGVjdFZpZXckU3NyTWFya2V0SW5wdXRTZWxlY3RWaWV3JENoZWNrQm94U1NSc2QPfRwg3cwWfo1kb8/MACZsEO/o&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24RadioButtonMarketStructure=RoundTrip&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24TextBoxMarketOrigin1=SIN&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24TextBoxMarketDestination1=PEK&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListMarketDay1=15&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListMarketMonth1=2012-05&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListMarketDay2=20&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListMarketMonth2=2012-05&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListPassengerType_ADT=1&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListPassengerType_CHD=0&"
                 "ControlGroupSearchView%24AvailabilitySearchInputSearchView%24DropDownListPassengerType_INFANT=0&"
                 "viewState=%2FwEPDwUBMGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFPENvbnRyb2xHcm91cFNlbGVjdFZpZXckU3NyTWFya2V0SW5wdXRTZWxlY3RWaWV3JENoZWNrQm94U1NSc2QPfRwg3cwWfo1kb8/MACZsEO/o&"
                 "pageToken=G415X86jQkk=&"
                 "eventTarget=&"
                 "eventArgument="
    }
}

def url_params_from_string(str):
    d = dict()
    for v in str.split("&"):
        if len(v):
            pair = v.split("=")
            d[pair[0]] = pair[1]
    return d

def url_params_to_string(obj):
    str = ""
    for k in obj:
        str += ("&" if str else "") + k + "=" + obj[k]
    return str

def url_info(domain, obj):
    proposal = obj["proposal"]
    request = obj["request"]

    request = request.copy()

    request["depart_date"] = request["depart_date"].replace('-', "%2F")
    request["return_date"] = request["return_date"].replace('-', "%2F")

    print 'url_info ', obj
    if not PARAMS.has_key(domain):
        return False

    params = PARAMS[domain]["params"]
    if type(params) != str:
        params = url_params_to_string(params)

    for k in request:
        params = params.replace("{" + k + "}", request[k])

    params = url_params_from_string(params)

    return {
        "method":"get",
        "url": PARAMS[domain]["url"],
        "params": params
    }

def main():
    import urllib

    a = url_info("cebupacificair.com", {})
    r = []
    for k in a["params"].keys():
        r.append( k + '=' + urllib.quote(a["params"][k], '') )

    print a["url"] + '?' + '&'.join(r)

if __name__ == "__main__":
    main()
