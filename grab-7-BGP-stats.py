'''The idea of the script is to parse LACNOG's mailing list
search for emails called "Weekly Routing Report IPv4"
and generate some BGP statistics for our region

March 2023
'''

#Variable declaration
import time
import sys
import random
from datetime import date
today = date.today()
from datetime import datetime
import requests
from bs4 import BeautifulSoup
## // VARIABLE DECLARATION ##//
startTime = datetime.now()
baseurl="https://mail.lacnic.net/pipermail/lacnog/"
mailinglisturl = 'https://mail.lacnic.net/pipermail/lacnog/'
HiloLINKs=[] #todos los links "Hilos" del pipermail/mailman de la lista LACNOG
TodosLinkConElEmail=[] #En esta lista se encuentran TODOS los link sobre Weekly Global IPv4 Routing Table Report
dictDetailInfo={}
start_LACNIC=0 #This variable will indicate in the email in which lines starts LACNIC info
end_LACNIC=0  #This variable will indicate in the email in which lines ends LACNIC info
i=0
a=[] #The webpage is store in this list
DESC="  <p><div> \
Las graficas inferiores son el resultado de la recoleccion de datos automaticas <br>\
de los emails enviados a LACNOG con el titulo Weekly Routing Report IPv4  \
</p></div><br>"

a.append(DESC)

def IMPRIMIRBONITO(a):
    import sys, os
    from mako.template import Template
    from mako.lookup import TemplateLookup
    mytemplate = Template(filename='index.mako',\
    input_encoding='utf-8',\
    default_filters=['decode.utf8'],\
    output_encoding='utf-8',\
    encoding_errors='replace')
    #b=('\n'.join(a),'utf-8')
    return mytemplate.render(Name=a)


def CREATEGRAPH(title,item,i,varchart,divid,a):
  myrandom=random.randint(1, 3) #Options for the graphs. Graph effect
  if myrandom==1:
      easing='out'
  if myrandom==2:
      easing='in'
  if myrandom==3:
      easing='inAndOut'

  a.append ("""\
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart); 
      function drawChart() { var data = google.visualization.arrayToDataTable ([ ['Fecha', '"""+item+ """ '], """)


  import collections
  for key in collections.OrderedDict(sorted(dictDetailInfo.items())): #ordenamos el dict para que el chart salga bien
    #print (key)
    for item in dictDetailInfo[key]:
      if item==TITLE:
        datetime_object = datetime.fromtimestamp(int(key.split(".")[0])).strftime('%Y,%m-1,%d') #timestamp a %Y,%m-1,%d (formato exigido por gogle)
        b = "["+"new Date("+str(datetime_object)+"),"+str(dictDetailInfo[key][item])+"],"+"\n"
        a.append(b)

  a.append("""\
        ]);

        var options = {
           curveType: 'function',      
           animation: {
             duration: 11500,
             easing: '""" + str(easing) + """',
             startup: true
           },

           title:

  """)


  b="'"+title+"'"  #This was needed because the title within the JavaScript needed '
  a.append (b)
  a.append("""\
        };
  """)
  a.append("")
  a.append(varchart)
  a.append("""
        chart.draw(data, options);
      }
    </script>
  """)

  a.append(divid)

  return a

def ObtainLinks(URL, TextToFind):
  #in this function we receive an URL and find every link where the a href matches TextToFind
  LINKs=[]
  # Hacemos la solicitud GET a la página web
  response = requests.get(URL)

  # Utilizamos BeautifulSoup para analizar el HTML de la página web
  soup = BeautifulSoup(response.content, 'html.parser')

  # Recorremos todos los enlaces de la página
  for link in soup.find_all('a'):

    # Si el enlace contiene la cadena 'Weekly Global IPv4 Routing Table Report'
    if TextToFind in link.text:

        # Imprimimos el enlace con el texto "Hilo"
        #print(baseurl+link.get('href'))
        a=baseurl+link.get('href')
        LINKs.append(str(a))
  return LINKs

def IdentifyOnlyLACNICSection(text_lines):
  #global start_LACNIC, end_LACNIC
  cnt=0
  for item in text_lines:
    cnt = cnt +1
    if "LACNIC Region Analysis Summary" in item:
      start_LACNIC=cnt #We know in the text in which line LACNIC's section starts

    if "AfriNIC Region Analysis Summary" in item:
      end_LACNIC=cnt -3 #We know in the text in which line LACNIC's section ends
      POSICIONES=[start_LACNIC,end_LACNIC]
      return POSICIONES
      break
