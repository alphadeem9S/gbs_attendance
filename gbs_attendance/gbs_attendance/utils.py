import frappe 
from shapely.geometry import Point, Polygon
from decimal import Decimal
import json



@frappe.whitelist()
def install_employee_check_in():
    print("+asd")
    #install_client_script()

def install_client_script():
    doc = frappe.new_doc("Client Script")
    doc.dt      = "Employee Checkin"
    doc.enabled = 1
    doc.script  = """
        frappe.ui.form.on('Employee Checkin', {
            validate:(frm)=>{
            frappe.call({
                "method":"gbs_attendance.gbs_attendance.utils.validate_check_in_form",
                args:{
                    "doc":frm.doc
                },callback(r){
                    if(r.message==false){
                        console
                        //frappe.throw("Restricted Area")
                        frappe.msgprint("Restricted Area")
                        frappe.validated = false;
                    }
                }
            })  
            },

            map: function(frm){
            console.log(frm.doc.map);
            let mapdata = JSON.parse(cur_frm.doc.map).features[0];
            if(mapdata && mapdata.geometry.type=='Point'){
            let lat = mapdata.geometry.coordinates[1];
            let lon = mapdata.geometry.coordinates[0];
        // make an api call 

            frappe.call({
            type: "GET",
            url: `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`,
            callback: function(r) {
                frm.set_value('address', r.display_name);
        }

        })
        }
        } // END MAP 

        });

        frappe.ui.form.on('Employee Checkin', {
            onload(frm) {
                
                function onPositionRecieved(position){
                    var longitude= position.coords.longitude;
                    var latitude= position.coords.latitude;
                    frm.set_value('longitude',longitude);
                    frm.set_value('latitude',latitude);
                    console.log(longitude);
                    console.log(latitude);
                    fetch('https://api.opencagedata.com/geocode/v1/json?q='+latitude+'+'+longitude+'&key=de1bf3be66b546b89645e500ec3a3a28')
                    .then(response => response.json())
                    .then(data => {
                        var city=data['results'][0].components.city;
                        var state=data['results'][0].components.state;
                        var area=data['results'][0].components.residential;
                        frm.set_value('city',city);
                        frm.set_value('state',state);
                        frm.set_value('area',area);
                        console.log(data);
                    })
                    .catch(err => console.log(err));
                    frm.set_df_property('my_location','options','<div class="mapouter"><div class="gmap_canvas"><iframe width=100% height="300" id="gmap_canvas" src="https://maps.google.com/maps?q='+latitude+','+longitude+'&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe><a href="https://yt2.org/youtube-to-mp3-ALeKk00qEW0sxByTDSpzaRvl8WxdMAeMytQ1611842368056QMMlSYKLwAsWUsAfLipqwCA2ahUKEwiikKDe5L7uAhVFCuwKHUuFBoYQ8tMDegUAQCSAQCYAQCqAQdnd3Mtd2l6"></a><br><style>.mapouter{position:relative;text-align:right;height:300px;width:100%;}</style><style>.gmap_canvas {overflow:hidden;background:none!important;height:300px;width:100%;}</style></div></div>');
                    frm.refresh_field('my_location');
                }
                
                function locationNotRecieved(positionError){
                    console.log(positionError);
                }
                
                if(frm.doc.longitude && frm.doc.latitude){
                    frm.set_df_property('my_location','options','<div class="mapouter"><div class="gmap_canvas"><iframe width=100% height="300" id="gmap_canvas" src="https://maps.google.com/maps?q='+frm.doc.latitude+','+frm.doc.longitude+'&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe><a href="https://yt2.org/youtube-to-mp3-ALeKk00qEW0sxByTDSpzaRvl8WxdMAeMytQ1611842368056QMMlSYKLwAsWUsAfLipqwCA2ahUKEwiikKDe5L7uAhVFCuwKHUuFBoYQ8tMDegUAQCSAQCYAQCqAQdnd3Mtd2l6"></a><br><style>.mapouter{position:relative;text-align:right;height:300px;width:100%;}</style><style>.gmap_canvas {overflow:hidden;background:none!important;height:300px;width:100%;}</style></div></div>');
                    frm.refresh_field('my_location');
                } else {
                    if(navigator.geolocation){
                        navigator.geolocation.getCurrentPosition(onPositionRecieved,locationNotRecieved,{ enableHighAccuracy: true});
                    }
                }
            }
        })

    """
    doc.save()


def validate_check_in(doc,*args,**Kwargs):
    try :
        p1 = Point(Decimal(doc.latitude or 0), Decimal(doc.longitude or 0))
        employee = frappe.get_doc("Employee",doc.employee)
        if employee.no_ceckin_restriction:
            pass
        coords = [
            (float(employee.p1_lat or 0) , float(employee.p1_lng or 0)),
            (float(employee.p2_lat or 0), float(employee.p2_lng or 0)),
            (float(employee.p3_lat or 0), float(employee.p3_lng or 0)),
            (float(employee.p4_lat or 0), float(employee.p4_lng or 0))]


        poly = Polygon(coords)

        res = p1.within(poly)
        if res:
            #frappe.throw("Restricted area")
            return True
        else:
            return False
    except Exception as ex:
        error_log = frappe.new_doc("Error Log")
        error_log.error = str(ex)
        error_log.save(ignore_permissions=True)
        pass


@frappe.whitelist()
def validate_check_in_form(doc,*args,**Kwargs):
    doc = json.loads(doc)
    try :
        p1 = Point(Decimal(doc.get("latitude") or 0), Decimal(doc.get("longitude") or 0))
        employee = frappe.get_doc("Employee",doc.get("employee"))
        # if employee.no_ceckin_restriction:
        #     return True

        #p2 = Point(24.895, 60.05)
        # p1_lat,p1_lng,p2_lat,p2_lng,p3_lat,p3_lng,p4_lat,p4_lng 
        # Create a square
        coords = [
            (float(employee.p1_lat or 0) , float(employee.p1_lng or 0)),
            (float(employee.p2_lat or 0), float(employee.p2_lng or 0)),
            (float(employee.p3_lat or 0), float(employee.p3_lng or 0)),
            (float(employee.p4_lat or 0), float(employee.p4_lng or 0))]
        poly = Polygon(coords)
    
        error_log = frappe.new_doc("Error Log")
        error_log.error =str(coords) + str(p1)
        error_log.save(ignore_permissions=1)
        res = p1.within(poly)

        
        if res:
            #frappe.throw("Restricted area")
            return True
        else:
            return False
    except Exception as ex:
        error_log = frappe.new_doc("Error Log")
        error_log.error = str(ex) + str(doc)
        error_log.save(ignore_permissions=True)
        return False