def IdentifyRoutingInfo(text_lines,POSICIONES):
  #global start_LACNIC, end_LACNIC
  TMPDict={}
  for item in text_lines[POSICIONES[0]:POSICIONES[1]]: #Let's process only LACNIC's section
    if "Prefixes being announced by LACNIC Region ASes" in item:
        Prefixes_being_announced_by_LACNIC_Region_ASes=item.split(":")[1].strip()
        #print (Prefixes_being_announced_by_LACNIC_Region_ASes)
        TMPDict['Prefixes_being_announced_by_LACNIC_Region_ASes']=Prefixes_being_announced_by_LACNIC_Region_ASes

    if "LACNIC Region origin ASes present in the Internet Routing Table" in item:
        LACNIC_Region_origin_ASes_present_in_the_Internet_Routing_Table=item.split(":")[1].strip()
        #print (LACNIC_Region_origin_ASes_present_in_the_Internet_Routing_Table)
        TMPDict['LACNIC_Region_origin_ASes_present_in_the_Internet_Routing_Table']=LACNIC_Region_origin_ASes_present_in_the_Internet_Routing_Table

    if "LACNIC Region origin ASes announcing only one prefix" in item:
        LACNIC_Region_origin_ASes_announcing_only_one_prefix=item.split(":")[1].strip()
        #print (LACNIC_Region_origin_ASes_announcing_only_one_prefix)
        TMPDict['LACNIC_Region_origin_ASes_announcing_only_one_prefix']=LACNIC_Region_origin_ASes_announcing_only_one_prefix  

    if "LACNIC Region transit ASes present in the Internet Routing Table" in item:
        LACNIC_Region_transit_ASes_present_in_the_Internet_Routing_Table=item.split(":")[1].strip()
        #print (LACNIC_Region_transit_ASes_present_in_the_Internet_Routing_Table)
        TMPDict['LACNIC_Region_transit_ASes_present_in_the_Internet_Routing_Table']=LACNIC_Region_transit_ASes_present_in_the_Internet_Routing_Table

    if "Number of LACNIC addresses announced to Internet" in item:
        Number_of_LACNIC_addresses_announced_to_Internet=item.split(":")[1].strip()
        #print (Number_of_LACNIC_addresses_announced_to_Internet)
        TMPDict['Number_of_LACNIC_addresses_announced_to_Internet']=Number_of_LACNIC_addresses_announced_to_Internet

    if "LACNIC Deaggregation factor" in item:
        LACNIC_Deaggregation_factor=item.split(":")[1].strip()
        #print (LACNIC_Deaggregation_factor)
        TMPDict['LACNIC_Deaggregation_factor']=LACNIC_Deaggregation_factor

    if "LACNIC Prefixes per ASN" in item:
        LACNIC_Prefixes_per_ASN=item.split(":")[1].strip()
        #print (LACNIC_Prefixes_per_ASN)
        TMPDict['LACNIC_Prefixes_per_ASN']=LACNIC_Prefixes_per_ASN

  return TMPDict

text_lines=""
def GetURLandConvertTOtext(URL):
  #This function receives an URL and return the content of the URL but ONLY the text
  global text_lines
  import requests
  from bs4 import BeautifulSoup

  # Realizar solicitud GET
  response = requests.get(URL)

  # Analizar contenido HTML
  soup = BeautifulSoup(response.content, 'html.parser')

  # Obtener todas las líneas de texto
  text_lines = [line.strip() for line in soup.get_text().splitlines()]
  return text_lines

def FindDateOfEmail(text_lines):
  #We want to find the date the report was generated (not the date the email was received)
  #Example: https://mail.lacnic.net/pipermail/lacnog/2023-March/009427.html

  # Imprimir las líneas de texto
  #for line in text_lines:
  #  print(line)

  for item in text_lines:
    if "+10GMT" in item:
        #print("Se encontro el item:", item)

        TMP=item.split(",")[0]
        DIA=item.split(",")[0]
        MES=DIA.split(" ")[-1]
        from time import strptime
        MES=strptime(MES,'%b').tm_mon
        DIA=TMP.split(" ")[-2]
        ANO=item.split(",")[1].strip()
        if int(ANO) < 2017: return None#There is not much information before 2017

        FECHA=ANO+","+str(MES)+"-1, "+DIA
        FECHA=DIA+"/"+str(MES)+"/"+ANO
        import time
        import datetime


        FECHA=(time.mktime(datetime.datetime.strptime(FECHA,"%d/%m/%Y").timetuple())) #la fecha la colocamos en Timestamp porque luego necesitamos ordenar el Dict por fecha

        #print (FECHA)
        return str(FECHA) #La fecha es devuelta en Timestamp

if __name__ == "__main__":
  HiloLINKs=ObtainLinks(mailinglisturl, "Hilo")

  for link in HiloLINKs:
    #print (link)
    URLneededForFixing=(link.split("/")[-2])
    LinksNeededToBeFixed=ObtainLinks(link, "[lacnog] Weekly Global IPv4 Routing Table Report")
    for LINK in LinksNeededToBeFixed: #The links are relative links, need to fix few things
        LastPath="/"+LINK.split("/")[-1]
        FirstPart=LINK.rsplit("lacnog/")[0]
        NewURL=FirstPart+"lacnog/"+URLneededForFixing+LastPath
        TodosLinkConElEmail.append(NewURL)


  for link in HiloLINKs:
    #print (link)
    URLneededForFixing=(link.split("/")[-2])
    LinksNeededToBeFixed=ObtainLinks(link, "[lacnog] Weekly Routing Table Report")
    for LINK in LinksNeededToBeFixed: #The links are relative links, need to fix few things
        LastPath="/"+LINK.split("/")[-1]
        FirstPart=LINK.rsplit("lacnog/")[0]
        NewURL=FirstPart+"lacnog/"+URLneededForFixing+LastPath
        TodosLinkConElEmail.append(NewURL)

  #print (start_LACNIC, end_LACNIC)
  try:
    for link in TodosLinkConElEmail: #Vamos a recorrer todos los links que tienen el correo
      TextPage=GetURLandConvertTOtext(link)  #Nos interesa solo el texto, no el html
      FECHA=FindDateOfEmail(TextPage) #Revisamos la fecha 
      #IdentifyRoutingInfo(text_lines,dictDetailInfo, FECHA)
      if FECHA: #Solo por si acaso, si no obtenemos fecha no procesamos. Un basic sanity check
        POSICIONES=IdentifyOnlyLACNICSection(text_lines) #Disculpen que este aqui, pero no sirvio en otro sitio :-)
        dictDetailInfo[FECHA]=IdentifyRoutingInfo(text_lines,POSICIONES)
  except Exception:
    pass

  #print(dictDetailInfo)
#  for key in dictDetailInfo:
#    print (key)
#    for item in dictDetailInfo[key]:
#        print ("   ",key,item,dictDetailInfo[key][item])


  TITLE = "Prefixes_being_announced_by_LACNIC_Region_ASes"
  item = "Number of Prefixes"
  i=1
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)

  TITLE = "LACNIC_Region_origin_ASes_present_in_the_Internet_Routing_Table"
  item = "Origin ASs"
  i=2
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)

  TITLE = "LACNIC_Region_origin_ASes_announcing_only_one_prefix"
  item = "ASs originating one Prefix"
  i=3
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)

  TITLE = "LACNIC_Region_transit_ASes_present_in_the_Internet_Routing_Table"
  item = "Transit ASs ASs"
  i=4
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)

  TITLE = "Number_of_LACNIC_addresses_announced_to_Internet"
  item = "Number of IPv4 addresses"
  i=5
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)

  TITLE = "LACNIC_Deaggregation_factor"
  item = "Deaggregation factor"
  i=6
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)

  TITLE = "LACNIC_Prefixes_per_ASN"
  item = "Prefixes per ASN"
  i=7
  varchart="var chart = new google.visualization.LineChart(document.getElementById('chart_div"+str(i)+"'));"
  divid="<div style='width:85%' id=chart_div"+str(i)+"></div>\n"
  CREATEGRAPH(TITLE,item,i,varchart,divid,a)


#"<br>Script execution time:",datetime.now()-startTime 
#"<br>Last updated:",time.strftime("%H:%M:%S"), time.strftime("%d/%B/%Y")
a.append('''
<font size=-1>
<br><br>Stats based on: Weekly Routing Report IPv4 in LACNOG mailing list
https://mail.lacnic.net/pipermail/lacnog/ by Philip Smith
<br>Opendata for this stats: <a href=/BGP/opendata/ParserWeeklyBGPUpdate.json>
/BGP/opendata/ParserWeeklyBGPUpdate.json </a>
<br>Script execution time: '''+ str(datetime.now()-startTime) + '''
<br>Page generated by: '''+ sys.argv[0] + '''
<br>Last updated: '''+time.strftime("%d/%b/%Y %H:%M:%S")+'''

</body></html>
''')

print ((IMPRIMIRBONITO(a)).decode('UTF-8'))
  
